"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id



            resp = c.post("/messages/new", data={"text": "Hello"})


            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_following_pages_access(self):

        with self.client as c:
            #teste access when logged out
            response = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            self.assertIn("Access unauthorized.", response.get_data(as_text=True))

            #log in
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            #test access when logged in
            response = c.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(response.status_code, 200)


    def test_add_message(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        # add a message
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertIn("Hello", resp.get_data(as_text=True))

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_logged_out(self):

        resp = self.client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
        self.assertIn("Access unauthorized.", resp.get_data(as_text=True))
        self.assertEqual(Message.query.count(), 0)

    def test_edit_profile_access(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = c.get("/users/profile", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Edit Your Profile", response.get_data(as_text=True))

        # Test logged out
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            response = c.get("/users/profile", follow_redirects=True)
            self.assertNotIn("Edit Your Profile", response.get_data(as_text=True))
            self.assertIn("Access unauthorized.", response.get_data(as_text=True))


    def test_add_message_form_access_logged_out(self):
        with self.client as c:
            response = c.get("/messages/new", follow_redirects=True)
            self.assertNotIn("Add my message", response.get_data(as_text=True))
            self.assertIn("Access unauthorized.", response.get_data(as_text=True))


