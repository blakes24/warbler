"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User.signup(
            email="testy@test.com",
            username="testyuser",
            password="unhashed",
            image_url="img.jpg"
        )
        u.id = 1111
        db.session.add(u)
        db.session.commit()

        u = User.query.get(1111)
        self.u = u

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
        

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # repr should display id, username, and email
        self.assertEqual(f'{u}', f'<User #{u.id}: {u.username}, {u.email}>')

    def test_is_following(self):
        """Does is_following method work?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        u1.following.append(u2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    def test_is_followed_by(self):
        """Does is_followed_by method work?"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        u1.following.append(u2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def test_signup(self):
        """Does signup method create a new user?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="unhashed",
            image_url="img.jpg"
        )

        db.session.add(u)
        db.session.commit()

        # u should display id, username, and email
        self.assertEqual(f'{u}', f'<User #{u.id}: {u.username}, {u.email}>')
        # should not be created missing args
        self.assertRaises(Exception, User.signup, email="test@test.com")
        self.assertRaises(Exception, User.signup, "test2@test.com", '', '', '')
        
    def test_signup_unique(self):
        """Does signup raise error if email/username not unique"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="unhashed",
            image_url="img.jpg"
        )
        u2 = User.signup(
            email="test@test.com",
            username="testuser",
            password="unhashed",
            image_url="img.jpg"
        )

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authenticate_valid(self):
        """Does authentication work?"""

        u = User.authenticate("testyuser", "unhashed")

        # authenticate should return the user 
        self.assertEqual(u, self.u)

    def test_invalid_username(self):
        """Does invalid username fail?"""

        u = User.authenticate("wrong", "unhashed")

        # authenticate should return false
        self.assertNotEqual(u, self.u)
        self.assertFalse(u)

    def test_invalid_password(self):
        """Does invalid username fail?"""

        u = User.authenticate("testyuser", "nope")

        # authenticate should return false
        self.assertNotEqual(u, self.u)
        self.assertFalse(u)
    
        
