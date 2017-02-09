import unittest

from server import app
from model import db, connect_to_db

class RouteTests(unittest.TestCase):
    """Tests for the app sites"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config["SECRET_KEY"] = "sjkfvsdgbwiueijqn23ed"

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("here eventually", result.data)

    def test_login_page(self):
        result = self.client.get("/login")
        self.assertIn("Username:", result.data)
        self.assertIn("Welcome Back", result.data)

    def test_login(self):
        result = self.client.post("/login", data={"username": "tropikiko",
                                  "password": "kiko"}, follow_redirects=True)
        self.assertIn("Logged in as tropikiko", result.data)
        self.assertNotIn("Username:", result.data)

    def test_signup_page(self):
        result = self.client.get("/signup")
        self.assertIn("Join EXP", result.data)
        self.assertIn("Email:", result.data)

    def test_signup(self):
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        data = {"username": "testing123", "email": "please@work.com",
                "password": "vigenere", "match_password": "vigenere"}
        result = self.client.post("/signup", data=data, follow_redirects=True)
        self.assertIn("Age:", result.data)
        self.assertNotIn("Username:", result.data)

    def test_logout(self):
        with self.client as c:
            with c.session_transaction() as test_session:
                test_session['user_id'] = 1
        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn("Logged out", result.data)
        self.assertIn("here eventually", result.data)


if __name__ == "__main__":
    unittest.main()