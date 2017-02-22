"""EXP Reviews"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import sqlalchemy
from sqlalchemy.sql import func
import json
from math import ceil
from datetime import datetime

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

    all_user_reviews = db.session.query(func.avg(Review.score).label("avg_score"), Review.game_id).group_by(Review.game_id).order_by(func.avg(Review.score).desc())
    user_reviews = all_user_reviews.limit(20).all()
    all_critic_reviews = db.session.query(func.avg(CriticReview.score).label("avg_score"), CriticReview.game_id).group_by(CriticReview.game_id).order_by(func.avg(CriticReview.score).desc())
    critic_reviews = all_critic_reviews.limit(20).all()
    user_list = []
    critic_list = []

    for review in user_reviews:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        game.avg_user_score = float(review.avg_score)
   
        user_list.append(game)

    for review in critic_reviews:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        game.avg_critic_score = float(review.avg_score)

        critic_list.append(game)

    recent_reviews = Review.query.order_by(Review.review_time.desc()).limit(20).all()
    recent_list = []

    for review in recent_reviews:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        avg_score = db.session.query(func.avg(Review.score)).filter(Review.game_id==game_id).first()
        game.avg_user_score = float(avg_score[0])

        recent_list.append(game)

    soon_list = Game.query.filter(Game.release_date > datetime.now()).order_by(Game.release_date).limit(20).all()

    if session.get("user_id"):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        user_reviwed = {}
        for review in user.reviews:
            user_reviwed[review.game_id] = review
        best_users = user.recommend()
        recommended_list = []
        if best_users:
            for other_user in best_users:
                top_four = Review.query.filter_by(user_id=other_user).order_by(Review.score.desc()).limit(4).all()
                recommended_list.extend(top_four)
        else:
            # Ignored in test due to small sample size
            recommended_list = None # pragma: no cover
    else:
        recommended_list = None

    # Remove duplicates
    if recommended_list:
        recommended_list = list(set(recommended_list))
        final_list = []
        for game in recommended_list:
            if game.game_id not in user_reviwed:
                # Ignored in test due to small sample size
                final_list.append(game) # pragma: no cover
        recommended_list = final_list
        print len(recommended_list)

    return render_template("index.html", 
                           recommended_list=recommended_list,
                           user_list=user_list,
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

    search = {}
    search["text"] = request.args.get("search")
    results = {}

    results["users"] = db.session.query(User.username, User.user_id).filter(User.username.ilike("%" + search["text"] + "%")).all()
    results["games"] = db.session.query(Game.name, Game.game_id).filter(Game.name.ilike("%" + search["text"] + "%")).all()
    results["genres"] = db.session.query(Genre.genre, Genre.genre_id).filter(Genre.genre.ilike("%" + search["text"] + "%")).all()
    results["franchises"] = db.session.query(Franchise.name, Franchise.franchise_id).filter(Franchise.name.ilike("%" + search["text"] + "%")).all()
    results["developers"] = db.session.query(Developer.name, Developer.developer_id).filter(Developer.name.ilike("%" + search["text"] + "%")).all()
    results["platforms"] = db.session.query(Platform.name, Platform.platform_id).filter(Platform.name.ilike("%" + search["text"] + "%")).all()

    for key in results:
        print results[key]
        results[key] = load_search_results(results, key)

    search["results"] = results

    return render_template("search.html", search=search)


def load_search_results(results, key):
    """Builds links for each search result item"""

    for index, item in enumerate(results[key]):
        item = (item[0], "/" + key + "/" + str(item[1]))
        results[key][index] = item

    return results[key]


@app.route("/games/<game_id>")
def display_game(game_id):
    """Returns game_details page for selected game_id"""

    game = Game.query.filter_by(game_id=game_id).first()
    reviews = Review.query.filter_by(game_id=game_id).all()

    player_score = db.session.query(func.avg(Review.score)).filter_by(game_id=game_id).first()
    critic_scores = db.session.query(CriticReview.name, CriticReview.score).filter_by(game_id=game_id).all()

    num_pages = int(ceil(float(len(reviews)) / 10))

    if session.get("user_id"):
        user_id = session["user_id"]
        current_review = Review.query.filter_by(user_id=user_id, game_id=game_id).first()
        added = CurrentGame.query.filter_by(user_id=user_id, game_id=game_id).first()
    else:
        current_review = None
        added = None


    return render_template("game_details.html", game=game, reviews=reviews,
                           player_score=player_score, critic_scores=critic_scores,
                           num_pages=num_pages, current_review=current_review,
                           added=added)


@app.route("/review/<game_id>", methods=["POST"])
def add_update_review(game_id):

    user_id = session["user_id"]
    score = request.form.get("score")
    comment = request.form.get("comment")

    review = Review.query.filter_by(user_id=user_id, game_id=game_id).first()

    if review:
        review.score = score
        review.comment = comment
        review.review_time = datetime.now()
        flash("Your rating has been updated.")
    else:
        review = Review(user_id=user_id, game_id=game_id, score=score,
                        comment=comment)
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

    current = CurrentGame.query.filter_by(user_id=user_id).all()
    current_games = []

    for game in current:
        game_item = Game.query.filter_by(game_id=game.game_id).first()
        game_item.notes = game.notes
        game_item.time_played = game.time_played
        current_games.append(game_item)

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


@app.route("/get_review_breakdown")
def get_review_breakdown():
    """Returns datasets for age and gender grouped review scores"""

    game_id = request.args.get("gameId")

    user_review_join = db.session.query(User.age, User.gender, Review.score).join(Review).filter_by(game_id=game_id)

    queries = {"m": user_review_join.filter(User.gender == "m"),
               "f": user_review_join.filter(User.gender == "f"),
               "tm": user_review_join.filter(User.gender == "tm"),
               "tw": user_review_join.filter(User.gender == "tw"),
               "nb": user_review_join.filter(User.gender == "nb_gf")}

    datasets = {"m": [], "f": [], "tm": [], "tw":[], "nb": []}

    for item in queries:
        datasets[item].append(queries[item].filter(User.age <= 19).all())
        datasets[item].append(queries[item].filter(User.age <= 29, User.age >19).all())
        datasets[item].append(queries[item].filter(User.age <= 39, User.age >29).all())
        datasets[item].append(queries[item].filter(User.age <= 49, User.age >39).all())
        datasets[item].append(queries[item].filter(User.age <= 59, User.age >49).all())

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

    return jsonify({ 
        "labels": ["10-19", "20-29", "30-39", "40-49", "50-59"],
        "datasets": [
            {
                "label": "Men",
                "backgroundColor": "rgba(179,181,198,0.2)",
                "borderColor": "rgba(179,181,198,1)",
                "pointBackgroundColor": "rgba(179,181,198,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(179,181,198,1)",
                "data": averages["m"]
            },
            {
                "label": "Women",
                "backgroundColor": "rgba(255,99,132,0.2)",
                "borderColor": "rgba(255,99,132,1)",
                "pointBackgroundColor": "rgba(255,99,132,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(255,99,132,1)",
                "data": averages["f"]
            },
            {
                "label": "Transmen",
                "backgroundColor": "rgba(179,181,198,0.2)",
                "borderColor": "rgba(179,181,198,1)",
                "pointBackgroundColor": "rgba(179,181,198,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(179,181,198,1)",
                "data": averages["tm"]
            },
            {
                "label": "Transwomen",
                "backgroundColor": "rgba(255,99,132,0.2)",
                "borderColor": "rgba(255,99,132,1)",
                "pointBackgroundColor": "rgba(255,99,132,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(255,99,132,1)",
                "data": averages["tw"]
            },
            {
                "label": "Nonbinary",
                "backgroundColor": "rgba(179,181,198,0.2)",
                "borderColor": "rgba(179,181,198,1)",
                "pointBackgroundColor": "rgba(179,181,198,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(179,181,198,1)",
                "data": averages["nb"]
            }
        ]
    })



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

