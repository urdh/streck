# -*- coding: utf-8 -*-
from streck import app
from streck.models.product import *
from flask import render_template, request, flash, redirect, send_from_directory

@app.route('/product',methods=['POST'])
def product_arrival():
	if request.method == 'POST':
		p = Product(request.form['barcode'])
		if not p.exists():
			flash(u'Produkten eller användaren existerar inte!')
			return redirect('/')
		return redirect('/product/%s' % p.barcode())
	return redirect('/')

@app.route('/product/<barcode>')
def product_showcase(barcode):
	p = Product(barcode)
	if not p.exists():
		flash(u'Produkten existerar inte!')
		return redirect('/')
	return render_template('product.html', product=p)

@app.route('/static/products/<filename>')
def product_picture(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'products/'), filename)
