# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.models.transaction import *
from flask import render_template, request, flash, redirect

@app.route('/user/<user>/buy',methods=['POST'])
def transaction_arrival(user):
	if request.method == 'POST':
		u = User(user)
		if not u.exists():
			flash(u'Användaren existerar inte!')
			return redirect('/')
		if User(request.form['barcode']).exists():
			return redirect('/user/%s' % u.barcode())
		p = Product(request.form['barcode'])
		if p.barcode() == app.config['LOGOUT_BARCODE']:
			return redirect('/')
		if p.barcode() == app.config['PAID_BARCODE']:
			return redirect('/user/%s/paid' % u.barcode())
		if not u.enabled():
			flash(u'Användaren är avstängd!')
			return redirect('/user/%s' % u.barcode())
		if p.barcode() == app.config['UNDO_BARCODE']:
			return redirect('/user/%s/undo' % u.barcode())
		if not p.exists():
			flash(u'Produkten existerar inte!')
			return redirect('/user/%s' % u.barcode())
		return redirect('/user/%s/buy/%s' % (u.barcode(), p.barcode()))
	return redirect('/')

@app.route('/user/<user>/buy/<product>')
def transaction_action(user, product):
	u = User(user)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	if not u.enabled():
		flash(u'Användaren är avstängd!')
		return redirect('/user/%s' % u.barcode())
	p = Product(product)
	if not p.exists():
		flash(u'Produkten existerar inte!')
		return redirect('/user/%s' % u.barcode())
	t = Transaction(u.barcode(), p.barcode(), p.price())
	if t.perform():
		flash(u'Köpte %s!' % p.name())
		return redirect('/user/%s' % u.barcode())
	flash(u'Ett fel uppstod!')
	return redirect('/user/%s' % u.barcode())

@app.route('/user/<user>/paid')
def transaction_paid(user):
	u = User(user)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	t = Transaction(u.barcode(), paid=True)
	if t.perform():
		flash(u'Tömde strecklista för %s!', u.name())
		return redirect('/user/%s' % u.barcode())
	flash(u'Ett fel uppstod!')
	return redirect('/user/%s' % u.barcode())

@app.route('/user/<user>/undo')
def transaction_paid(user):
	u = User(user)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	if not u.enabled():
		flash(u'Användaren är avstängd!')
		return redirect('/user/%s' % u.barcode())
	t = Transaction(u.barcode(), undo=True)
	if t.perform():
		flash(u'Ångrade köp för %s!', u.name())
		return redirect('/user/%s' % u.barcode())
	flash(u'Ett fel uppstod!')
	return redirect('/user/%s' % u.barcode())
	
