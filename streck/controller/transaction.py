# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.models.transaction import *
from flask import render_template, request, flash, redirect
from flaskext.babel import gettext

@app.route('/user/<user>/buy',methods=['POST'])
def transaction_arrival(user):
	if request.method == 'POST':
		u = User(user)
		if not u.exists():
			return redirect('/')
		p = User(request.form['barcode'])
		if p.exists():
			return redirect('/user/%s' % p.barcode())
		p = Product(request.form['barcode'])
		if p.barcode() == app.config['LOGOUT_BARCODE']:
			return redirect('/')
		if p.barcode() == app.config['PAID_BARCODE']:
			return redirect('/user/%s/paid' % u.barcode())
		if not u.enabled():
			return redirect('/user/%s?disabled' % u.barcode())
		if p.barcode() == app.config['UNDO_BARCODE']:
			return redirect('/user/%s/undo' % u.barcode())
		if not p.exists():
			return redirect('/user/%s' % u.barcode())
		return redirect('/user/%s/buy/%s' % (u.barcode(), p.barcode()))
	return redirect('/')

@app.route('/user/<user>/buy/<product>')
def transaction_action(user, product):
	u = User(user)
	if not u.exists():
		return redirect('/')
	if not u.enabled():
		return redirect('/user/%s?disabled' % u.barcode())
	p = Product(product)
	if not p.exists():
		return redirect('/user/%s' % u.barcode())
	t = Transaction(u.barcode(), p.barcode(), p.price())
	if t.perform():
		return redirect('/user/%s?bought=%s' % (u.barcode(), p.barcode()))
	return redirect('/error')

@app.route('/user/<user>/paid')
def transaction_paid(user):
	u = User(user)
	if not u.exists():
		return redirect('/')
	t = Transaction(u.barcode(), paid=True)
	if t.perform():
		return redirect('/user/%s?paid' % u.barcode())
	return redirect('/error')

@app.route('/user/<user>/undo')
def transaction_undo(user):
	u = User(user)
	if not u.exists():
		return redirect('/')
	if not u.enabled():
		return redirect('/user/%s?disabled' % u.barcode())
	t = Transaction(u.barcode(), undo=True)
	if t.perform():
		return redirect('/user/%s?undone' % u.barcode())
	return redirect('/error')

