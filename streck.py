#!/usr/bin/env python
# -*- coding: utf-8 -*-
from streck import app
from streck.models import user, product, transaction

if __name__ == '__main__':
	app.run(debug=True)
