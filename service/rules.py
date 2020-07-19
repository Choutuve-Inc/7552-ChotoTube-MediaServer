from durable.lang import *
from __init__ import app, db, Video, Like, Comment
from datetime import datetime

with ruleset('ranking'):
	# antecedent
	@when_all(s.event == 'cantVideos')
	def activity(c):
		# consequent
		app.logger.debug("Se cuenta la actividad de los usuarios")
		for video in c.s.videos:
			cantVideos = Video.query.filter(Video.user.like(video['user'])).count()
			video['weight'] += 0.5*(cantVideos)
		c.s.event = 'reactions'

	@when_all(s.event == 'reactions')
	def countReaction(c):
		app.logger.debug("Se cuenta los likes del video")
		for video in c.s.videos:
			likes = len(list(filter(lambda x: x['value']==True,video['like'])))
			disLikes = len(list(filter(lambda x: x['value']==False,video['like'])))
			video['weight'] += 0.7*(likes - disLikes)
		c.s.event = 'comments'

	@when_all(s.event == 'comments')
	def countComments(c):
		app.logger.debug("Se cuentan los comentarios")
		for video in c.s.videos:
			comments = len(video['comments'])
			video['weight'] += 0.2*(comments)
		c.s.event = 'date'

	@when_all(s.event == 'date')
	def divideByDate(c):
		app.logger.debug("Se toma en cuenta la fecha del video")
		today = datetime.now()
		for video in c.s.videos:
			videoDate = datetime.strptime(video['date'],'%Y-%m-%d')
			diference = abs((today - videoDate).days) + 1
			video['weight'] = video['weight']/(0.3*diference)
		c.s.event = 'sort'


	@when_all(s.event == 'sort')
	def order(c):
		app.logger.debug("Se hace el sort de videos")
		c.s.videos = sorted(c.s.videos,key=lambda x:x['weight'],reverse=True)
		c.s.event = 'end'
