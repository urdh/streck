# -*- coding: utf-8 -*-
from os import path
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.controller.transaction import *
from flask import render_template, redirect

@app.route('/admin/export')
def admin_export():
	return render_template('admin/export.html', users=User.all(), categories=Product.categories())

@app.route('/admin/export/empty')
def admin_export_empty():
	for user in User.all():
		Transaction(user.barcode(), paid=True).perform()
	return redirect('/admin')
