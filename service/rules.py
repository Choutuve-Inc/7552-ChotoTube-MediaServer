from durable.lang import *
from __init__ import app, db, Video, Like, Comment
from datetime import datetime

COEFICIENTS = {
	'ATIVITY': 2,
	'REACTIONS': 5,
	'COMMENTS':1,
	'DATE_NEW':0.5,
	'DATE_REASENT':2,
	'DATE_OLD':10
}

with ruleset('ranking'):
	# antecedent
	@when_all(s.event == 'cantVideos')
	def activity(c):
		# consequent
		app.logger.debug("Se cuenta la actividad de los usuarios")
		for video in c.s.videos:
			cantVideos = Video.query.filter(Video.user.like(video['user'])).count()
			video['weight'] += COEFICIENTS['ATIVITY']*(cantVideos)
		c.s.event = 'reactions'

	@when_all(s.event == 'reactions')
	def countReaction(c):
		app.logger.debug("Se cuenta los likes del video")
		for video in c.s.videos:
			likes = len(list(filter(lambda x: x['value']==True,video['like'])))
			disLikes = len(list(filter(lambda x: x['value']==False,video['like'])))
			video['weight'] += 5*(likes - disLikes)
		c.s.event = 'comments'

	@when_all(s.event == 'comments')
	def countComments(c):
		app.logger.debug("Se cuentan los comentarios")
		for video in c.s.videos:
			comments = len(video['comments'])
			video['weight'] += (comments)
		c.s.event = 'date'

	@when_all(s.event == 'date')
	def divideByDate(c):
		app.logger.debug("Se toma en cuenta la fecha del video")
		today = datetime.now()
		for video in c.s.videos:
			videoDate = datetime.strptime(video['date'],'%Y-%m-%d')
			diference = abs((today - videoDate).days) + 1
			video['weight'] = video['weight']/(0.5*diference)
			#if diference < 5:
			#	video['weight'] = video['weight']/(0.5*diference)
			#elif deiference < 15:
			#	video['weight'] = video['weight']/(2*diference)
			#else:
			#	app.logger.debug("video muy viejo")
			#	video['weight'] = video['weight']/(10*diference)
		c.s.event = 'sort'


	@when_all(s.event == 'sort')
	def order(c):
		app.logger.debug("Se hace el sort de videos")
		c.s.videos = sorted(c.s.videos,key=lambda x:x['weight'],reverse=True)
		c.s.event = 'end'
