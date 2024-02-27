"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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

    def test_repr(self):
        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")
        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")

    def test_is_following(self):
        u1 = User(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD")
        u2 = User(email="test2@test.com", username="testuser2", password="HASHED_PASSWORD")
        db.session.add_all([u1, u2])
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    
    def test_is_not_following(self):
        u1 = User(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD")
        u2 = User(email="test2@test.com", username="testuser2", password="HASHED_PASSWORD")
        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    def test_is_followed_by(self):
        u1 = User(email="test1@test.com", username="testuser1", password="HASHED_PASSWORD")
        u2 = User(email="test2@test.com", username="testuser2", password="HASHED_PASSWORD")
        db.session.add_all([u1, u2])
        db.session.commit()

        u2.followers.append(u1)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def test_user_signup(self):
        image_url = "/static/images/default-pic.png"
        u = User.signup("newuser", "newuser@test.com", "password", image_url)
        db.session.commit()

        #verify user was created
        self.assertIsNotNone(u.id)
        self.assertEqual(u.username, "newuser")
        self.assertEqual(u.email, "newuser@test.com")
        self.assertNotEqual(u.password, "password")
        self.assertEqual(u.image_url, image_url)

        #fetch the user from the database to ensure they were correctly added
        fetched_user = User.query.filter_by(username="newuser").first()
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.username, u.username)

    def test_user_authenticate_success(self):
        User.signup("authuser", "auth@test.com", "password", "/static/images/default-pic.png")
        db.session.commit()

        user = User.authenticate("authuser", "password")
        self.assertIsNot(user, False)

    def test_user_authenticate_invalid_username(self):
        User.signup("authuser", "auth@test.com", "password", "/static/images/default-pic.png")
        db.session.commit()

        self.assertFalse(User.authenticate("wronguser", "password"))

    def test_user_authenticate_invalid_password(self):
        User.signup("authuser", "auth@test.com", "password", "/static/images/default-pic.png")
        db.session.commit()

        self.assertFalse(User.authenticate("authuser", "wrongpassword"))

