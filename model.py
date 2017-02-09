"""Models and database function for EXP Reviews"""

from flask_sqlalchemy import SQLAlchemy
import datetime

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

        r = "<Review user_id=%s game_id=%s score=%s datetime=%s>"
        return r % (self.user_id, self.game_id, self.score, self.review_time)


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
        return r % (self.game_id, self.name, self.release_date)


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

    slug = db.Column(db.String(32), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"), nullable=False)
    name = db.Column(db.String(64), nullable=False)

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


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."


