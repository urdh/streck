#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest
import tempfile
from StringIO import StringIO
from binascii import unhexlify
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
        # Get a temporary directory for uploads
        streck.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

    def tearDown(self):
        """ Tear down test case. """
        os.close(self.db_fd)
        os.unlink(streck.app.config['DATABASE'])
        shutil.rmtree(streck.app.config['UPLOAD_FOLDER'])


class StaticPageTests(GenericStreckTestCase):
    """ Test all the pretty static pages.

    This is mostly for coverage, but we do look at the status code.

    TODO: test for some vital content on these pages?
    """

    def test_admin_index(self):
        """ The admin landing page. """
        rv = self.app.get('/admin')
        assert rv.status_code == 200

    def test_landing(self):
        """ The main page. """
        rv = self.app.get('/')
        assert rv.status_code == 200

    def test_error(self):
        """ The error page.

        Note: this is not the 404/error code handler!

        TODO: consider expecting an error code here instead
        """
        rv = self.app.get('/error')
        assert rv.status_code == 200


class UserModelTests(GenericStreckTestCase):
    """ Test the :class:User model and controller. """
    IMAGE=b''.join([
            b'89504e470d0a1a0a0000000d4948445200000001000000010100000000376ef9',
            b'240000001049444154789c626001000000ffff03000006000557bfabd4000000',
            b'0049454e44ae426082'
          ])
    TESTUSER = dict(barcode='jdoe', name='John Doe')

    def add_user(self, user_dict):
        """ Helper function for adding a user to the database. """
        return self.app.post('/admin/user/add', data=dict(
            barcode=user_dict['barcode'],
            name=user_dict['name']
        ), follow_redirects=True)

    def test_user_info(self):
        """ Test accessing users. """
        self.add_user(self.TESTUSER)

        # Access a normal user
        rv = self.app.get('/user/%s' % self.TESTUSER['barcode'], follow_redirects=True)
        assert self.TESTUSER['name'] in rv.data

        # Access a disabled user
        self.app.get('/admin/user/%s/disable' % self.TESTUSER['barcode'], follow_redirects=True)
        rv = self.app.get('/user/%s' % self.TESTUSER['barcode'], follow_redirects=True)
        assert b'<h1>Nej!</h1>' in rv.data

        # Access a nonexistent user
        rv = self.app.get('/user/nobody', follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

    def test_create_user(self):
        """ Test creating users through the admin interface. """
        # Create user
        rv = self.add_user(self.TESTUSER)
        assert b'Användaren &#34;%s&#34; tillagd.' % self.TESTUSER['name'] in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).exists()

        # Create already existing user
        rv = self.add_user(self.TESTUSER)
        assert b'Användarens ID är ej unikt!' in rv.data

    def test_update_user(self):
        """ Test updating users through the admin interface. """
        new_user_name = 'Joe'
        self.add_user(self.TESTUSER)

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
        self.add_user(self.TESTUSER)

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
            assert streck.models.user.User(self.TESTUSER['barcode']).enabled()

        # Enable a user again
        rv = self.app.get('/admin/user/%s/enable' % self.TESTUSER['barcode'], follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User(self.TESTUSER['barcode']).enabled()

        # Disable a nonexistent user
        rv = self.app.get('/admin/user/nobody/disable', follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

        # Enable a nonexistent user
        rv = self.app.get('/admin/user/nobody/enable', follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

    def test_picture(self):
        """ Test uploading a user picture through the admin interface. """
        self.add_user(self.TESTUSER)

        # Test the default picture
        with app.test_request_context():
            app.preprocess_request()
            new_picture = streck.models.user.User(self.TESTUSER['barcode']).picture()
        assert new_picture == '../img/NoneUser.png'

        # Update a user
        rv = self.app.post('/admin/user/%s/update' % self.TESTUSER['barcode'], data=dict(
            picture=(StringIO(unhexlify(self.IMAGE)), 'picture.png')
        ), buffered=True, follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            new_picture = streck.models.user.User(self.TESTUSER['barcode']).picture()
        assert new_picture != '../img/NoneUser.png'

        # Compare the resulting picture
        rv = self.app.get('/images/%s' % new_picture)
        assert rv.status_code == 200

    def test_admin_user_list(self):
        """ Test loading the administration interface user list. """
        # No users
        rv = self.app.get('/admin/user')
        assert rv.status_code == 200

        # More than 0 users
        self.add_user(self.TESTUSER)
        rv = self.app.get('/admin/user', follow_redirects=True)
        assert self.TESTUSER['name'] in rv.data

    def test_admin_user_info(self):
        """ Test loading a single user in the administration interface. """
        self.add_user(self.TESTUSER)

        # Missing user
        rv = self.app.get('/admin/user/nobody', follow_redirects=True)
        assert b'Användaren existerar inte!' in rv.data

        # Existing user
        rv = self.app.get('/admin/user/%s' % self.TESTUSER['barcode'], follow_redirects=True)
        assert self.TESTUSER['name'] in rv.data


# TODO: TransactionModelTests
# TODO: ProductModelTests
# TODO: StatsModelTests
# TODO: AdminExportModelTests

# Run tests
if __name__ == '__main__':
    unittest.main()
