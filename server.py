"""EXP Reviews"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import sqlalchemy
from sqlalchemy.sql import func
import json

from model import (User, Game, Review, CriticReview, Platform, Developer,
                   Genre, Franchise, connect_to_db, db)


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "khsgzcvwtriquhiwdjbsdjfgiuijasdbhfv"

# Tells Jinja to raise an error when an undefined vairable is used
app.jinja_env.undefined = StrictUndefined

################################################################################
# Routes

@app.route("/")
def display_homepage():
    """Displays the homepage"""

    all_user_reviews = db.session.query(func.avg(Review.score).label("avg_score"), Review.game_id).group_by(Review.game_id).order_by(func.avg(Review.score).desc())
    user_reviews = all_user_reviews.limit(20).all()
    all_critic_reviews = db.session.query(func.avg(CriticReview.score).label("avg_score"), CriticReview.game_id).group_by(CriticReview.game_id).order_by(func.avg(CriticReview.score).desc())
    critic_reviews = all_critic_reviews.limit(20).all()
    user_list = []
    critic_list = []

    for review in user_reviews:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        game.avg_score = float(review.avg_score)
   
        user_list.append(game)

    for review in critic_reviews:
        print review
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        game.avg_score = float(review.avg_score)

        critic_list.append(game)

    recent_reviews = Review.query.order_by(Review.review_time.desc()).limit(20).all()
    recent_list = []

    for review in recent_reviews:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        avg_score = db.session.query(func.avg(Review.score)).filter(Review.game_id==game_id).first()
        game.avg_score = float(avg_score[0])

        recent_list.append(game)

    soon_list = Game.query.filter(Game.release_date > '2017-02-28 00:00:00').order_by(Game.release_date).limit(20).all()


    return render_template("index.html", user_list=user_list,
                           critic_list=critic_list,
                           recent_list=recent_list,
                           soon_list=soon_list)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Displays signup form on GET and handles input on POST"""

    if request.method == "GET":
        return render_template("signup.html")

    else:

        # Get form inputs
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        #Validation of username and email happens in the form, so add user
        user = User(username=username, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        # Set the session value with the user's ID
        session["user_id"] = user.user_id

        return redirect("/create_profile")


@app.route("/create_profile", methods=["GET", "POST"])
def create_profile():
    """Displays more info form on GET and handles input on POST

    Will only display if the username and email the user entered aren't already
    in the User table
    """

    if request.method == "GET":
        return render_template("create_profile.html")

    else:

        # Get form inputs
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        age = request.form.get("age")
        gender = request.form.get("gender")

        # Get user in process, add info to DB row
        user = User.query.filter_by(user_id=session["user_id"]).first()
        user.fname = fname
        user.lname = lname
        user.age = age
        user.gender = gender
        db.session.commit()

        flash("Your profile is complete!")
        return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Displays login form on GET and handles input on POST"""

    if request.method == "GET":
        return render_template("login.html", passed="")

    else:

        # Get form inputs
        username = request.form.get("username")
        password = request.form.get("password")

        # Get user info from username and check for valid username
        valid_user = User.query.filter_by(username=username).first()
        if not valid_user:
            flash("Inavlid username.")
            return redirect("/login")

        # Check that password matches user's password
        elif password != valid_user.password:
            flash("Incorrect password")
            return render_template("login.html", passed=username)

        # Info is correct, set session and redirect home
        else:
            session["user_id"] = valid_user.user_id

            flash("Logged in as " + username)
            return redirect("/")



@app.route("/logout")
def logout():
    """Logs current user out and wipes session"""

    # If no user logged in, don't log out; otherwise clear session
    if session.get('user_id'):
        session.clear()
        flash("Logged out.")
    else:
        flash("No user currently logged in.")

    return redirect("/")


@app.route("/valid_username.json")
def validate_username():
    """Returns username from db if already exists"""

    username = request.args.get("username")
    user_list = db.session.query(User.username).filter_by(username=username).all()

    # Returns user if username already taken, otherwise empty JSON object
    return jsonify(user_list)

@app.route("/valid_email.json")
def validate_email():
    """Returns email from db if already exists"""

    email = request.args.get("email")
    email_list = db.session.query(User.email).filter_by(email=email).all()

    # Returns user if email already taken, otherwise empty JSON object
    return jsonify(email_list)
  

@app.route("/games/<game_id>")
def display_game(game_id):
    """Returns game_details page for selected game_id"""

    game = Game.query.filter_by(game_id=game_id).first()

    return render_template("game_details.html", game=game)


@app.route("/search")
def display_results():
    """Displays paginated results of user search"""

    search = {}
    search["text"] = request.arg.get("search")

    user_results = User.query.filter(User.username.ilike(search["text"]))
    game_results = Game.query.filter(Game.username.ilike(search["text"]))
    genre_results = Genre.query.filter(Genre.username.ilike(search["text"]))
    fran_results = Franchise.query.filter(Franchise.username.ilike(search["text"]))
    dev_results = Developer.query.filter(Developer.username.ilike(search["text"]))
    platform_results = Platform.query.filter(Platform.username.ilike(search["text"]))

    results = user_results.extend(game_results).extend(genre_results).extend(fran_results).extend(dev_results).extend(platform_results)



################################################################################
# Helper Functions

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug 

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

