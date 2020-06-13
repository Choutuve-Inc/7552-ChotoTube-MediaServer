import os
from flask import Flask, jsonify, request, json, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.ext.declarative import DeclarativeMeta
from config.encoder import AlchemyEncoder
import service.video_service as video


app = Flask(__name__)
app.config.from_object("config.config.Config")
db = SQLAlchemy(app)

port = int(os.environ.get("PORT", 5000))

app.json_encoder = AlchemyEncoder


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
			return video.getAllVideos()
	elif request.method == 'DELETE':
		if id is not None:
			return video.deleteVideo(id)
		else:
			return Response(status=400)
	return

@app.route("/likes",methods=['POST'])
def likes():
	if request.method == 'POST':
		content = request.json
		return video.likeVideo(content)

@app.route("/comments",methods=['POST'])
def comments():
	if request.method == 'POST':
		content = request.json
		return video.postComment(content)

if __name__=='__main__':
	app.run(debug=True,host='0.0.0.0',port=port)