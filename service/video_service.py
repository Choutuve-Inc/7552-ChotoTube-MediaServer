#from db.data_base import Video, Like, Comment
from flask import Flask, jsonify, request, json, Response, make_response
from __init__ import app, db,Video, Like, Comment
import sys
from sqlalchemy import or_, func, desc
import service.rules 
from durable.lang import *

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
		app.logger.error(e)
		return Response(status=400)

def getVideoById(id):
	video = Video.query.filter_by(id=id).first()
	if video is None:
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
	print(video,file=sys.stderr)
	if video is not None:
		db.session.delete(video)
		db.session.commit()
		return Response(status=200)
	else:
		return Response(status=404)

def likeVideo(video_id,content):
	video = Video.query.filter_by(id=video_id).first()
	if video is None:
		return Response(status=404)
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

def postComment(video_id,content):
	video = Video.query.filter_by(id=video_id).first()
	if video is None:
		return Response(status=404)
	user = content['user']
	text = content['text']
	comment = Comment(video_id=video_id,user=user,text=text)
	db.session.add(comment)
	db.session.commit()
	return Response(status=200)

def getLikes(id):
	video = Video.query.filter_by(id=id).first()
	if video is None:
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
		return Response(status=404)
	comment = Comment.query.filter_by(video_id=id).all()
	return jsonify(comments=comment)

def getUsersActivity():
	activity = db.session.query(Video.user,func.count(Video.user)).group_by(Video.user)\
	.order_by((desc(func.count(Video.user)))).all()
	app.logger.debug(activity)
	return jsonify(activity)

def videosMostLiked():
	mostLiked = db.session.query(Video.title,func.count(Like.video_id))\
	.join(Video).filter(Like.value==True).group_by(Like.video_id,Video.title)\
	.order_by((desc(func.count(Like.video_id)))).all()
	app.logger.debug(mostLiked)
	return jsonify(mostLiked)

def videosMostDisliked():
	mostDisliked = db.session.query(Video.title,func.count(Like.video_id))\
	.join(Video).filter(Like.value==False).group_by(Like.video_id,Video.title)\
	.order_by((desc(func.count(Like.video_id)))).all()
	app.logger.debug(mostDisliked)
	return jsonify(mostDisliked)

def videosMostCommented():
	mostComented = db.session.query(Video.title,func.count(Comment.video_id))\
	.join(Video).group_by(Comment.video_id,Video.title)\
	.order_by((desc(func.count(Comment.video_id)))).all()
	app.logger.debug(mostComented)
	return jsonify(mostComented)

def userActivityComments():
	activity = db.session.query(Comment.user,func.count(Comment.user)).group_by(Comment.user)\
	.order_by((desc(func.count(Comment.user)))).all()
	app.logger.debug(activity)
	return jsonify(activity)