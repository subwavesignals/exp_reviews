"""EXP Reviews"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

import model


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
def start_adding_user():
    """Prompts new user for username, email, and password"""

    return render_template("signup.html")


@app.route("/create_profile", methods=["GET", "POST"])
def finish_adding_user():
    """Prompts user for personal info after successfully getting username

    Will only display if the username and email the user entered aren't already
    in the User table
    """

    return render_template("create_profile.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Prompts new user for username, email, and password"""

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs current user out and wipes session"""

    # If no user logged in, don't log out; otherwise clear session
    if session.get('username'):
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

    model.connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')