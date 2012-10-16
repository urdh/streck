# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class User(object):
	def __init__(self, barcode):
		self.bcode = barcode
		self.db = sqlite.connect(app.config['DATABASE'])
		self.c = self.db.cursor()
	
	def barcode(self):
		return self.bcode

	def id(self):
		if not self.exists():
			return None
		self.c.execute('select id from users where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['id']
	
	def exists(self):
		self.c.execute('select id from users where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r != None
	
	def picture(self):
		if not self.exists():
			return None
		self.c.execute('select image from users where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['image']
	
	def name(self):
		if not self.exists():
			return None
		self.c.execute('select name from users where barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['name']
	
	def debt(self):
		if not self.exists():
			return 0.0;
		self.c.execute('select sum(t.price) as debt from transactions as t, users as u where t.user = u.id and u.barcode = ?', [self.bcode])
		r = self.c.fetchone()
		return r['debt']
	
	def debt_per_category(self):
		if not self.exists():
			return []
		self.c.execute('select c.name as name, sum(t.price) as debt from transactions as t, users as u left join categories as c on t.category = c.id where u.barcode = ? and t.user = u.id group by t.category', [self.bcode])
		return self.c.fetchall()

	def __del__(self):
		self.db.close()
