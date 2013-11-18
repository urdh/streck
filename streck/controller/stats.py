# -*- coding: utf-8 -*-
from streck import app
from streck.models.stats import *
from streck.models.product import *
from flask import render_template, Response, stream_with_context

@app.route('/stats')
def stats():
	return render_template('stats.html', stats=Stats, categories=Product.categories())

@app.route('/stats/timeseries.csv')
def csvseries():
	def generate():
		series = Stats.timeseries()
		categories = []
		data = {}
		for row in series:
			if not row[1] in categories:
				categories.append(row[1])
		for row in series:
			if not row[0] in data.keys():
				data[row[0]] = [0.0] * categories.__len__()
			idx = categories.index(row[1])
			data[row[0]][idx] = row[2]
		yield 'Datum,%s\n' % ','.join(categories)
		for date, row in data.iteritems():
			yield '%s,%s\n' % (date, ','.join(['%10.3f' % s for s in row]))
	return Response(stream_with_context(generate()), mimetype='text/csv')
