# -*- coding: utf-8 -*-
from os import path, getcwd
from streck import app
from streck.models.product import *
from flask import render_template, request, flash, redirect, send_file
from flaskext.babel import gettext

@app.route('/product',methods=['POST'])
def product_arrival():
	if request.method == 'POST':
		p = Product(request.form['barcode'])
		if not p.exists():
			flash(gettext(u'Product/user does not exist!'))
			return redirect('/')
		return redirect('/product/%s' % p.barcode())
	return redirect('/')

@app.route('/product/<barcode>')
def product_showcase(barcode):
	p = Product(barcode)
	if not p.exists():
		flash(gettext(u'Product does not exist!'))
		return redirect('/')
	return render_template('product.html', product=p)

@app.route('/images/products/<path:filename>')
def product_picture(filename):
	return send_file(path.join(app.config['UPLOAD_FOLDER'], 'products/', filename)) # unsafe!
