#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '0.1'

import sys, os, glob, ConfigParser, StringIO
from streck.models import User, Product, Transaction
# Need to set up a request contest for werkzeug first

def parse_inilike_file(f):
	ret = {}
	cp = ConfigParser.ConfigParser()
	cp.readfp(StringIO.StringIO("[dummy]\n" + open(f).read()))
	for item in cp.items('dummy'):
		ret[item[0]] = item[1]
	return ret

def import_users(userpath):
	users = glob.iglob(os.path.join(userpath, '*/'))
	for user in users:
		userinfo = os.path.join(user, 'user-details.txt')
		data = parse_inilike_file(userinfo)
		active = True
		if data['id'].find('-EJ-BETALT') != -1:
			data['id'] = data['id'].replace('-EJ-BETALT','')
			active = False
		u = User.add(data['id'], data['name'], None)
		if not u.exists():
			print 'Could not add "%s"!' % data['name']
		if not active:
			u.disable()

def import_products(productpath):
	pass

def import_transactions(userpath):
	pass

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('Usage: ./convert.py <old data path>')
		sys.exit(1)
	if not os.path.exists(sys.argv[1]):
		sys.stderr.write('Invalid path!')
		sys.exit(2)
	userpath = os.path.join(sys.argv[1], 'users/')
	productpath = os.path.join(sys.argv[1], 'products/')
	resourcepath = os.path.join(sys.argv[1], 'resources/')
	if not os.path.exists(userpath) or not os.path.exists(productpath) or not os.path.exists(resourcepath):
		sys.stderr.write('No data found!')
		sys.exit(3)
	import_users(userpath)
	import_products(productpath)
	import_transactions(userpath)
	sys.exit(0)
