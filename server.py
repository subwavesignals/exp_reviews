"""EXP Reviews"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import sqlalchemy
from sqlalchemy.sql import func
import json
from math import ceil
from datetime import datetime
import helpers

from model import (User, Game, Review, CriticReview, Platform, Developer,
                   Genre, Franchise, CurrentGame, connect_to_db, db)

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

    user_reviews = (db.session.query(func.avg(Review.score).label("avg_score"), 
                    Review.game_id).group_by(Review.game_id).order_by(func.avg(
                    Review.score).desc()).limit(20).all())
    critic_reviews = (db.session.query(func.avg(CriticReview.score).label("avg_score"), 
                      CriticReview.game_id).group_by(CriticReview.game_id).order_by(
                      func.avg(CriticReview.score).desc()).limit(20).all())
    recent_reviews = (Review.query.order_by(Review.review_time.desc()).limit(20).all())
    soon_list = (Game.query.filter(Game.release_date > datetime.now()).order_by(
                 Game.release_date).limit(20).all())

    user_list = helpers.assign_avg_score(user_reviews)
    critic_list = helpers.assign_avg_score(critic_reviews)
    recent_list = helpers.assign_avg_score(recent_reviews, recent=True)

    if session.get("user_id"):
        recommended_list = helpers.get_recommended_list(session["user_id"])
    else:
        recommended_list = None

    return render_template("index.html", 
                           recommended_list=recommended_list, user_list=user_list,
                           critic_list=critic_list, recent_list=recent_list,
                           soon_list=soon_list)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Displays signup form on GET and handles input on POST"""

    if request.method == "GET":
        return render_template("signup.html")

    else:

        #Validation of username and email happens in the form, so add user
        user = User(username=request.form.get("username"),
                    email=request.form.get("email"),
                    password=request.form.get("password"))

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

        # Get user in process, add info to DB row
        user = User.query.filter_by(user_id=session["user_id"]).first()
        user.fname = request.form.get("fname")
        user.lname = request.form.get("lname")
        user.age = request.form.get("age")
        user.gender = request.form.get("gender")
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
            flash("Invalid username.")
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


@app.route("/search")
def display_results():
    """Displays paginated results of user search"""

    search = request.args.get("search")
    results = {}

    results["users"] = (db.session.query(User.username, User.user_id).filter(
                        User.username.ilike("%" + search + "%")).all())
    results["games"] = Game.query.filter(Game.name.ilike("%" + search + "%")).all()
    results["genres"] = Genre.query.filter(Genre.genre.ilike("%" + search + "%")).all()
    results["franchises"] = (Franchise.query.filter(Franchise.name.ilike("%" + 
                             search + "%")).all())
    results["developers"] = (Developer.query.filter(Developer.name.ilike("%" + 
                             search + "%")).all())
    results["platforms"] = (Platform.query.filter(Platform.name.ilike("%" + 
                            search + "%")).all())

    return render_template("search.html", search=search, results=results)


@app.route("/games/<game_id>")
def display_game(game_id):
    """Returns game_details page for selected game_id"""

    game = Game.query.filter_by(game_id=game_id).first()
    reviews = Review.query.filter_by(game_id=game_id).all()

    player_score = (db.session.query(func.avg(Review.score))
                    .filter_by(game_id=game_id).first())
    critic_scores = (db.session.query(CriticReview.name, CriticReview.score)
                     .filter_by(game_id=game_id).all())

    num_pages = int(ceil(float(len(reviews)) / 10))

    videos = game.videos

    if session.get("user_id"):
        user_id = session["user_id"]
        current_review = (Review.query.filter_by(user_id=user_id, 
                          game_id=game_id).first())
        added = (CurrentGame.query.filter_by(user_id=user_id,
                 game_id=game_id).first())
    else:
        current_review = None
        added = None


    return render_template("game_details.html", game=game, reviews=reviews,
                           player_score=player_score, critic_scores=critic_scores,
                           num_pages=num_pages, current_review=current_review,
                           added=added, videos=videos)


@app.route("/review/<game_id>", methods=["POST"])
def add_update_review(game_id):

    review = Review.query.filter_by(user_id=session["user_id"], game_id=game_id).first()

    if review:
        review.score = request.form.get("score")
        review.comment = request.form.get("comment")
        review.review_time = datetime.now()
        flash("Your rating has been updated.")
    else:
        review = Review(user_id=session["user_id"], game_id=game_id, 
                        score=request.form.get("score"),
                        comment=request.form.get("comment"))
        db.session.add(review)
        flash("Your rating has been added.")

    db.session.commit()

    return redirect("/games/" + game_id)


@app.route("/users/<user_id>")
def display_user(user_id):
    """Displays the user and all of their reviews"""

    user = User.query.filter_by(user_id=user_id).first()
    reviews = Review.query.filter_by(user_id=user_id).all()

    num_pages = int(ceil(float(len(reviews)) / 10))

    current_games = CurrentGame.query.filter_by(user_id=user_id).all()

    for game in current_games:
        game_item = Game.query.filter_by(game_id=game.game_id).first()
        game.name = game_item.name
        game.cover = game_item.covers[0]

    return render_template("user_details.html", user=user, reviews=reviews,
                           num_pages=num_pages, current_games=current_games)


