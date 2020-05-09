import os
from flask import Flask, jsonify, request, json, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta


app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)

port = int(os.environ.get("PORT", 5000))

#JSON ENCODER
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



class Video(db.Model):
	__tablename__ = "videos"

	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(64), nullable=False)
	title = db.Column(db.String(64), nullable=False)
	size = db.Column(db.Float)
	date = db.Column(db.DateTime, nullable=False)
	url = db.Column(db.String(128), nullable=False)
	thumbnail = db.Column(db.String(128), nullable=False)
	
	def __repr__(self):
		return '<Video %r>' % self.video_name



@app.route("/")
def hello_world():
	return jsonify(hello="world")

@app.route("/videos",methods=['GET','POST', 'DELETE'])
@app.route("/videos/<int:id>",methods=['GET', 'DELETE'])
def videos(id=None):
	if request.method == 'POST':
		try:
			content = request.json
			title = content['title']
			size = content['size']
			url = content['url']
			user = content['user']
			thumbnail = content['thumbnail']
			date = datetime.strptime(content['date'],'%Y-%m-%d').date()
			print(date, flush=True)
			video = Video(title=title,size=size,url=url,user=user,thumbnail=thumbnail,date=date)
			db.session.add(video)
			db.session.commit()
			return Response(status=200)
		except Exception as e:
			return Response(status=400)
	elif request.method == 'GET':
		if id is not None:
			video = Video.query.filter_by(id=id).first()
			return jsonify(video)
		else:
			videos = Video.query.all()
			return jsonify(videos)
	elif request.method == 'DELETE':
		if id is not None:
			video = Video.query.filter_by(id=id).first()
			if video is not None:
				db.session.delete(video)
				db.session.commit()
				return Response(status=200)
			else:
				return Response(status=400)
		else:
			return Response(status=400)
	return


if __name__=='__main__':
	db.drop_all()
	db.create_all()
	db.session.commit()
	app.run(debug=True,host='0.0.0.0',port=port)