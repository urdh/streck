# -*- coding: utf-8 -*-
from os import path, getcwd
from streck import app
from streck.models.user import *
from streck.models.product import *
from flask import render_template, request, flash, redirect, send_file

@app.route('/disabled')
def user_is_disabled():
	return render_template('no.html')

@app.route('/user',methods=['POST'])
def user_arrival():
	u = User(request.form['barcode'])
	if u.barcode() == app.config['LOGOUT_BARCODE']:
		return redirect('/')
	if not u.exists():
		return redirect('/product/%s' % u.barcode())
	if u.disabled():
		return redirect('/disabled')
	return redirect('/user/%s' % u.barcode())

@app.route('/user/<barcode>')
def show_user(barcode):
	undone = request.args.get('undone', False)
	bought = Product(request.args.get('bought', None))
	if not bought.exists():
		bought = False
	paid = request.args.get('paid', False)
	disabled = request.args.get('disabled', False)
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	if u.disabled():
		return redirect('/disabled')
	return render_template('user.html', user=u, undone=undone, bought=bought, paid=paid, disabled=disabled)

@app.route('/images/users/<path:filename>')
def user_picture(filename):
	return send_file(path.join(app.config['UPLOAD_FOLDER'], 'users/', filename)) # unsafe!
