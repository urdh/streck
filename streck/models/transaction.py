# -*- coding: utf-8 -*-
import sqlite3
from streck.models.user import *
from streck.models.product import *
from flask import g

class Transaction(object):
	def __init__(self, user, product=None, price=None, undo=False, paid=False):
		u = User(user)
		self.user = u.id()
		p = Product(product)
		self.product = p.id()
		self.price = p.price() if price == None else price
		self.special = ''
		if u.reverse:
			self.price = -self.price
		if undo:
			self.special = 'undo'
		if paid:
			self.special = 'paid'
			self.price = -u.debt()

	def perform(self):
		if self.special == 'undo':
			g.db.execute('delete from transactions where id = (select id from transactions where user = ? order by id desc limit 1)', [self.user])
		else:
			g.db.execute('insert into transactions values (null, datetime("now"), ?, ?, ?, ?)', [self.user, self.product, self.price, self.special])
		# we should check query success here
		return True
