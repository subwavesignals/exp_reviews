import unittest

from server import app
from model import (db, connect_to_db, example_data, User, Review, CriticReview,
                   Game, CurrentGame, Cover, Franchise, Genre, Developer,
                   Platform, Screenshot)

from correlation import pearson
import pull_data
import datetime

class RouteIntegrationTests(unittest.TestCase):
    """Tests for the app routes and URL paths"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config["SECRET_KEY"] = "sjkfvsdgbwiueijqn23ed"
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()

    def tearDown(self):
        db.session.close()
        db.drop_all()

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("Popular with Our Users", result.data)

    def test_login_page(self):
        result = self.client.get("/login")
        self.assertIn("Username:", result.data)
        self.assertIn("Welcome Back", result.data)

    def test_login_success(self):
        result = self.client.post("/login", data={"username": "testo",
                                  "password": "testo"}, follow_redirects=True)
        self.assertIn("Logged in as testo", result.data)
        self.assertNotIn("Username:", result.data)

    def test_login_fail_username(self):
        result = self.client.post("/login", data={"username": "test",
                                  "password": "testo"}, follow_redirects=True)
        self.assertIn("Invalid username", result.data)
        self.assertIn("Username:", result.data)

    def test_login_fail_password(self):
        result = self.client.post("/login", data={"username": "testo",
                                  "password": "test"}, follow_redirects=True)
        self.assertIn("Incorrect password", result.data)
        self.assertIn("Username:", result.data)

    def test_signup_page(self):
        result = self.client.get("/signup")
        self.assertIn("Join EXP", result.data)
        self.assertIn("Email:", result.data)

    def test_signup(self):
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
        self.assertNotIn("Recommended for You", result.data)



class DatabaseTests(unittest.TestCase):
    """Tests for db units (seed methods/user methods) and integration"""

    def setUp(self):
        """Sets up testdb and connects"""
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()
        example_data()

    def tearDown(self):
        """Ends the db session and drops the whole db"""
        db.session.close()
        db.drop_all()
    
    def test_reprs(self):
        """Tests represenation methods for each db class"""
        self.assertEqual(repr(User.query.first()), 
            "<User user_id=1 username=testo email=testo@test.com age=35 " + 
            "gender=nb_gf>")
        self.assertEqual(repr(Review.query.first()), 
            "<Review user_id=1 game_id=1 score=95>")
        self.assertEqual(repr(CriticReview.query.first()), 
            "<CriticReview critic_code=ign game_id=1 score=100>")
        self.assertEqual(repr(Game.query.first()), 
            "<Game game_id=1 name=Testo release_date=" + 
            str(Game.query.first().release_date) + ">")
        self.assertEqual(repr(CurrentGame.query.first()),
            "<CurrentGame game_id=1 user_id=1>")
        self.assertEqual(repr(Cover.query.first()),
            "<Cover cover_id=1 game_id=1 url=///testo.png>")
        self.assertEqual(repr(Franchise.query.first()),
            "<Franchise franchise_id=1 name=Testo Stories>")
        self.assertEqual(repr(Genre.query.first()),
            "<Genre genre_id=1 genre=test>")
        self.assertEqual(repr(Developer.query.first()),
            "<Developer developer_id=1 name=Testo Games>")
        self.assertEqual(repr(Platform.query.first()),
            "<Platform platform_id=1 name=Testo360>")
        self.assertEqual(repr(Screenshot.query.first()),
            "<Screenshot screenshot_id=1 game_id=1 url=///test.png>")

    def test_relationships(self):
        """Tests the relationships between the tables"""
        self.assertEqual(User.query.first().reviews, [Review.query.first()])
        self.assertEqual(User.query.first().currently_playing, [CurrentGame.query.first()])
        self.assertEqual(Game.query.first().reviews, Review.query.all())
        self.assertEqual(Game.query.first().critics, [CriticReview.query.first()])
        self.assertEqual(Game.query.first().franchise, Franchise.query.first())
        self.assertEqual(Game.query.first().covers, [Cover.query.first()])
        self.assertEqual(Game.query.first().genres, [Genre.query.first()])
        self.assertEqual(Game.query.first().developers, [Developer.query.first()])
        self.assertEqual(Game.query.first().platforms, [Platform.query.first()])
        self.assertEqual(Game.query.first().screenshots, [Screenshot.query.first()])

    def test_recommendation(self):
        """Tests the recommendation system"""
        user1 = User.query.filter_by(user_id=1).first()
        user2 = User.query.filter_by(user_id=2).first()
        user3 = User.query.filter_by(user_id=3).first()

        self.assertEqual(user1.recommend(), [2])
        self.assertEqual(user2.recommend(), [1])
        self.assertEqual(user3.recommend(), None)


class PearsonTests(unittest.TestCase):
    """Tests for correlation/pearson"""

    def test_pearson(self):
        """Tests that perfectly matched users have correlation 1.0"""
        match_pairs = [(1,1), (2,2), (3,3), (4,4), (5,5)]
        self.assertEqual(pearson(match_pairs), 1.0)

    def test_anti_pearson(self):
        """Tests that perfectly unmatched users have correlation -1.0"""
        unmatched_pairs = [(1,5), (2,4), (3,3), (4,2), (5,1)]
        self.assertEqual(pearson(unmatched_pairs), -1.0)

    def test_mid_pearson(self):
        """Tests that users with mixed values have expected correlation"""
        mixed_pairs = [(1,5), (2,1), (3,2), (4,4), (5,3)]
        self.assertEqual(pearson(mixed_pairs), -0.1)

    def test_zero_pearson(self):
        """Tests that if the denominator is 0 that correlation is 0.0"""
        pairs = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.assertEqual(pearson(pairs), 0.0)


class PullDataTests(unittest.TestCase):
    """Tests for pull_data"""

    def test_gameURL(self):
        """Gets base game URL and checks request returns something"""
        gameURL = ('https://igdbcom-internet-game-database-v1.p.mashape.com/' + 
        'games/?fields=id%2Cname%2Csummary%2Cstoryline%2Cfranchise%2Cgenres%2C' +
        'first_release_date%2Cvideos%2Ccover%2Cdevelopers%2Cscreenshots&order=' +
        'first_release_date%3Adesc')
        self.assertEqual(pull_data.get_game_url(), gameURL)
        # Removed from regular testing due to the number of games in std. request
        # self.assertIsNotNone(pull_data.make_request(gameURL))

    def test_franchiseURL(self):
        """Gets base franchise URL and checks request returns something"""
        franchiseURL = ('https://igdbcom-internet-game-database-v1.p.mashape.com' +
        '/franchises/?fields=id%2Cname')
        self.assertEqual(pull_data.get_franchise_url(), franchiseURL)
        # Removed from regular testing due to the number of franchises in std. request
        # self.assertIsNotNone(pull_data.make_request(franchiseURL))

    def test_companyURL(self):
        """Gets base company URL and checks request returns something"""
        companyURL = ('https://igdbcom-internet-game-database-v1.p.mashape.com' +
        '/companies/6?fields=name')
        self.assertEqual(pull_data.get_company_url(6), companyURL)
        self.assertIsNotNone(pull_data.make_request(companyURL))

    def test_genreURL(self):
        """Gets base genre URL and checks request returns something"""
        genreURL = ('https://igdbcom-internet-game-database-v1.p.mashape.com' +
        '/genres/?fields=id%2Cname')
        self.assertEqual(pull_data.get_genre_url(), genreURL)
        self.assertIsNotNone(pull_data.make_request(genreURL))

    def test_platformURL(self):
        """Gets base platform URL and checks request returns something"""
        platformURL = ('https://igdbcom-internet-game-database-v1.p.mashape.com' +
        '/platforms/?fields=id%2Cname%2Cgames')
        self.assertEqual(pull_data.get_platform_url(), platformURL)
        self.assertIsNotNone(pull_data.make_request(platformURL))



if __name__ == "__main__":
    unittest.main()