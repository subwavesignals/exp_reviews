"""EXP Reviews"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, connect_to_db, db


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

    return render_template("index.html")


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
        user = User.query.filter_by(user_id=session["user_id"]).one()
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

    return render_template("login.html")


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