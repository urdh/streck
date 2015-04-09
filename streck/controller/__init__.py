# -*- coding: utf-8 -*-
from streck import app
from flask import render_template
import streck.controller.user
import streck.controller.product
import streck.controller.transaction
import streck.controller.admin
import streck.controller.stats

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/error')
def error():
	return render_template('error.html')

# TODO: a real error handler using @app.errorhandler(404)
