# -*- coding: utf-8 -*-
import sqlite3
from flask import g
from streck.models.user import *

class Product(object):
	def __init__(self, barcode):
		self.bcode = barcode

	def barcode(self):
		return self.bcode

	def allowed_jobbmat(self):
		return (self.category() in app.config['ALLOWED_JOBBMAT_CATEGORIES'])

	def id(self):
		if not self.exists():
			return None
		g.db.execute('select id from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return int(r['id'])

	def exists(self):
		g.db.execute('select id from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r != None

	def picture(self):
		if not self.exists():
			return None
		g.db.execute('select image from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		if r['image'] == None:
			return '../img/NoneProduct.png'
		return r['image']

	def name(self):
		if not self.exists():
			return None
		g.db.execute('select name from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['name']

	def price(self):
		if not self.exists():
			return None
		g.db.execute('select price from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return float(r['price'])

	def category(self):
		if not self.exists():
			return None
		g.db.execute('select c.name from products p, categories c where p.barcode = ? and c.id = p.category', [self.bcode])
		r = g.db.fetchone()
		return r['name']

	def update(self, name=None, price=None, category=None, picture=None):
		if not self.exists():
			return False
		if name != None:
			g.db.execute('update products set name = ? where barcode = ?', [name, self.bcode])
			# we should check query success here
		if price != None:
			g.db.execute('update products set price = ? where barcode = ?', [price, self.bcode])
			# we should check query success here
		if category != None:
			g.db.execute('update products set category = ? where barcode = ?', [category, self.bcode])
			# we should check query success here
		if picture != None:
			g.db.execute('update products set image = ? where barcode = ?', [picture, self.bcode])
			# we should check query success here
		return True

	def toplist(self):
		g.db.execute('select u.barcode, count(t.id) as total from users as u, transactions as t, products as p where t.product = p.id and p.barcode = ? and t.user = u.id group by t.user order by total desc limit 10', [self.bcode])
		return [(User(r['barcode']), r['total']) for r in g.db.fetchall()]

	@classmethod
	def all(cls):
		g.db.execute('select barcode from products order by name asc')
		return [Product(r['barcode']) for r in g.db.fetchall()]

	@classmethod
	def add(cls, barcode, name, price, category, picture):
		if Product(barcode).exists():
			return None
		g.db.execute('insert into products values (null, ?, ?, ?, ?, ?, null)', [barcode, name, price, category, picture])
		return Product(barcode)

	# This really ought to be in a separate model, but meh
	@classmethod
	def categories(cls):
		g.db.execute('select id, name from categories')
		return g.db.fetchall()
