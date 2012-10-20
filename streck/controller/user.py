# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from flask import render_template, request, flash, redirect, send_from_directory

@app.route('/user',methods=['POST'])
def user_arrival():
	if request.method == 'POST':
		u = User(request.form['barcode'])
		if u.barcode() == app.config['LOGOUT_BARCODE']:
			return redirect('/')
		if not u.exists():
			return redirect('/product/%s' % u.barcode())
		return redirect('/user/%s' % u.barcode())
	return redirect('/')

@app.route('/user/<barcode>')
def show_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash('Användaren existerar inte!')
		return redirect('/')
	return render_template('user.html', user=u)

@app.route('/pictures/users/<filename>')
def product_picture(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'users/'), filename)
