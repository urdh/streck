# -*- coding: utf-8 -*-
from streck import app
from flask import render_template
import streck.controller.user
import streck.controller.product
import streck.controller.transaction
import streck.controller.admin

@app.route('/')
def index():
	return render_template('index.html')
