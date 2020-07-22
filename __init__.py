import os
import sys
from flask import Flask, jsonify, request, json, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from config.encoder import AlchemyEncoder
import service.video_service as video
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object("config.config.Config")
db = SQLAlchemy(app)
CORS(app)

port = int(os.environ.get("PORT", 5000))

app.json_encoder = AlchemyEncoder

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

@app.route("/")
def hello_world():
	return jsonify(hello="world")

@app.route("/videos",methods=['GET','POST', 'DELETE'])
@app.route("/videos/<int:id>",methods=['GET', 'DELETE'])
def videos(id=None):
	if request.method == 'POST':
		content = request.json
		return video.createVideo(content)
	elif request.method == 'GET':
		if id is not None:
			return video.getVideoById(id)
		else:
			token = request.headers.get('token')
			body = {
				"JWT": token
			}
			headers = {"Content-Type": 'application/json'}
			data = json.dumps(body)
			userType = requests.post("https://serene-shelf-10674.herokuapp.com/token",headers=headers, data=data)
			if userType.status_code == 200:
				if userType.text[1:6] == "admin":
					videos = video.getVideos()
					return videos
				else:
					content = request.json
					friendList = request.args.get('friendList').split(",")
					return video.getAllVideos(friendList)
			else:
				return Response(status=400)
	elif request.method == 'DELETE':
		if id is not None:
			return video.deleteVideo(id)
		else:
			return Response(status=400)
	return

@app.route("/videos/<int:id>/likes",methods=['GET','POST'])
def likes(id=None):
	if (id is None):
		return Response(status=404)
	if request.method == 'POST':
		content = request.json
		return video.likeVideo(id,content)
	if request.method == 'GET':
		return video.getLikes(id)

@app.route("/videos/<int:id>/comments",methods=['POST','GET'])
def comments(id=None):
	if (id is None):
		return Response(status=404)
	if request.method == 'POST':
		content = request.json
		return video.postComment(id,content)
	if request.method == 'GET':
		return video.getComments(id)

@app.route("/videos/user/<id>")
def getUSerVideos(id=None):
	if (id is None):
		return Response(status=404)
	app.logger.debug(id)
	return video.getUserVideo(id)

@app.route("/ping")
def ping():
	return("Hello")

@app.route("/metrics/users/activity")
def userActivity():
	return video.getUsersActivity()

@app.route("/metrics/users/comments")
def userActivityComments():
	return video.userActivityComments()

@app.route("/metrics/videos/likes")
def videosMostLiked():
	return video.videosMostLiked()

@app.route("/metrics/videos/dislikes")
def videosMostDisliked():
	return video.videosMostDisliked()

@app.route("/metrics/videos/comments")
def videosMostCommented():
	return video.videosMostCommented()

if __name__=='__main__':
	#db.drop_all()
	#db.create_all()
	#db.session.commit()
	app.run(debug=True,host='0.0.0.0',port=port)
