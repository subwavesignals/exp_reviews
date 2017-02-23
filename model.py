"""Models and database function for EXP Reviews"""

from flask_sqlalchemy import SQLAlchemy
import datetime
import correlation

db = SQLAlchemy()

################################################################################
# Model definitions

class User(db.Model):
    """User of EXP Reviews"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    fname = db.Column(db.String(16))
    lname = db.Column(db.String(32))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(5))

    def __repr__(self):
        """Provide helpful output when printed"""

        u = "<User user_id=%s username=%s email=%s age=%s gender=%s>"
        return u % (self.user_id, self.username, self.email, self.age, self.gender)

    def recommend(self):
        """Predict games that this user would like"""

        
        # Find users that are similar to the current user
        review_dict = {}

        for review in self.reviews:
            review_dict[review.game_id] = review.score

        min_age = self.age / 10 * 10
        max_age = min_age + 10

        sim_users = db.session.query(Review.user_id, Review.game_id, Review.score).filter(User.user_id != self.user_id,
                                              User.gender == self.gender,
                                              User.age >= min_age,
                                              User.age <= max_age,
                                              Review.user_id == User.user_id).all()

        matched_reviews = {}
        for review in sim_users:
            match = review_dict.get(review[1])
            if match:
                if matched_reviews.get(review.user_id):
                    # Ignored in test due to small sample size
                    matched_reviews[review.user_id].append((match, review.score)) # pragma: no cover
                else:
                    matched_reviews[review.user_id] = [(match, review.score)]

        similarities = []
        for user in matched_reviews:
            similarities.append((user,
                            correlation.pearson(matched_reviews[user])))

        if similarities:

            similarities.sort(key=lambda x: x[1], reverse=True)

            #Return top five similar user_ids
            best_users = []
            for i in range(5):
                try:
                    best_users.append(similarities[i][0])
                except IndexError:
                    return best_users
            # Ignored in test due to small sample size
            return best_users # pragma: no cover

        # If there are not similarities, return None
        else:
            return None


class Review(db.Model):
    """Reviews of games; contains score and comment"""

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"),
                        nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"),
                        nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_time = db.Column(db.DateTime, nullable=False,
                            default=datetime.datetime.utcnow)

    # Set middle table relationships to users and games
    user = db.relationship("User", backref="reviews")
    game = db.relationship("Game", backref="reviews")

    def __repr__(self):
        """Provide helpful output when printed"""

        r = "<Review user_id=%s game_id=%s score=%s>"
        return r % (self.user_id, self.game_id, self.score)


class CriticReview(db.Model):
    """Reviews specific to the critic websties scraped

    Kept separate to prevent convoluted queries that occur when critics are
    treated like normal users.
    """

    __tablename__ = "critics"

    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    critic_code = db.Column(db.String(5), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"),
                        nullable=False)
    score = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(32), nullable=False)

    game = db.relationship("Game", backref="critics")

    def __repr__(self):
        """Provide helpful output when printed"""

        r = "<CriticReview critic_code=%s game_id=%s score=%s>"
        return r % (self.critic_code, self.game_id, self.score)


class Game(db.Model):
    """Game data"""

    __tablename__ = "games"

    game_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    summary = db.Column(db.Text)
    storyline = db.Column(db.Text)
    release_date = db.Column(db.DateTime, nullable=False)
    franchise_id = db.Column(db.Integer, db.ForeignKey("franchises.franchise_id"))

    # Set one to many relationship with franchises
    franchise = db.relationship("Franchise", backref="games")

    def __repr__(self):
        """Provide helpful output when printed"""

        g = "<Game game_id=%s name=%s release_date=%s>"
        return g % (self.game_id, self.name, self.release_date)


class CurrentGame(db.Model):
    """Tabel for holding onto currently playing games for users"""

    __tablename__ = "current_games"

    current_game_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"))
    notes = db.Column(db.Text)
    time_played = db.Column(db.Integer)

    user = db.relationship("User", backref="currently_playing")

    def __repr__(self):
        """Provide helpful output when printed"""

        g = "<CurrentGame game_id=%s user_id=%s>"
        return g % (self.game_id, self.user_id)


class Cover(db.Model):
    """Game cover art image and dimensions"""

    __tablename__ = "covers"

    cover_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"))
    url = db.Column(db.String(256), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)

    # Set one to many reltionship with games
    game = db.relationship("Game", backref="covers")

    def __repr__(self):
        """Provide helpful output when printed"""

        c = "<Cover cover_id=%s game_id=%s url=%s>"
        return c % (self.cover_id, self.game_id, self.url)


class Franchise(db.Model):
    """Franchise data"""

    __tablename__ = "franchises"

    franchise_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """Provide helpful output when printed"""

        f = "<Franchise franchise_id=%s name=%s>"
        return f % (self.franchise_id, self.name)


class GameGenre(db.Model):
    """Association table between games and genres"""

    __tablename__ = "game_genres"

    gamegenre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.genre_id"), nullable=False)


class Genre(db.Model):
    """Genre table"""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(32), nullable=False)

    # Set many to many relationship with games using secondary
    games = db.relationship("Game", secondary="game_genres", backref="genres")

    def __repr__(self):
        """Provide helpful output when printed"""

        g = "<Genre genre_id=%s genre=%s>"
        return g % (self.genre_id, self.genre)


class GameDeveloper(db.Model):
    """Association table between games and developers"""

    __tablename__ = "game_developers"

    gamedev_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey("developers.developer_id"),
                             nullable=False)


class Developer(db.Model):
    """Developer table"""

    __tablename__ = "developers"

    developer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    # Set many to many relationship with games using secondary
    games = db.relationship("Game", secondary="game_developers", backref="developers")

    def __repr__(self):
        """Provide helpful output when printed"""

        d = "<Developer developer_id=%s name=%s>"
        return d % (self.developer_id, self.name)


class Video(db.Model):
    """Video table"""

    __tablename__ = "videos"

    video_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    slug = db.Column(db.String(32))
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    name = db.Column(db.String(256), nullable=False)

    # Set one to many relationship with games
    game = db.relationship("Game", backref="videos")

    def __repr__(self):
        """Provide helpful output when printed"""

        v = "<Video video_id=%s game_id=%s name=%s url=%s>"
        return v % (self.video_id, self.game_id, self.name, self.url)


class GamePlatform(db.Model):
    """Association table between games and platforms"""

    __tablename__ = "game_platforms"

    gameplatform_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey("platforms.platform_id"),
                            nullable=False)


class Platform(db.Model):
    """Game platform table"""

    __tablename__ = "platforms"

    platform_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    # Set many to many relationship with games using secondary
    games = db.relationship("Game", secondary="game_platforms", backref="platforms")

    def __repr__(self):
        """Provide helpful output when printed"""

        p = "<Platform platform_id=%s name=%s>"
        return p % (self.platform_id, self.name)


class Screenshot(db.Model):
    """Screenshot table"""

    __tablename__ = "screenshots"

    screenshot_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"))
    url = db.Column(db.String(256), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)

    # Set one to many reltionship with games
    game = db.relationship("Game", backref="screenshots")

    def __repr__(self):
        """Provide helpful output when printed"""

        s = "<Screenshot screenshot_id=%s game_id=%s url=%s>"
        return s % (self.screenshot_id, self.game_id, self.url)


##############################################################################
# Helper functions


def connect_to_db(app, db_url='postgresql:///games'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)


def example_data():
    """Makes some example objects for db testing"""
    user = User(username='testo', password='testo', email='testo@test.com',
                age=35, gender='nb_gf')
    user2 = User(username='boolean', password='bear', email='bb@test.com',
                 age=32, gender='nb_gf')
    user3 = User(username='instance', password='cat', email='ic@test.com',
                 age=30, gender='nb_gf')
    review = Review(user_id=1, game_id=1, score=95, comment=None)
    review2 = Review(user_id=2, game_id=1, score=95, comment=None)
    critic_review = CriticReview(game_id=1, critic_code='ign', score=100, name="IGN")
    game = Game(game_id=1, name="Testo", release_date=datetime.datetime.now(), franchise_id=1)
    current_game = CurrentGame(user_id=1, game_id=1)
    cover = Cover(game_id=1, url="///testo.png", width=360, height=240)
    franchise = Franchise(franchise_id=1, name="Testo Stories")
    genre = Genre(genre="test")
    developer = Developer(name="Testo Games")
    platform = Platform(name="Testo360")
    screenshot = Screenshot(game_id=1, url="///test.png", width=260, height=240)

    db.session.add_all([user, user2, user3, franchise, game])
    db.session.commit()
    db.session.add_all([review, review2, critic_review, current_game,
                       cover, genre, developer, platform, screenshot])
    db.session.commit()

    gameGenre = GameGenre(game_id=1, genre_id=1)
    gameDeveloper = GameDeveloper(game_id=1, developer_id=1)
    gamePlatform = GamePlatform(game_id=1, platform_id=1)

    db.session.add_all([gameGenre, gamePlatform, gameDeveloper])
    db.session.commit()

