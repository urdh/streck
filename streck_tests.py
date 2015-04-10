#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest
import tempfile
from StringIO import StringIO
from binascii import unhexlify
from flask import g
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


class ProductModelTests(GenericStreckTestCase):
    """ Test the :class:Product model and controller. """
    IMAGE=b''.join([
            b'89504e470d0a1a0a0000000d4948445200000001000000010100000000376ef9',
            b'240000001049444154789c626001000000ffff03000006000557bfabd4000000',
            b'0049454e44ae426082'
          ])
    TESTPRODUCT1 = dict(barcode='0012345678905', name='Product 1', price=10.0)
    TESTPRODUCT2 = dict(barcode='4011200296903', name='Product 2', price=7.5)
    CATEGORIES = {1: b'Öl', 2: b'Ickeöl'} # These are hardcoded :(

    def add_product(self, product_dict, category):
        """ Helper function for adding a user to the database. """
        return self.app.post('/admin/product/add', data=dict(
            barcode=product_dict['barcode'],
            name=product_dict['name'],
            price=product_dict['price'],
            category=category
        ), follow_redirects=True)

    def test_arrival_page(self):
        """ Test the product/user arrival page using a product. """
        self.add_product(self.TESTPRODUCT1, 1)

        # Existing product
        rv = self.app.post('/user', data=dict(barcode=self.TESTPRODUCT1['barcode']), follow_redirects=True)
        assert self.TESTPRODUCT1['name'] in rv.data

        # Nonexistent product (albeit for incorrect requests)
        rv = self.app.post('/product', data=dict(barcode='nothing'), follow_redirects=True)
        assert b'Produkten eller användaren existerar inte!' in rv.data

    def test_product_info(self):
        """ Test accessing users. """
        self.add_product(self.TESTPRODUCT1, 1)
        self.add_product(self.TESTPRODUCT2, 2)

        # Access products
        rv = self.app.get('/product/%s' % self.TESTPRODUCT1['barcode'], follow_redirects=True)
        assert self.TESTPRODUCT1['name'] in rv.data
        assert self.CATEGORIES[1] in rv.data
        rv = self.app.get('/product/%s' % self.TESTPRODUCT2['barcode'], follow_redirects=True)
        assert self.TESTPRODUCT2['name'] in rv.data
        assert self.CATEGORIES[2] in rv.data

        # Access a nonexistent product
        rv = self.app.get('/product/nothing', follow_redirects=True)
        assert b'Produkten existerar inte!' in rv.data

    def test_create_product(self):
        """ Test creating products through the admin interface. """
        # Create product
        rv = self.add_product(self.TESTPRODUCT1, 1)
        assert b'Produkten &#34;%s&#34; tillagd.' % self.TESTPRODUCT1['name'] in rv.data
        with app.test_request_context():
            app.preprocess_request()
            product = streck.models.product.Product(self.TESTPRODUCT1['barcode'])
            assert product.exists()
            assert product.price() == self.TESTPRODUCT1['price']
            assert product.category() == (self.CATEGORIES[1]).decode('utf-8')

        # Create another product
        rv = self.add_product(self.TESTPRODUCT2, 2)
        assert b'Produkten &#34;%s&#34; tillagd.' % self.TESTPRODUCT2['name'] in rv.data
        with app.test_request_context():
            app.preprocess_request()
            product = streck.models.product.Product(self.TESTPRODUCT2['barcode'])
            assert product.exists()
            assert product.price() == self.TESTPRODUCT2['price']
            assert product.category() == (self.CATEGORIES[2]).decode('utf-8')

        # Create already existing product
        rv = self.add_product(self.TESTPRODUCT1, 1)
        assert b'Produktens ID är ej unikt!' in rv.data

        # Create already existing product with different category
        rv = self.add_product(self.TESTPRODUCT1, 2)
        assert b'Produktens ID är ej unikt!' in rv.data

    def test_update_product(self):
        """ Test updating products through the admin interface. """
        new_name = 'Cheaper Product'
        new_price = 0.5
        self.add_product(self.TESTPRODUCT1, 1)

        # Update product name
        rv = self.app.post('/admin/product/%s/update' % self.TESTPRODUCT1['barcode'], data=dict(
            name=new_name
        ), follow_redirects=True)
        assert new_name in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.product.Product(self.TESTPRODUCT1['barcode']).name() == new_name

        # Update product price
        rv = self.app.post('/admin/product/%s/update' % self.TESTPRODUCT1['barcode'], data=dict(
            price=new_price
        ), follow_redirects=True)
        assert str(new_price) in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.product.Product(self.TESTPRODUCT1['barcode']).price() == new_price

        # Update product category
        rv = self.app.post('/admin/product/%s/update' % self.TESTPRODUCT1['barcode'], data=dict(
            category=2
        ), follow_redirects=True)
        assert self.CATEGORIES[2] in rv.data
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.product.Product(self.TESTPRODUCT1['barcode']).category() == (self.CATEGORIES[2]).decode('utf-8')

        # Update a nonexistent product
        rv = self.app.post('/admin/product/nothing/update', data=dict(
            name='Irrelevant'
        ), follow_redirects=True)
        assert b'Produkten existerar inte!' in rv.data

    def test_picture(self):
        """ Test uploading a product picture through the admin interface. """
        self.add_product(self.TESTPRODUCT1, 1)

        # Test the default picture
        with app.test_request_context():
            app.preprocess_request()
            new_picture = streck.models.product.Product(self.TESTPRODUCT1['barcode']).picture()
        assert new_picture == '../img/NoneProduct.png'

        # Update a user
        rv = self.app.post('/admin/product/%s/update' % self.TESTPRODUCT1['barcode'], data=dict(
            picture=(StringIO(unhexlify(self.IMAGE)), 'picture.png')
        ), buffered=True, follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            new_picture = streck.models.product.Product(self.TESTPRODUCT1['barcode']).picture()
        assert new_picture != '../img/NoneProduct.png'

        # Compare the resulting picture
        rv = self.app.get('/images/%s' % new_picture)
        assert rv.status_code == 200

    def test_admin_product_list(self):
        """ Test loading the administration interface product list. """
        # No products
        rv = self.app.get('/admin/product')
        assert rv.status_code == 200

        # More than 0 products
        self.add_product(self.TESTPRODUCT1, 1)
        self.add_product(self.TESTPRODUCT2, 2)
        rv = self.app.get('/admin/product', follow_redirects=True)
        assert self.TESTPRODUCT1['name'] in rv.data
        assert self.TESTPRODUCT2['name'] in rv.data

    def test_admin_product_info(self):
        """ Test loading a single product in the administration interface. """
        self.add_product(self.TESTPRODUCT1, 1)

        # Missing product
        rv = self.app.get('/admin/product/nothing', follow_redirects=True)
        assert b'Produkten existerar inte!' in rv.data

        # Existing product
        rv = self.app.get('/admin/product/%s' % self.TESTPRODUCT1['barcode'], follow_redirects=True)
        assert self.TESTPRODUCT1['name'] in rv.data


class TransactionModelTests(GenericStreckTestCase):
    """ Test the :class:Transaction model and controller. """

    def setUp(self):
        """ Set up test case.

        Inserts a product and a user into the database
        """
        GenericStreckTestCase.setUp(self)
    	with app.test_request_context():
            app.preprocess_request()
            streck.models.product.Product.add('0012345678905', 'The Product', 5.0, 1, '../img/NoneProduct.png')
            streck.models.user.User.add('john', 'User 1', '../img/NoneUser.png')
            streck.models.user.User.add('jane', 'User 2', '../img/NoneUser.png').disable()

    def test_buy(self):
        """ Test buying something. """
        # Make sure we can buy the product
        self.app.post('/user/john/buy', data=dict(barcode='0012345678905'), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('john').debt() == 5.0

        # Make sure it appears on the user page
        rv = self.app.get('/user/john', follow_redirects=True)
        assert b'The Product' in rv.data

    def test_undo(self):
        """ Test undoing something. """
        # Hack a product into the database so we have something to undo
        with app.test_request_context():
            app.preprocess_request()
            streck.models.transaction.Transaction('john', '0012345678905', 5.0).perform()
            assert streck.models.user.User('john').debt() == 5.0

        # Make sure we can undo the transaction
        self.app.post('/user/john/buy', data=dict(barcode=app.config['UNDO_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('john').debt() == 0.0

        # Make sure it appears on the user page
        rv = self.app.get('/user/john', follow_redirects=True)
        assert b'The Product' not in rv.data

    def test_paid(self):
        """ Test resetting a user debt. """
        # Make sure we have a debt
        with app.test_request_context():
            app.preprocess_request()
            streck.models.transaction.Transaction('john', '0012345678905', 5.0).perform()
            streck.models.transaction.Transaction('john', '0012345678905', 5.0).perform()
            assert streck.models.user.User('john').debt() == 10.0

        # Test paying off the debt
        self.app.post('/user/john/buy', data=dict(barcode=app.config['PAID_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('john').debt() == 0.0

    def test_buy_disabled(self):
        """ Test buying something using a disabled user. """
        # Make sure we can't buy the product
        self.app.post('/user/jane/buy', data=dict(barcode='0012345678905'), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('jane').debt() == 0.0

        # Make sure it appears on the user page
        rv = self.app.get('/user/jane', follow_redirects=True)
        assert b'The Product' not in rv.data

    def test_undo_disabled(self):
        """ Test undoing a transaction using a disabled user. """
        # Hack a product into the database so we have something to undo
        with app.test_request_context():
            app.preprocess_request()
            streck.models.transaction.Transaction('jane', '0012345678905', 5.0).perform()
            assert streck.models.user.User('jane').debt() == 5.0

        # Try to undo it
        self.app.post('/user/jane/buy', data=dict(barcode=app.config['UNDO_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('jane').debt() == 5.0

    def test_paid_disabled(self):
        """ Test resetting the debt of a disabled user. """
        # Make sure we have a debt
        with app.test_request_context():
            app.preprocess_request()
            streck.models.transaction.Transaction('jane', '0012345678905', 5.0).perform()
            streck.models.transaction.Transaction('jane', '0012345678905', 5.0).perform()
            assert streck.models.user.User('jane').debt() == 10.0

        # Test paying off the debt
        self.app.post('/user/jane/buy', data=dict(barcode=app.config['PAID_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('jane').debt() == 0.0

    def test_undo_empty(self):
        """ Test undoing the last transaction when there isn't one. """
        # Try to undo it
        self.app.post('/user/john/buy', data=dict(barcode=app.config['UNDO_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('john').debt() == 0.0

    def test_undo_after_paid(self):
        """ Test undoing a transaction when the last one was a debt reset. """
        # Make sure we have a debt, and that it's paid
        with app.test_request_context():
            app.preprocess_request()
            streck.models.transaction.Transaction('john', '0012345678905', 5.0).perform()
            streck.models.transaction.Transaction('john', '0012345678905', 5.0).perform()
            streck.models.transaction.Transaction('john', paid=True).perform()
            assert streck.models.user.User('john').last_paid_id() != -1
            assert streck.models.user.User('john').debt() == 0.0

        # Try to undo
        self.app.post('/user/john/buy', data=dict(barcode=app.config['UNDO_BARCODE']), follow_redirects=True)
        with app.test_request_context():
            app.preprocess_request()
            assert streck.models.user.User('john').debt() == 10.0 # by design apparently?


# TODO: StatsModelTests
# TODO: AdminExportModelTests
# TODO: JobbmatFeatureTests
# TODO: SpecialBarcodeTests

# Run tests
if __name__ == '__main__':
    unittest.main()
