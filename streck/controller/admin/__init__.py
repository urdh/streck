# -*- coding: utf-8 -*-
from streck import app
from flask import render_template
from flaskext.babel import Babel
import streck.controller.admin.user
import streck.controller.admin.product

babel = Babel(app)

@app.route('/admin')
def admin_index():
	return render_template('admin/index.html')
