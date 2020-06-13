from __init__ import db
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_sqlalchemy import SQLAlchemy


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
	
	def __repr__(self):
		return '<Video %r>' % self.video_name

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

db.drop_all()
db.create_all()
db.session.commit()