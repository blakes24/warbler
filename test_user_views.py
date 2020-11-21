"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser.id = 1111
        self.testuser_id = self.testuser.id

        self.u1 = User.signup("u1", "u1@test.com", "password", None)
        self.u1_id = 1234
        self.u1.id = self.u1_id
        self.u2 = User.signup("u2", "u2@test.com", "password", None)
        self.u2_id = 5678
        self.u2.id = self.u2_id

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_signup(self):
        """Can user sign up?"""

        with self.client as c:
            resp = c.post("/signup", data={"username":"testyuser",
                                    "email":"testy@test.com",
                                    "password":"testyuser",
                                    "image_url":None}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testyuser', html)

    def test_login(self):
        """Can user log in?"""

        with self.client as c:
            resp = c.post("/login", data={"username":"testuser", "password":"testuser"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)

    def test_logout(self):
        """Can user log out?"""

        # change the session to mimic logging in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have been logged out.', html)

    def test_list_users(self):
        """Does it display a list of users?"""

        with self.client as c:

            resp = c.get("/users", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="card user-card">', html)

    def test_delete_user(self):
        """Does it delete the user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('User Deleted', html)

    def test_users_show(self):
        """Does it display a user detail page?"""

        with self.client as c:
            resp = c.get('/users/1111', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.testuser.username}</h4>', html)

    def setup_followers(self):
      
        f1 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2])
        db.session.commit()

    def test_following(self):
        """Does it show list of people this user is following?"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@u2', html)
            self.assertNotIn('@u1', html)

    def test_add_follow(self):
        """Can user follow another user?"""

        self.setup_followers()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/follow/{self.u1_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@u1', html)

    def test_followers(self):
        """Does it show list of followers?"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@u1', html)
            self.assertNotIn('@u2', html)

    def test_stop_following(self):
        """Can a user stop following someone?"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/users/stop-following/{self.u2_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('@u2', html)

    def test_add_follow_logged_out(self):
        """Can unauthenticated user follow another user?"""

        self.setup_followers()
        
        with self.client as c:
            resp = c.post(f"/users/follow/{self.u1_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def setup_likes(self):
      
        m1 = Message(id=999, text="testing m1", user_id=self.u1_id)
        m2 = Message(id=888, text="testing m2", user_id=self.u1_id)
        m3 = Message(id=777, text="testing m3", user_id=self.u1_id)

        db.session.add_all([m1,m2,m3])
        db.session.commit()

        like = Likes(user_id=self.testuser_id, message_id=999)
        db.session.add(like)
        db.session.commit()

    def test_show_likes(self):
        """Does it show list of liked messages?"""

        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/likes", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testing m1', html)

    def test_add_like(self):
        """Can user like a message?"""

        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/users/add_like/888", follow_redirects=True)

            likes = Likes.query.filter(Likes.message_id == 888).first()

            self.assertEqual(resp.status_code, 201)
            self.assertEqual(likes.message_id, 888)

    def test_un_like(self):
        """Can user unlike a message?"""

        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/users/un_like/999", follow_redirects=True)

            likes = Likes.query.filter(Likes.message_id == 999).all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 0)
            
    def test_add_like_logged_out(self):
        """Can an unauthenticated user like a message?"""

        self.setup_likes()

        with self.client as c:

            resp = c.post(f"/users/add_like/888", follow_redirects=True)
            html = resp.get_data(as_text=True)


            likes = Likes.query.filter(Likes.message_id == 888).all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 0)
            self.assertIn('Access unauthorized.', html)