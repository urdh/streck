# -*- coding: utf-8 -*-
from streck import app
from streck.models.product import *
from flask import render_template, request, flash, redirect

@app.route('/admin/product')
def admin_product_list():
	return render_template('admin/productlist.html', products=Product.all())

@app.route('/admin/product/new',methods=['GET','POST'])
def admin_add_product():
	if request.method == 'GET':
		return render_template('admin/productadd.html')
	elif request.method == 'POST':
		p = Product(request.form['barcode'])
		if p.exists():
			flash('Produktens ID är ej unikt!')
			return redirect('/admin/product/add')
		# add the product here
		return redirect('/admin/product/%s' % p.barcode())
	return redirect('/admin/product')

@app.route('/admin/product/<barcode>')
def admin_show_product(barcode):
	p = Product(barcode)
	if not p.exists():
		flash('Produkten existerar inte!')
		return redirect('/admin/product')
	return render_template('admin/product.html', product=p)

@app.route('/admin/product/<barcode>/update',methods=['POST'])
def admin_edit_product(barcode):
	if request.method == 'POST':
		p = Product(barcode)
		if not p.exists():
			flash('Produkten existerar inte!')
			return redirect('/admin/product')
		# update the product here
		return redirect('/admin/product/%s' % barcode)
	return redirect('/admin/product')
