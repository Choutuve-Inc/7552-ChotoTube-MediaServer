''' Tuve problemas con los testing, que no me reconocia lod modulos a pesar 
se que la aplicacion coprria bien, para poder hacer los test para la entrega puse todo en un solo archivo.  '''

import os
import sys
from flask import Flask, jsonify, request, json, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
from flask_cors import CORS
from durable.lang import *
from sqlalchemy import or_, func, desc

###Config de base de datos ####
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#### APP ##########
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
CORS(app)

port = int(os.environ.get("PORT", 5000))

#### JSON encoder #######3

class AlchemyEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o.__class__, DeclarativeMeta):
			data = {}
			fields = o.__json__() if hasattr(o, '__json__') else dir(o)
			for field in [f for f in fields if not f.startswith('_') and f not in ['metadata', 'query', 'query_class']]:
				value = o.__getattribute__(field)
				try:
					json.dumps(value)
					data[field] = value
				except TypeError:
					data[field] = None
			return data
		return json.JSONEncoder.default(self, o)

app.json_encoder = AlchemyEncoder


#### Tablas de base de datos ########


class Video(db.Model):
	__tablename__ = "videos"

	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(256),nullable=False)
	title = db.Column(db.String(256),nullable=False)
	size = db.Column(db.Float)
	date = db.Column(db.String(10), nullable=False)
	url =db.Column(db.String(256),nullable=False)
	thumbnail = db.Column(db.String(256),nullable=False)
	description =  db.Column(db.String(1024))
	private = db.Column(db.Boolean,nullable=False)
	weight = db.Column(db.Float,default=0)
	
	like = relationship("Like", cascade="all, delete-orphan")
	comments = relationship("Comment", cascade="all, delete-orphan")

	def __repr__(self):
		return '<Video %r>' % self.title

class Like(db.Model):
	__tablename__="like"

	id = db.Column(db.Integer, primary_key=True)
	video_id = db.Column(db.Integer,db.ForeignKey('videos.id'),nullable=False)
	user =  db.Column(db.String(256),nullable=False)
	value = db.Column(db.Boolean, nullable=False) #Like es true, dislike es false
	__table_args__ = (db.UniqueConstraint('video_id','user'),)


class Comment(db.Model):
	__tablename__ = "comment"

	id = db.Column(db.Integer, primary_key=True)
	video_id = db.Column(db.Integer,db.ForeignKey('videos.id'),nullable=False)
	user = db.Column(db.String(256),nullable=False)
	text = db.Column(db.String(1024 ), nullable=False)
	#__table_args__ = (db.UniqueConstraint('video_id','user'),)


####### RUTAS #########
@app.route("/")
def hello_world():
	return jsonify(hello="world")

@app.route("/videos",methods=['GET','POST', 'DELETE'])
@app.route("/videos/<int:id>",methods=['GET', 'DELETE'])
def videos(id=None):
	if request.method == 'POST':
		app.logger.info("Post video")
		content = request.json
		return createVideo(content)
	elif request.method == 'GET':
		if id is not None:
			app.logger.info("Get video by id")
			return getVideoById(id)
		else:
			app.logger.info("Token verification for feed")
			token = request.headers.get('token')
			body = {
				"JWT": token
			}
			headers = {"Content-Type": 'application/json'}
			data = json.dumps(body)
			userType = requests.post("https://serene-shelf-10674.herokuapp.com/token",headers=headers, data=data)
			if userType.status_code == 200:
				if userType.text[1:6] == "admin":
					app.logger.info("Get all videos admin side")
					videos = getVideos()
					return videos
				else:
					app.logger.info("Get all videos client side")
					content = request.json
					friendList = request.args.get('friendList').split(",")
					return getAllVideos(friendList)
			else:
				app.logger.error('Invalid Token')
				return Response(status=400)
	elif request.method == 'DELETE':
		if id is not None:
			app.logger.info("Delete video")
			return deleteVideo(id)
		else:
			app.logger.error('Invalid video id')
			return Response(status=404)
	return

@app.route("/videos/<int:id>/likes",methods=['GET','POST'])
def likes(id=None):
	if (id is None):
		app.logger.error('Invalid video id')
		return Response(status=404)
	if request.method == 'POST':
		app.logger.info("Post like on a video")
		content = request.json
		return likeVideo(id,content)
	if request.method == 'GET':
		app.logger.info("Get like dislike ratio of a video")
		return getLikes(id)

@app.route("/videos/<int:id>/comments",methods=['POST','GET'])
def comments(id=None):
	if (id is None):
		app.logger.error('Invalid video id')
		return Response(status=404)
	if request.method == 'POST':
		app.logger.info("Post a comment on a video")
		content = request.json
		return postComment(id,content)
	if request.method == 'GET':
		app.logger.info("Get all the comments of a video")
		return getComments(id)

