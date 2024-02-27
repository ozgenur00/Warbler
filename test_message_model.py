"""Message Model Tests."""


import os 
from unittest import TestCase
from datetime import datetime
from models import db, User, Message

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'
from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Model for Messages"""

    def setUp(self):
        db.drop_all()
        db.create_all()


        u = User.signup("testuser", "test@test.com", "passsword", None)
        uid = 1111
        u.id = uid

        db.session.commit()

        self.u = User.query.get(uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def __repr__(self):
        return f"Message #{self.id}: {self.text}, User {self.user_id}>"
    
    def test_message_model(self):

        m = Message(
            text="a warble",
            user_id=self.u.id
        )

        db.session.add(m)
        db.session.commit()

        #user should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "a warble")

    def test_message_user_relationship(self):

        m = Message(
            text="Test user relationship",
            user_id=self.u.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user.id, self.u.id)

    def test_user_messages_access(self):
        m = Message(
            text="Accessing user messages",
            user_id=self.u.id
        )
        db.session.add(m)
        db.session.commit()

        self.assertIn(m, self.u.messages)

    def test_invalid_message_save(self):
        m = Message(user_id=self.u.id)
        db.session.add(m)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_message_length_validation(self):
        long_text = "a" * 141
        m = Message(text=long_text, user_id=self.u.id)
        db.session.add(m)
        with self.assertRaises(Exception):
            db.session.commit()

    