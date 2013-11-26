# -*- coding: utf-8 -*-
from collections import deque
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
		categoryhistory = []
		data = {}
		for row in series:
			if not row[1] in categories:
				categories.append(row[1])
				categoryhistory.append(deque([0.0] * 7))
		for row in series:
			if not row[0] in data.keys():
				data[row[0]] = [0.0] * (categories.__len__() * 2 + 1)
			idx = categories.index(row[1])
			data[row[0]][idx] = row[2]
		yield 'Datum,%s,%s,Glidmedel summa\n' % (','.join(categories), ','.join(['Glidmedel ' + c for c in categories]))
		for date in sorted(data.iterkeys()):
			for idx, cat in enumerate(categories):
				categoryhistory[idx].popleft()
				categoryhistory[idx].append(data[date][idx])
				data[date][2 + idx] = sum(categoryhistory[idx]) / 7
			data[date][4] = data[date][2] + data[date][3]
			yield '%s,%s\n' % (date, ','.join(['%10.3f' % s for s in data[date]]))
	return Response(stream_with_context(generate()), mimetype='text/csv')
