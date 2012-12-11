# -*- coding: utf-8 -*-
__version__ = '0.2.1'

from flask import Flask
app = Flask('streck')
app.config['VERSION'] = __version__
app.config['DATABASE'] = './streck/streck.db'
app.config['PAID_BARCODE'] = 'BETALT'
app.config['UNDO_BARCODE'] = 'undo'
app.config['LOGOUT_BARCODE'] = 'log out'
app.config['UPLOAD_FOLDER'] = './pictures/'
app.secret_key = '\xbe\xb8_i\xbe\xe7{\xd0\xb8\xb6\x9b\xb3\x8c#\xc4\x81\x8bZ\x994cEcf'

import streck.models
import streck.controller
