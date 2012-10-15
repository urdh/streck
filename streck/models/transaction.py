# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Producs(object):
	def __init__(self, user, product=None, price=None, undo=False, paid=False):
		self.user = user
		self.prod = product
		self.price = price
		if undo:
			self.special = 'undo'
		if paid:
			self.special = 'paid'

	def perform(self):
		pass
