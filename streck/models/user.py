# -*- coding: utf-8 -*-
import sqlite3
from flask import g
from streck import app

class User(object):
	def __init__(self, barcode):
		self.reverse = False
		self.bcode = barcode
		if self.bcode == app.config['REMOVE_JOBBMAT_BARCODE']:
			self.bcode = app.config['JOBBMAT_BARCODE']
			self.reverse = True

	def reverse(self):
		return self.reverse

	def barcode(self):
		if self.reverse:
			return app.config['REMOVE_JOBBMAT_BARCODE']
		return self.bcode

	def id(self):
		if not self.exists():
			return None
		g.db.execute('select id from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return int(r['id'])

	def exists(self):
		g.db.execute('select id from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r != None

	def picture(self):
		if not self.exists():
			return None
		g.db.execute('select image from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		if r['image'] == None:
			return '../img/NoneUser.png'
		return r['image']

	def name(self):
		if not self.exists():
			return None
		g.db.execute('select name from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['name']

	def last_paid_id(self):
		if not self.exists():
			return 0
		g.db.execute('select t.id as id from transactions as t, users as u where u.barcode = ? and u.id = t.user and (t.notes = "paid" or t.price < 0) order by id desc limit 1', [self.bcode])
		r = g.db.fetchone()
		if r == None:
			return -1
		return int(r['id'])

	def debt(self):
		if not self.exists():
			return 0.0
		g.db.execute('select sum(t.price) as debt from transactions as t, users as u where t.user = u.id and u.barcode = ?', [self.bcode])
		r = g.db.fetchone()
		if r['debt'] == None:
			return 0.0
		return float(r['debt'])

	def debt_per_category(self):
		if not self.exists():
			return []
		g.db.execute('select c.name as name, sum(t.price) as debt from transactions as t, users as u left join products as p on p.id = t.product left join categories as c on p.category = c.id where u.barcode = ? and t.user = u.id and t.id > ? group by p.category', [self.bcode, self.last_paid_id()])
		return g.db.fetchall()

	def transactions(self):
		if not self.exists():
			return []
		g.db.execute('select p.name as name, t.price as price, t.added as added, t.notes as notes from transactions as t, users as u left join products as p on t.product = p.id where u.barcode = ? and t.user = u.id', [self.bcode])
		return g.db.fetchall()

	def enabled(self):
		if not self.exists():
			return False
		g.db.execute('select enabled from users where barcode = ?', [self.bcode])
		return g.db.fetchone()['enabled'] == True

	def disabled(self):
		return not self.enabled()

	def enable(self, e=True):
		if self.exists():
			g.db.execute('update users set enabled = ? where barcode = ?', [e, self.bcode])
		return self.enabled()

	def disable(self):
		return self.enable(False)

	def update(self, name=None, picture=None):
		if not self.exists():
			return False
		if name != None:
			g.db.execute('update users set name = ? where barcode = ?', [name, self.bcode])
			# we should check query success here
		if picture != None:
			g.db.execute('update users set image = ? where barcode = ?', [picture, self.bcode])
			# we should check query success here
		return True

	@classmethod
	def all(cls):
		g.db.execute('select barcode from users order by name asc')
		return [User(r['barcode']) for r in g.db.fetchall()]

	@classmethod
	def add(cls, barcode, name, picture):
		if User(barcode).exists():
			return None
		g.db.execute('insert into users values (null, ?, 1, ?, ?, null)', [barcode, name, picture])
		return User(barcode)
