# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class Producs(object):
	def __init__(self, barcode):
		self.bcode = barcode

	def barcode(self):
		return self.bcode

	def exists(self):
		return True

	def picture(self):
		pass

	def name(self):
		pass

	def price(self):
		pass

	def category(self):
		pass
