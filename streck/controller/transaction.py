# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.models.transaction import *
from flask import render_template, request, flash, redirect

@app.route('/user/<user>/buy',methods=['POST'])
def transaction_arrival(user):
	u = User(user)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	p = User(request.form['barcode'])
	if p.exists():
		return redirect('/user/%s' % p.barcode())
	p = Product(request.form['barcode'])
	if p.barcode() == app.config['LOGOUT_BARCODE']:
		flash(u'Du har loggats ut!')
		return redirect('/')
	if p.barcode() == app.config['PAID_BARCODE']:
		return redirect('/user/%s/paid' % u.barcode())
	if not u.enabled():
		return redirect('/user/%s?disabled' % u.barcode())
	if p.barcode() == app.config['UNDO_BARCODE']:
		return redirect('/user/%s/undo' % u.barcode())
	if not p.exists():
		flash(u'Produkten existerar inte!')
		return redirect('/user/%s' % u.barcode())
	return redirect('/user/%s/buy/%s' % (u.barcode(), p.barcode()))

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
	if (u.barcode() == app.config['JOBBMAT_BARCODE'] or u.barcode() == app.config['REMOVE_JOBBMAT_BARCODE']) and not p.allowed_jobbmat():
		return redirect('/user/%s?disabled' % u.barcode())
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
