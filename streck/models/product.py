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
		return r['c.name']
