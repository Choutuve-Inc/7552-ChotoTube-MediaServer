from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from dataclasses import dataclass


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Media server"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


class Video(db.Model):
	__tablename__ = "videos"

	id: int
	video_name: str
	video_size: int
	date_of_upload: datetime

	id = db.Column(db.Integer, primary_key=True)
	video_name = db.Column(db.String(128), unique=True, nullable=False)
	video_size = db.Column(db.Integer)
	date_of_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Video %r>' % self.video_name



@app.route("/")
def hello_world():
	return jsonify(hello="world")

@app.route("/videos",methods=['GET','POST'])
def videos():
	if request.method == 'POST':
		pass
	elif request.method == 'GET':
		videos = Video.query.all()
		return jsonify(videos)
	return
