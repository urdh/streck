# -*- coding: utf-8 -*-
from streck import app
from streck.models.stats import *
from flask import render_template, Response, stream_with_context

@app.route('/stats')
def stats():
	return render_template('stats.html', stats=Stats)

@app.route('/stats/timeseries.csv')
def csvseries():
	def generate():
		series = Stats.timeseries()
		yield 'Datum,Total\n'
		for row in series:
			yield '%s,%10.3f\n' % row
	return Response(stream_with_context(generate()), mimetype='text/csv')
