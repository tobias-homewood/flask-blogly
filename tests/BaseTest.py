import unittest
from flask import url_for, Flask
from flask_testing import TestCase
from app import create_app, db, connect_db, User

class BaseTest(TestCase):
    def create_app(self):
        self.app = create_app(db_url='postgresql:///blogly_test', testing=True)
        return self.app

    def setUp(self):
        connect_db(self.app)
        with self.app.app_context():
            db.create_all()
            # create a user
            db.session.add(User(first_name="Test", last_name="User", image_url="https://www.example.com"))
            db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_setup(self):
        self.assertTrue(True)