# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from streck.models.product import *
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
	undone = request.args.get('undone', False)
	bought = Product(request.args.get('bought', None))
	print bought
	print bought.name()
	if not bought.exists():
		bought = False
	paid = request.args.get('paid', False)
	disabled = request.args.get('disabled', False)
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/')
	return render_template('user.html', user=u, undone=undone, bought=bought, paid=paid, disabled=disabled)

@app.route('/static/users/<filename>')
def product_picture(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'users/'), filename)
