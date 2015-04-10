# -*- coding: utf-8 -*-
from os import path, mkdir
from streck import app
from streck.models.user import *
from flask import render_template, request, flash, redirect
from werkzeug.utils import secure_filename

def upload_user_picture(file):
	if not file:
		return None
	if not path.exists(path.join(app.config['UPLOAD_FOLDER'], 'users')):
		mkdir(path.join(app.config['UPLOAD_FOLDER'], 'users'))
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
			flash(u'Användarens ID är ej unikt!')
			return redirect('/admin/user/add')
		fname = upload_user_picture(request.files.get('picture', None))
		u = User.add(request.form['barcode'], request.form['name'], fname)
		if not u.exists():
			flash(u'Användaren kunde inte läggas till!')
			return redirect('/admin/user/add')
		flash(u'Användaren "%s" tillagd.' % u.name())
		return redirect('/admin/user/%s' % u.barcode())
	return redirect('/admin/user')

@app.route('/admin/user/<barcode>')
def admin_show_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/admin/user')
	return render_template('admin/user.html', user=u)

@app.route('/admin/user/<barcode>/update',methods=['POST'])
def admin_edit_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/admin/user')
	name = request.form.get('name', None)
	fname = upload_user_picture(request.files.get('picture', None))
	u.update(name, fname)
	return redirect('/admin/user/%s' % barcode)

@app.route('/admin/user/<barcode>/enable')
def admin_enable_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/admin/user')
	u.enable()
	if u.enabled():
		flash(u'Användaren är inte längre avstängd!')
	else:
		flash(u'Användaren är fortfarande avstängd.')
	return redirect('/admin/user/%s' % barcode)

@app.route('/admin/user/<barcode>/disable')
def admin_disable_user(barcode):
	u = User(barcode)
	if not u.exists():
		flash(u'Användaren existerar inte!')
		return redirect('/admin/user')
	u.disable()
	if u.enabled():
		flash(u'Användaren är fortfarande inte längre avstängd.')
	else:
		flash(u'Användaren är nu avstängd!')
	return redirect('/admin/user/%s' % barcode)
