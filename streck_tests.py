#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from streck import app

class StreckTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, streck.app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = streck.app.test_client()
        # Fill database
        self.db = sqlite3.connect(app.config['DATABASE'])
        with self.app.open_resource('schema.sql', mode='r') as f:
            self.db.cursor().executescript(f.read())
        self.db.commit()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
