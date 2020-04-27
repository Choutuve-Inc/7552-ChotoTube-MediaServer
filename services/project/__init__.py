from flask import Flask, jsonify, request, json, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


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

	id = db.Column(db.Integer, primary_key=True)
	video_name = db.Column(db.String(64), unique=True, nullable=False)
	video_size = db.Column(db.Integer)
	date_of_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	url = db.Column(db.String(128), unique=True, nullable=False)
	
	def __repr__(self):
		return '<Video %r>' % self.video_name



@app.route("/")
def hello_world():
	return jsonify(hello="world")

@app.route("/videos",methods=['GET','POST'])
@app.route("/videos/<string:name>",methods=['GET'])
def videos(name=None):
	if request.method == 'POST':
		content = request.json
		name = content['name']
		size = content['size']
		url = content['url']
		video = Video(video_name=name,video_size=size,url=url)
		db.session.add(video)
		db.session.commit()
		return Response(status=200)
	elif request.method == 'GET':
		print(name)
		if name is not None:
			video = Video.query.filter_by(video_name=name).first()
			return jsonify(video)
		else:
			videos = Video.query.all()
			return jsonify(videos)
	return
