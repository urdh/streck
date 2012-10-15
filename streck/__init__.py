# -*- coding: utf-8 -*-
__version__ = '0.1'

from flask import Flask
app = Flask('streck')
app.config['DATABASE'] = './streck.db'
app.config['PAID_BARCODE'] = 'BETALT'
app.config['UNDO_BARCODE'] = 'undo'
app.config['LOGOUT_BARCODE'] = 'log out'

import streck.models
import streck.controller