@app.route("/genres/<genre_id>")
def display_genre(genre_id):
    """Displays the list of games for a given genre"""

    genre = Genre.query.filter_by(genre_id=genre_id).first()

    return render_template("genre_details.html", genre=genre)


@app.route("/developers/<developer_id>")
def display_developer(developer_id):
    """Displays the list of games for a given developer"""

    developer = Developer.query.filter_by(developer_id=developer_id).first()

    return render_template("developer_details.html", developer=developer)


@app.route("/franchises/<franchise_id>")
def display_franchise(franchise_id):
    """Displays the list of games for a given franchise"""

    franchise = Franchise.query.filter_by(franchise_id=franchise_id).first()

    return render_template("franchise_details.html", franchise=franchise)


@app.route("/platforms/<platform_id>")
def display_platform(platform_id):
    """Displays the list of games for a given platform"""

    platform = Platform.query.filter_by(platform_id=platform_id).first()

    return render_template("platform_details.html", platform=platform)


@app.route("/get_game_reviews.json")
def get_game_reviews():
    """Returns json object of reviews for pagination"""

    game_id = int(request.args.get("gameId"))
    max_reviews = int(request.args.get("maxReview"))

    reviews = Review.query.filter_by(game_id=game_id).offset(max_reviews - 10).limit(10).all()

    cleaned_reviews = []
    for review in reviews:
        cleaned_reviews.append({"username": review.user.username,
                                "user_id": review.user.user_id,
                                "score": review.score,
                                "comment": review.comment})

    return jsonify(cleaned_reviews)


@app.route("/get_user_reviews.json")
def get_user_reviews():
    """Returns json object of reviews for pagination"""

    user_id = int(request.args.get("userId"))
    max_reviews = int(request.args.get("maxReview"))

    reviews = Review.query.filter_by(user_id=user_id).offset(max_reviews - 10).limit(10).all()

    cleaned_reviews = []
    for review in reviews:
        cleaned_reviews.append({"name": review.game.name,
                                "game_id": review.game.game_id,
                                "score": review.score,
                                "comment": review.comment})

    return jsonify(cleaned_reviews)


@app.route("/update_notes", methods=["POST"])
def update_notes():
    """Updates and commits changes to currently playing table"""

    user_id = request.form.get("user_id")
    game_id = request.form.get("game_id")
    notes = request.form.get("notes")
    time_played = request.form.get("time_played")

    current_game = CurrentGame.query.filter_by(user_id=user_id, game_id=game_id).first()

    current_game.notes = notes
    current_game.time_played = time_played

    db.session.commit()

    return jsonify("Updated")


@app.route("/add_game", methods=["POST"])
def add_game():
    """Adds selected game to user's currently playing list"""

    user_id = session["user_id"]
    game_id = request.form.get("game_id")

    current_game = CurrentGame(user_id=user_id, game_id=game_id)

    db.session.add(current_game)
    db.session.commit()

    return jsonify("Added")


@app.route("/publish_review", methods=["POST"])
def publish_review():
    """Turns a user's notes into a review and add it to db"""

    user_id = request.form.get("user_id")
    game_id = request.form.get("game_id")
    notes = request.form.get("notes")
    time_played = request.form.get("time_played")
    score = request.form.get("score")

    comment = notes + "\n\nTime Played: " + str(time_played)

    prev_review = Review.query.filter_by(user_id=user_id, game_id=game_id).first()
    if prev_review:
        prev_review.score = score
        prev_review.comment = comment
    else:
        review = Review(user_id=user_id, game_id=game_id, score=score, comment=comment)
        db.session.add(review)

    CurrentGame.query.filter_by(user_id=user_id, game_id=game_id).delete()

    db.session.commit()

    return jsonify({"game_id": game_id})


@app.route("/get_review_breakdown")
def get_review_breakdown():
    """Returns datasets for age and gender grouped review scores"""

    game_id = request.args.get("gameId")

    user_review_join = db.session.query(User.age, User.gender, Review.score).join(Review).filter_by(game_id=game_id)

    datasets = helpers.sort_by_age_gender(user_review_join)

    averages = {"m": [], "f": [], "tm": [], "tw":[], "nb": []}

    for gender in datasets:
        for age_bracket in datasets[gender]:
            total = 0
            for user in age_bracket:
                total += user[2]
            if len(age_bracket) >= 1:
                averages[gender].append(float(total) / len(age_bracket))
            else:
                averages[gender].append(0)

    results = helpers.get_chart_dict(averages)

    return jsonify(results)


@app.route("/update_sort_pref", methods=["POST"])
def save_pref():

    user_id = request.form.get("user_id")
    full_sort = request.form.get("isChecked")
    print full_sort

    user = User.query.filter_by(user_id=user_id).first()
    user.full_sort = bool(full_sort)

    db.session.commit()

    return jsonify("Done")


################################################################################
# Helper Functions

if __name__ == "__main__": # pragma: no cover
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug 

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

