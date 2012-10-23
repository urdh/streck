# -*- coding: utf-8 -*-
import sqlite3
from streck import app
from streck.models.user import *
from streck.models.product import *
from streck.models.transaction import *

# on request init
@app.before_request
def setup_db():
	g._db = sqlite3.connect(app.config['DATABASE']);
	g._db.row_factory = sqlite3.Row
	g.db = g._db.cursor()

@app.teardown_request
def close_db(e):
	g.db.close()
	g._db.commit()
	g._db.close()
