from __init__ import db
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


class Video(db.Model):
	__tablename__ = "videos"

	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(64), nullable=False)
	title = db.Column(db.String(64), nullable=False)
	size = db.Column(db.Float)
	date = db.Column(db.String(10), nullable=False)
	url = db.Column(db.String(128), nullable=False)
	thumbnail = db.Column(db.String(128), nullable=False)
	description =  db.Column(db.String(256))
	
	like = relationship("Like", cascade="all, delete-orphan")
	comments = relationship("Comment", cascade="all, delete-orphan")

	def __repr__(self):
		return '<Video %r>' % self.title

class Like(db.Model):
	__tablename__="like"

	id = db.Column(db.Integer, primary_key=True)
	video_id = db.Column(db.Integer,db.ForeignKey('videos.id'),nullable=False)
	user = db.Column(db.String(64), nullable=False)
	value = db.Column(db.Boolean, nullable=False) #Like es true, dislike es false
	__table_args__ = (db.UniqueConstraint('video_id','user'),)


class Comment(db.Model):
	__tablename__ = "comment"

	id = db.Column(db.Integer, primary_key=True)
	video_id = db.Column(db.Integer,db.ForeignKey('videos.id'),nullable=False)
	user = db.Column(db.String(64), nullable=False)
	text = db.Column(db.String(256), nullable=False)
	__table_args__ = (db.UniqueConstraint('video_id','user'),)

