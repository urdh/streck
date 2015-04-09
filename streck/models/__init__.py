# -*- coding: utf-8 -*-
import sqlite3
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.models.transaction import *
from streck.models.stats import *

# on request init
@app.before_request
def setup_db():
	g._db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES);
	g._db.row_factory = sqlite3.Row
	g.db = g._db.cursor()

@app.teardown_request
def close_db(e):
	g.db.close()
	g._db.commit()
	g._db.close()

# create the database (only used by tests so far)
def init_db():
	with app.app_context():
		setup_db()
		with app.open_resource('schema.sql', mode='r') as f:
			g.db.executescript(f.read())
		g._db.commit()
		close_db(None)
