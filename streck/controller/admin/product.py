# -*- coding: utf-8 -*-
from os import path
from streck import app
from streck.models.product import *
from flask import render_template, request, flash, redirect

def upload_product_picture(file):
	if not file:
		return None
	fname = path.join('products/', secure_filename(file.filename))
	file.save(path.join(app.config['UPLOAD_FOLDER'], fname))
	return fname

@app.route('/admin/product')
def admin_product_list():
	return render_template('admin/productlist.html', products=Product.all())

@app.route('/admin/product/add',methods=['GET','POST'])
def admin_add_product():
	if request.method == 'GET':
		return render_template('admin/productadd.html', categories=Product.categories())
	elif request.method == 'POST':
		p = Product(request.form['barcode'])
		if p.exists():
			flash(u'Produktens ID är ej unikt!')
			return redirect('/admin/product/add')
		fname = upload_product_picture(request.files.get('picture', None))
		p = Product.add(request.form['barcode'], request.form['name'], request.form['price'], request.form['category'], fname)
		if not p.exists():
			flash(u'Användaren kunde inte läggas till!')
			return redirect('/admin/product/add')
		flash(u'Produkten "%s" tillagd.' % p.name())
		return redirect('/admin/product/%s' % p.barcode())
	return redirect('/admin/product')

@app.route('/admin/product/<barcode>')
def admin_show_product(barcode):
	p = Product(barcode)
	if not p.exists():
		flash(u'Produkten existerar inte!')
		return redirect('/admin/product')
	return render_template('admin/product.html', product=p)

@app.route('/admin/product/<barcode>/update',methods=['POST'])
def admin_edit_product(barcode):
	if request.method == 'POST':
		p = Product(barcode)
		if not p.exists():
			flash(u'Produkten existerar inte!')
			return redirect('/admin/product')
		fname = upload_product_picture(request.files.get('picture', None))
		p.update(request.form['name'], request.form['price'], request.form['category'], fname)
		return redirect('/admin/product/%s' % barcode)
	return redirect('/admin/product')
