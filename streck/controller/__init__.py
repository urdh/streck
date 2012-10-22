# -*- coding: utf-8 -*-
from streck import app
from flask import render_template
from flaskext.babel import Babel
import streck.controller.user
import streck.controller.product
import streck.controller.transaction
import streck.controller.admin
import streck.controller.stats

babel = Babel(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/error')
def error():
	return render_template('error.html')
