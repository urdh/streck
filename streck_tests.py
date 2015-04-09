#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
from streck import app
import streck.models

class StreckTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, streck.app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = streck.app.test_client()
        # Fill database
        streck.models.init_db()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
