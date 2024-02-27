"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User
from app import session

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    @classmethod
    def setUpClass(cls):
        """Do before all tests."""

        # Create all tables in the test database
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Do after all tests."""

        # Drop all tables in the test database
        db.drop_all()
        db.session.commit()

    def setUp(self):
        """Do before each test."""

        # Clear any existing data
        User.query.delete()

        # Add sample data
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser", email="test@test.com", password="password", image_url=None)
        self.testuser_id = 888
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Do after each test."""

        db.session.rollback()

    def test_user_login(self):
        with self.client as c:
            # Test successful login
            response = c.post("/login", data={"username": "testuser", "password": "password"}, follow_redirects=True)
            self.assertIn("Hello, testuser!", response.get_data(as_text=True))

            # Test failed login
            response = c.post("/login", data={"username": "testuser", "password": "wrongpassword"}, follow_redirects=True)
            self.assertIn("Invalid credentials.", response.get_data(as_text=True))

    def test_profile_access(self):
    # Test access to own profile when logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(response.status_code, 200)

    # Test access to another user's profile when logged out
        with self.client as c:
            response = c.get("/users/12345", follow_redirects=True) 


    def test_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        # Perform the logout
            response = c.get("/logout", follow_redirects=True)
            self.assertIn("You have successfully logged out.", response.get_data(as_text=True))

            with c.session_transaction() as sess:
                self.assertNotIn(CURR_USER_KEY, sess, "User ID should not be in session after logout")
