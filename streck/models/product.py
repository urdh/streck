# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Product(object):
	def __init__(self, barcode):
		self.bcode = barcode

	def barcode(self):
		return self.bcode

	def id(self):
		if not self.exists():
			return None
		g.db.execute('select id from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['id']

	def exists(self):
		g.db.execute('select id from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r != None

	def picture(self):
		if not self.exists():
			return None
		g.db.execute('select image from products where barcode = ?', [self.bcode])
		r = g.db.fetchone()
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
		return r['price']

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
			g.db.execute('update products set name = ? where barcode = ?', [name, barcode])
			# we should check query success here
		if price != None:
			g.db.execute('update products set price = ? where barcode = ?', [price, barcode])
			# we should check query success here
		if category != None:
			g.db.execute('update products set category = ? where barcode = ?', [category, barcode])
			# we should check query success here
		if picture != None:
			g.db.execute('update products set image = ? where barcode = ?', [picture, barcode])
			# we should check query success here
		return True

	@classmethod
	def all(cls):
		g.db.execute('select barcode from products')
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
		
