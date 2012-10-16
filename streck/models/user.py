# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class User(object):
	def __init__(self, barcode):
		self.bcode = barcode
	
	def barcode(self):
		return self.bcode

	def id(self):
		if not self.exists():
			return None
		g.db.execute('select id from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['id']
	
	def exists(self):
		g.db.execute('select id from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r != None
	
	def picture(self):
		if not self.exists():
			return None
		g.db.execute('select image from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['image']
	
	def name(self):
		if not self.exists():
			return None
		g.db.execute('select name from users where barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['name']
	
	def debt(self):
		if not self.exists():
			return 0.0;
		g.db.execute('select sum(t.price) as debt from transactions as t, users as u where t.user = u.id and u.barcode = ?', [self.bcode])
		r = g.db.fetchone()
		return r['debt']
	
	def debt_per_category(self):
		if not self.exists():
			return []
		g.db.execute('select c.name as name, sum(t.price) as debt from transactions as t, users as u left join categories as c on t.category = c.id where u.barcode = ? and t.user = u.id group by t.category', [self.bcode])
		return g.db.fetchall()
