# -*- coding: utf-8 -*-
import sqlite3
from flask import flash, g

class User(object):
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
	
	def debt(self):
		pass
	
	def debt_per_category(self):
		return [{'name': 'test', 'debt': 4.53}]
