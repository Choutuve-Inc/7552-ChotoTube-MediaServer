from durable.lang import *
from __init__ import app

with ruleset('ranking'):
	# antecedent
	@when_all(s.event == 'weight')
	def order(c):
		# consequent
		for video in c.s.videos['videos']:
			video['weight'] += 1
		c.s.event = 'finish'
		