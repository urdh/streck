# -*- coding: utf-8 -*-
from os import path
from streck import app
from streck.models.user import *
from flask import render_template, request, flash, redirect
from flaskext.babel import gettext

def upload_user_picture(file):
	if not file:
		return None
	fname = path.join('users/', secure_filename(file.filename))
	file.save(path.join(app.config['UPLOAD_FOLDER'], fname))
	return fname

@app.route('/admin/user')
def admin_user_list():
	return render_template('admin/userlist.html', users=User.all())

@app.route('/admin/user/add',methods=['GET','POST'])
def admin_add_user():
	if request.method == 'GET':
		return render_template('admin/useradd.html')
	elif request.method == 'POST':
		u = User(request.form['barcode'])
		if u.exists():
			flash(gettext(u'User ID not unique!'))
			return redirect('/admin/user/add')
		fname = upload_user_picture(request.files.get('picture', None))
		u = User.add(request.form['barcode'], request.form['name'], fname)
		if not u.exists():
			flash(gettext(u'Could not add user!'))
			return redirect('/admin/user/add')
		flash(gettext(u'User %(name)s added!', name=u.name()))
		return redirect('/admin/user/%s' % u.barcode())
	return redirect('/admin/user')

@app.route('/admin/user/<barcode>')
def admin_show_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(gettext(u'User does not exist!'))
		return redirect('/admin/user')
	return render_template('admin/user.html', user=u)

@app.route('/admin/user/<barcode>/update',methods=['POST'])
def admin_edit_user(barcode):
	if request.method == 'POST':
		u = User(barcode)
		if not u.exists():
			flash(gettext(u'User does not exist!'))
			return redirect('/admin/user')
		fname = upload_user_picture(request.files.get('picture', None))
		u.update(request.form['name'], fname)
		return redirect('/admin/user/%s' % barcode)
	return redirect('/admin/user')

@app.route('/admin/user/<barcode>/enable')
def admin_enable_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(gettext(u'User does not exist!'))
		return redirect('/admin/user')
	u.enable()
	if u.enabled():
		flash(gettext(u'User %(name)s is no longer disabled!', name=u.name()))
	else:
		flash(gettext(u'User %(name)s is still disabled!', name=u.name()))
	return redirect('/admin/user/%s' % barcode)

@app.route('/admin/user/<barcode>/disable')
def admin_disable_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(gettext(u'User does not exist!'))
		return redirect('/admin/user')
	u.disable()
	if u.enabled():
		flash(gettext(u'User %(name)s is still enabled!', name=u.name()))
	else:
		flash(gettext(u'User %(name)s is no longer enabled!', name=u.name()))
	return redirect('/admin/user/%s' % barcode)

