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