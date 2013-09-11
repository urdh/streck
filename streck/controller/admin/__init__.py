# -*- coding: utf-8 -*-
from streck import app
from flask import render_template
import streck.controller.admin.user
import streck.controller.admin.export
import streck.controller.admin.product

@app.route('/admin')
def admin_index():
	return render_template('admin/index.html')
