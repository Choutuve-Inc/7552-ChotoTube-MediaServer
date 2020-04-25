from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class Video(db.Model):
	__tablename__ = "videos"

	id = db.Column(db.Integer, primary_key=True)
	video_name = db.Column(db.String(128), unique=True, nullable=False)
	video_size = db.Column(db.Integer)
	date_of_upload = db.Column(db.DateTime)
	


@app.route("/")
def hello_world():
	return jsonify(hello="world")

