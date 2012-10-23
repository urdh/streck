# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Transaction(object):
	def __init__(self, user, product=None, price=None, undo=False, paid=False):
		u = User(user)
		self.user = u.id()
		p = Product(product)
		self.prod = p.id()
		self.price = p.price() if price == None else price
		self.special = ''
		if undo:
			self.special = 'undo'
		if paid:
			self.special = 'paid'
			self.price = -u.debt()

	def perform(self):
		if self.special == 'undo':
			g.db.execute('delete from transactions order by id desc limit 1')
		else:
			g.db.execute('insert into transactions values (0, datetime("now"), ?, ?, ?, ?)', [self.user, self.product, self.price, self.special])
