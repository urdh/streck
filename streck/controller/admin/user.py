# -*- coding: utf-8 -*-
from streck import app
from streck.models.user import *
from flask import render_template, request, flash, redirect

@app.route('/admin/user')
def admin_user_list():
	return render_template('admin/userlist.html', users=User.all())

@app.route('/admin/user/new',methods=['GET','POST'])
def admin_add_user():
	if request.method == 'GET':
		return render_template('admin/useradd.html')
	elif request.method == 'POST':
		u = User(request.form['barcode'])
		if u.exists():
			flash('Användarens ID är ej unikt!')
			return redirect('/admin/user/add')
		# add the user here
		return redirect('/admin/user/%s' % u.barcode())
	return redirect('/admin/user')

@app.route('/admin/user/<barcode>')
def admin_show_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash('Användaren existerar inte!')
		return redirect('/admin/user')
	return render_template('admin/user.html', user=u)

@app.route('/admin/user/<barcode>/update',methods=['POST'])
def admin_edit_user(barcode):
	if request.method == 'POST':
		u = User(barcode)
		if not u.exists():
			flash('Användaren existerar inte!')
			return redirect('/admin/user')
		# update the user here
		return redirect('/admin/user/%s' % barcode)
	return redirect('/admin/user')
