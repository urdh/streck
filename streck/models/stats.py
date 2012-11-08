# -*- coding: utf-8 -*-
import sqlite3
from streck.models.user import *
from flask import g

class Stats(object):
	@classmethod
	def top_product(cls):
		g.db.execute('select p.id, p.name, t.product, count(t.product) as c from products as p, transactions as t where p.id = t.product group by t.product order by c desc limit 1')
		r = g.db.fetchone()
		return (r['name'], r['c'])

	@classmethod
	def top_user_debt(cls):
		users = User.all()
		users.sort(key=lambda u: u.debt(), reverse=True)
		return users[0]

	@classmethod
	def top_user_total(cls):
		g.db.execute('select sum(t.price) as s, u.* from transactions as t left join users as u on u.id = t.user where t.price > 0 group by t.user order by s desc limit 1')
		r = g.db.fetchone()
		return (r['name'], r['s'])

	@classmethod
	def timeseries(cls):
		g.db.execute('select sum(t.price) as total, date(t.added) as day from transactions as t where t.price > 0 group by day order by day;')
		return [(r['day'], r['total']) for r in g.db.fetchall()]

	@classmethod
	def total_four_weeks(cls):
		g.db.execute('select sum(t.price) as total from transactions as t where t.price > 0 and date(t.added) > date("now","-28 days");')
		r = g.db.fetchone()
		return r['total']

