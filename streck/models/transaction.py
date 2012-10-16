# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Producs(object):
	def __init__(self, user, product=None, price=None, undo=False, paid=False):
		u = User(user)
		self.user = u.id()
		p = Product(product)
		self.prod = p.id()
		self.price = price || p.price()
		self.special = ''
		if undo:
			self.special = 'undo'
		if paid:
			self.special = 'paid'
			self.price = -u.debt()
		self.db = sqlite.connect(app.config['DATABASE'])
		self.c = self.db.cursor()

	def perform(self):
		if self.special == 'undo':
			self.c.execute('delete from transactions order by id desc limit 1')
		else:
			self.c.execute('insert into transactions values (0, datetime("now"), ?, ?, ?, ?)', [self.user, self.product, self.price, self.special])

	def __del__(self):
		self.db.commit()
		self.db.close()
