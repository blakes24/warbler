import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes

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
        Likes.query.delete()

        u = User.signup(
            email="testy@test.com",
            username="testyuser",
            password="unhashed",
            image_url="img.jpg"
        )
        u.id = 1111

        m = Message(text="Hello")

        u.messages.append(m)
        db.session.add(u)
        db.session.commit()

        u = User.query.get(1111)
        self.u = u

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""
        m = Message(text="testing")
        self.u.messages.append(m)
        db.session.commit()

        self.assertIn(m, self.u.messages)
        self.assertEqual(len(self.u.messages), 2)
        self.assertEqual(m.text, "testing")

    def test_like_message(self):
        """Can a message be added to likes?"""
        user = User.signup("tester2", "t@email.com", "password", None)
        m = Message(text="testing")
        user.messages.append(m)
        self.u.likes.append(m)
        db.session.commit()
        
        self.assertIn(m, self.u.likes)
        self.assertEqual(len(self.u.likes), 1)
