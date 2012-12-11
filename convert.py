#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '0.2.1'

import sys, os, glob, ConfigParser, StringIO, csv
from datetime import datetime
from streck import app
from flask import g
import streck.models
from streck.models import User, Product

def parse_inilike_file(f):
	ret = {}
	cp = ConfigParser.ConfigParser()
	cp.readfp(StringIO.StringIO("[dummy]\n" + open(f).read()))
	for item in cp.items('dummy'):
		ret[item[0]] = unicode(item[1], "UTF-8")
	return ret

def find_category_id(catname):
	cats = Product.categories()
	category = 2
	for cat in cats:
		if cat[1] == catname:
			category = cat[0]
			break
	return category

def import_users(userpath):
	users = glob.iglob(os.path.join(userpath, '*/'))
	for user in users:
		userinfo = os.path.join(user, 'user-details.txt')
		data = parse_inilike_file(userinfo)
		active = True
		if data['id'].find('-EJ-BETALT') != -1:
			data['id'] = data['id'].replace('-EJ-BETALT','')
			active = False
		u = User.add(data['id'], data['name'], ('oldimg-%s' % data['image']))
		if u == None or not u.exists():
			print 'Could not add user "%s"!' % data['name']
			continue
		if not active:
			u.disable()

def import_products(productpath):
	products = glob.iglob(os.path.join(productpath, '*/'))
	cats = Product.categories()
	for product in products:
		productinfo = os.path.join(product, 'product-details.txt')
		data = parse_inilike_file(productinfo)
		category = find_category_id(data['type'])
		p = Product.add(data['id'], data['name'], data['price'], category, ('oldimg-%s' % data['image']))
		if p == None or not p.exists():
			print 'Could not add product "%s"!' % data['name']
			continue

def import_transactions(userpath):
	users = glob.iglob(os.path.join(userpath, '*/'))
	for user in users:
		history = os.path.join(user, 'history.txt')
		data = csv.reader(open(history, 'r'), dialect='excel-tab')
		for line in data:
			if len(line) < 4:
				continue
			time = datetime.fromtimestamp(int(line[0])/1000)
			flag = int(line[1])
			u = User(line[2])
			if flag == 0:
				p = Product(line[3])
				amt = float(line[4])
				g.db.execute('insert into transactions values (null, ?, ?, ?, ?, ?)', [time, u.id(), p.id(), amt, 'converted'])
				print '%s bought "%s"!' % (u.name(), p.name())
				continue
			elif flag == 2:
				amt = float(line[3])
				g.db.execute('insert into transactions values (null, ?, ?, ?, ?, ?)', [time, u.id(), Product(None).id(), -amt, 'converted pay'])
				print '%s paid debt!' % u.name()
			else:
				print 'Unknown flag %s' % flag
	# tab-separated, columns are:
	# timestamp flag user-barcode, product-barcode/paid amount, price, type
	# flag is *probably* 0 for buying and 2 for paying

if __name__ == '__main__':
	ctx = app.test_request_context()
	ctx.push()
	streck.models.setup_db()
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
	ctx.pop()
	sys.exit(0)