@app.route("/videos/user/<id>")
def getUSerVideos(id=None):
	if (id is None):
		app.logger.error('Invalid user id')
		return Response(status=404)
	app.logger.info("Get all videos of a user")
	return getUserVideo(id)

@app.route("/ping")
def ping():
	return("Hello")

@app.route("/metrics/users/activity")
def userActivity():
	app.logger.info("Get all user activity in the platform")
	return getUsersActivity()

@app.route("/metrics/users/comments")
def userActivityComments():
	app.logger.info("Get the amaunto of comments made by video")
	return userActivityComments()

@app.route("/metrics/videos/likes")
def videosMostLiked():
	app.logger.info("Get most liked videos")
	return videosMostLiked()

@app.route("/metrics/videos/dislikes")
def videosMostDisliked():
	app.logger.info("Get most disliked videos")
	return videosMostDisliked()

@app.route("/metrics/videos/comments")
def videosMostCommented():
	app.logger.info("Get most commented videos")
	return videosMostCommented()

@app.route("/metrics/videos/day")
def getVideosPerDay():
	app.logger.info("Get the amaunt of videos posted per day")
	return getVideosPerDay()


########### SERVICE ###############
def createVideo(content):
	try:
		app.logger.info(content)
		title = content['title']
		size = content['size']
		url = content['url']
		user = content['user']
		thumbnail = content['thumbnail']
		date = content['date']
		description = content['description']
		private = content['private']
		video = Video(title=title,size=size,url=url,user=user,thumbnail=thumbnail,date=date,description=description,private=private)
		db.session.add(video)
		db.session.commit()
		return Response(status=200)
	except Exception as e:
		app.logger.error("Problem with parameter: ")
		app.logger.error(e)
		return Response(status=400)

def getVideoById(id):
	video = Video.query.filter_by(id=id).first()
	if video is None:
		app.logger.error('No video found with that id')
		return Response(status=404)
	return jsonify(video)

def getAllVideos(friendList):
	videos = Video.query.filter((Video.private==False) | (or_(*[Video.user.like(freind) for freind in friendList]))).all()
	videosJson = jsonify(videos).json
	update_state('ranking', { 'event': 'cantVideos', 'videos':videosJson})
	return jsonify(get_state('ranking')['videos'])

def getVideos():
	videos = Video.query.all()
	videosJson = jsonify(videos).json
	update_state('ranking', { 'event': 'cantVideos', 'videos':videosJson})
	return jsonify(get_state('ranking')['videos'])
	#return jsonify(videos=videos)

def deleteVideo(id):
	video = Video.query.filter_by(id=id).first()
	if video is not None:
		db.session.delete(video)
		db.session.commit()
		return Response(status=200)
	else:
		app.logger.error('No video found with that id')
		return Response(status=404)

def likeVideo(video_id,content):
	video = Video.query.filter_by(id=video_id).first()
	if video is None:
		app.logger.error('No video found with that id')
		return Response(status=404)
	try:
		user = content['user']
		value = content['value']
		query = Like.query.filter_by(video_id=video_id,user=user).first()
		if query is None:
			like = Like(video_id=video_id,user=user,value=value)
			db.session.add(like)
		else:
			if query.value == value:
				db.session.delete(query)
			else:
				query.value = not query.value
		db.session.commit()
		return Response(status=200)
	except Exception as e:
		app.logger.error(e)
		return Response(status=400)

def postComment(video_id,content):
	video = Video.query.filter_by(id=video_id).first()
	if video is None:
		app.logger.error('No video found with that id')
		return Response(status=404)
	try:
		user = content['user']
		text = content['text']
		comment = Comment(video_id=video_id,user=user,text=text)
		db.session.add(comment)
		db.session.commit()
		return Response(status=200)
	except Exception as e:
		app.logger.error(e)
		return Response(status=400)

def getLikes(id):
	video = Video.query.filter_by(id=id).first()
	if video is None:
		app.logger.error('No video found with that id')
		return Response(status=404)
	cantidad_de_likes = Like.query.filter_by(video_id=id,value=True).count()
	cantidad_de_dislikes = Like.query.filter_by(video_id=id,value=False).count()
	likes = {
		'likes': cantidad_de_likes,
		'dislike': cantidad_de_dislikes
	}
	return jsonify(reactions=likes)

def getComments(id):
	video = Video.query.filter_by(id=id).first()
	if video is None:
		app.logger.error('No video found with that id')
		return Response(status=404)
	comment = Comment.query.filter_by(video_id=id).all()
	return jsonify(comments=comment)

