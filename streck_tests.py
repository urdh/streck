#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import tempfile
from streck import app
import streck.models

class GenericStreckTestCase(unittest.TestCase):
    """ Generic test case class, handling database setup. """

    def setUp(self):
        """ Set up test case.

        Creates a temporary SQLite database and fills it according to the schema.
        """
        self.db_fd, streck.app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = streck.app.test_client()
        # Fill database
        streck.models.init_db()

    def tearDown(self):
        """ Tear down test case. """
        os.close(self.db_fd)
        os.unlink(streck.app.config['DATABASE'])


class UserModelTests(GenericStreckTestCase):
    """ Test the :class:User model and controller. """
    TESTUSER = dict(barcode='jdoe', name='John Doe')

    def add_user(self, barcode, name):
        """ Helper function for adding a user to the database. """
        return self.app.post('/admin/user/add', data=dict(
            barcode=barcode,
            name=name
        ), follow_redirects=True)

    def test_missing_user(self):
        """ Test accessing nonexistent users. """
        # Access a nonexistent user
        rv = self.app.get('/user/nobody', follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

    def test_create_user(self):
        """ Test creating users through the admin interface. """
        # Create user
        rv = self.add_user(self.TESTUSER['barcode'], self.TESTUSER['name'])
        assert b'Användaren &#34;%s&#34; tillagd.' % self.TESTUSER['name']
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).exists()

        # Create already existing user
        self.add_user(self.TESTUSER['barcode'], self.TESTUSER['name'])
        rv = self.add_user(self.TESTUSER['barcode'], self.TESTUSER['name'])
        assert b'Användarens ID är ej unikt!' in rv.data

    def test_update_user(self):
        """ Test updating users through the admin interface. """
        new_user_name = 'Joe'
        self.add_user(self.TESTUSER['barcode'], self.TESTUSER['name'])

        # Update a user
        rv = self.app.post('/admin/user/%s/update' % self.TESTUSER['barcode'], data=dict(
            name=new_user_name
        ), follow_redirects=True)
        assert new_user_name in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).name() == new_user_name

        # Update a nonexistent user
        rv = self.app.post('/admin/user/nobody/update', data=dict(
            name='Irrelevant'
        ), follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

    def test_user_disabling(self):
        """ Test disabling and enabling users through the admin interface. """
        self.add_user(self.TESTUSER['barcode'], self.TESTUSER['name'])

        # Disable a user
        rv = self.app.get('/admin/user/%s/disable' % self.TESTUSER['barcode'], follow_redirects=True)
        assert b'Användaren är nu avstängd!' in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).disabled()

        # Disable a user again
        rv = self.app.get('/admin/user/%s/disable' % self.TESTUSER['barcode'], follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).disabled()

        # Enable a user
        rv = self.app.get('/admin/user/%s/enable' % self.TESTUSER['barcode'], follow_redirects=True)
        assert b'Användaren är inte längre avstängd!' in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert (not streck.models.user.User(self.TESTUSER['barcode']).disabled())

        # Enable a user again
        rv = self.app.get('/admin/user/%s/enable' % self.TESTUSER['barcode'], follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert (not streck.models.user.User(self.TESTUSER['barcode']).disabled())


# Run tests
if __name__ == '__main__':
    unittest.main()
