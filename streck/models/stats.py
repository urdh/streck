# -*- coding: utf-8 -*-
import sqlite3
from streck.models.user import *
from flask import g
from streck import app

class Stats(object):
	@classmethod
	def top_product(cls):
		g.db.execute('select p.id, p.name, t.product, count(t.product) as c from products as p, transactions as t left join users as u on u.id = t.user where p.id = t.product and u.barcode != ? group by t.product order by c desc limit 1', [app.config['JOBBMAT_BARCODE']])
		r = g.db.fetchone()
		return (r['name'], int(r['c']))

	@classmethod
	def top_user_debt(cls):
		return cls.toplist_user_now()[0]

	@classmethod
	def top_user_total(cls):
		g.db.execute('select sum(t.price) as s, u.* from transactions as t left join users as u on u.id = t.user where t.price > 0 and u.barcode != ? group by t.user order by s desc limit 1', [app.config['JOBBMAT_BARCODE']])
		r = g.db.fetchone()
		return (r['name'], float(r['s']))

	@classmethod
	def timeseries(cls):
  		g.db.execute('select sum(t.price) as total, c.name as category, date(t.added) as day from transactions as t left join categories as c, products as p on p.category = c.id and t.product = p.id left join users as u on u.id = t.user where t.price > 0 and u.barcode != ? group by c.id, day order by day;', [app.config['JOBBMAT_BARCODE']])
		return [(r['day'], r['category'], float(r['total'])) for r in g.db.fetchall()]

	@classmethod
	def total_four_weeks(cls):
		g.db.execute('select sum(t.price) as total from transactions as t left join users as u on u.id = t.user where t.price > 0 and date(t.added) > date("now","-28 days") and u.barcode != ?;', [app.config['JOBBMAT_BARCODE']])
		r = g.db.fetchone()
		return float(r['total'])

	@classmethod
	def toplist_product(cls, category):
		g.db.execute('select p.name as name, count(t.price) as count, sum(t.price) as total from transactions as t left join categories as c, products as p on p.category = c.id and p.id = t.product where c.id = ? group by p.id order by count desc limit 3', [category])
		return [r for r in g.db.fetchall()]

	@classmethod
	def toplist_user(cls, category):
		g.db.execute('select u.name as name, count(t.price) as count, sum(t.price) as total from transactions as t left join categories as c, products as p, users as u on p.category = c.id and p.id = t.product and u.id = t.user where c.id = ? group by u.id order by total desc limit 3', [category])
		return [r for r in g.db.fetchall()]

	@classmethod
	def toplist_user_alltime(cls):
		g.db.execute('select u.name as name, count(t.price) as count, sum(t.price) as total from transactions as t left join categories as c, products as p, users as u on p.category = c.id and p.id = t.product and u.id = t.user group by u.id order by total desc limit 3')
		return [r for r in g.db.fetchall()]

	@classmethod
	def toplist_user_now(cls):
		users = User.all()
		users = [user for user in users if user.barcode() != app.config['JOBBMAT_BARCODE']]
		users.sort(key=lambda u: u.debt(), reverse=True)
		return users[0:3]