def getUsersActivity():
	activity = db.session.query(Video.user,func.count(Video.user)).group_by(Video.user)\
	.order_by((desc(func.count(Video.user)))).all()
	userActivity = []
	for item in activity:
		data ={'user': item[0], 'activity':item[1]}
		userActivity.append(data)
	return jsonify(userActivity)

def videosMostLiked():
	mostLiked = db.session.query(Video.title,func.count(Like.video_id))\
	.join(Video).filter(Like.value==True).group_by(Like.video_id,Video.title)\
	.order_by((desc(func.count(Like.video_id)))).all()
	liked = []
	for video in mostLiked:
		item = {"title": video[0], 'likes':video[1]}
		liked.append(item)
	app.logger.debug(liked)
	return jsonify(liked)

def videosMostDisliked():
	mostDisliked = db.session.query(Video.title,func.count(Like.video_id))\
	.join(Video).filter(Like.value==False).group_by(Like.video_id,Video.title)\
	.order_by((desc(func.count(Like.video_id)))).all()
	disliked = []
	for video in mostDisliked:
		item = {'title':video[0],'dislikes':video[1]}
		disliked.append(item)
	return jsonify(disliked)

def videosMostCommented():
	mostComented = db.session.query(Video.title,func.count(Comment.video_id))\
	.join(Video).group_by(Comment.video_id,Video.title)\
	.order_by((desc(func.count(Comment.video_id)))).all()
	comented = []
	for item in mostComented:
		data = {'title':item[0],'cantComments':item[1]}
		comented.append(data)
	return jsonify(comented)

def userActivityComments():
	activity = db.session.query(Comment.user,func.count(Comment.user)).group_by(Comment.user)\
	.order_by((desc(func.count(Comment.user)))).all()
	comentActivity = []
	for item in activity:
		data = {'user':item[0],'cantComments':item[1]}
		comentActivity.append(data)
	return jsonify(comentActivity)

def getUserVideo(id):
	videos = Video.query.filter(Video.user==id).all()
	return jsonify(videos)

def getVideosPerDay():
	videos = db.session.query(Video.date,func.count(Video.id)).group_by(Video.date).all()
	videosPerDay = []
	for item in videos:
		data = {'date':item[0],'cant':item[1]}
		videosPerDay.append(data)
	return jsonify(videosPerDay)




########### RULES ##############

COEFICIENTS = {
	'ATIVITY': 2,
	'REACTIONS': 5,
	'COMMENTS':1,
	'DATE_NEW':0.5,
	'DATE_OLD':2
}

with ruleset('ranking'):
	# antecedent
	@when_all(s.event == 'cantVideos')
	def activity(c):
		# consequent
		app.logger.debug("Se cuenta la actividad de los usuarios")
		for video in c.s.videos:
			cantVideos = Video.query.filter(Video.user.like(video['user'])).count()
			video['weight'] += COEFICIENTS['ATIVITY']*(cantVideos)
		c.s.event = 'reactions'

	@when_all(s.event == 'reactions')
	def countReaction(c):
		app.logger.debug("Se cuenta los likes del video")
		for video in c.s.videos:
			likes = len(list(filter(lambda x: x['value']==True,video['like'])))
			disLikes = len(list(filter(lambda x: x['value']==False,video['like'])))
			video['weight'] += 5*(likes - disLikes)
		c.s.event = 'comments'

	@when_all(s.event == 'comments')
	def countComments(c):
		app.logger.debug("Se cuentan los comentarios")
		for video in c.s.videos:
			comments = len(video['comments'])
			video['weight'] += (comments)
		c.s.event = 'date'

	@when_all(s.event == 'date')
	def divideByDate(c):
		app.logger.debug("Se toma en cuenta la fecha del video")
		today = datetime.now()
		for video in c.s.videos:
			videoDate = datetime.strptime(video['date'],'%Y-%m-%d')
			diference = abs((today - videoDate).days) + 1
			if (diference < 5):
				video['weight'] = video['weight']/(COEFICIENTS['DATE_NEW']*diference)
			else:
				video['weight'] = video['weight']/(COEFICIENTS['DATE_OLD']*diference)
		c.s.event = 'sort'


	@when_all(s.event == 'sort')
	def order(c):
		app.logger.debug("Se hace el sort de videos")
		c.s.videos = sorted(c.s.videos,key=lambda x:x['weight'],reverse=True)
		c.s.event = 'end'



######## MAIN ######################

if __name__=='__main__':
	#db.drop_all()
	#db.create_all()
	#db.session.commit()
	app.run(debug=True,host='0.0.0.0',port=port)
