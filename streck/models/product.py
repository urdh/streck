# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Producs(object):
	def __init__(self, barcode):
		self.bcode = barcode
		self.db = sqlite.connect(app.config['DATABASE'])
		self.c = self.db.cursor()

	def barcode(self):
		return self.bcode

	def id(self):
		if not self.exists():
			return None
		self.c.execute('select id from products where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['id']

	def exists(self):
		self.c.execute('select id from products where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r != None

	def picture(self):
		if not self.exists():
			return None
		self.c.execute('select image from products where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['image']

	def name(self):
		if not self.exists():
			return None
		self.c.execute('select name from products where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['name']

	def price(self):
		if not self.exists():
			return None
		self.c.execute('select price from products where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['price']

	def category(self):
		if not self.exists():
			return None
		self.c.execute('select c.name from products p, categories c where p.barcode = ? and c.id = p.category', [self.bcode])
		r = self.c.fetchone()
		return r['c.name']

	def __del__(self):
		self.db.close()
