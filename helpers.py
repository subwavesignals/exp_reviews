"""Helper functions for server routes"""

from flask import session
from flask_sqlalchemy import sqlalchemy
from sqlalchemy.sql import func

from model import (User, Game, Review, CriticReview, Platform, Developer,
                   Genre, Franchise, CurrentGame, db)


################################################################################
# @app.route("/") helpers

def assign_avg_score(lst, recent=False):
    """Gets the avg score from the query and binds it to the game object"""

    results = []

    for review in lst:
        game_id = review.game_id
        game = Game.query.filter_by(game_id=game_id).first()
        if not recent:
            game.avg_score = float(review.avg_score)
        else:        
            avg_score = (db.session.query(func.avg(Review.score)).filter(
                         Review.game_id==game_id).first())
            game.avg_score = float(avg_score[0])

        results.append(game)

    return results


def get_recommended_list(user_id):
    """Gets the best user matches for current user; builds unique rec. list"""

    user = User.query.filter_by(user_id=session["user_id"]).first()
    user_reviewed = {}
    for review in user.reviews:
        user_reviewed[review.game_id] = review
    best_users = user.recommend()
    print best_users
    recommended_list = []
    if best_users:
        for other_user in best_users:
            top_four = (Review.query.filter_by(user_id=other_user).order_by(
                        Review.score.desc()).limit(4).all())
            recommended_list.extend(top_four)
    else:
        # Ignored in test due to small sample size
        recommended_list = None # pragma: no cover

    print recommended_list
    # Remove duplicates
    if recommended_list:
        recommended_list = list(set(recommended_list))
        final_list = []
        for game in recommended_list:
            if game.game_id not in user_reviewed:
                # Ignored in test due to small sample size
                final_list.append(game) # pragma: no cover
        recommended_list = final_list


    return recommended_list

################################################################################

################################################################################
# @app.route("/get_review_breakdown") helpers

def sort_by_age_gender(users):

    queries = {"m": users.filter(User.gender == "m"),
               "f": users.filter(User.gender == "f"),
               "tm": users.filter(User.gender == "tm"),
               "tw": users.filter(User.gender == "tw"),
               "nb": users.filter(User.gender == "nb_gf")}

    datasets = {"m": [], "f": [], "tm": [], "tw":[], "nb": []}

    for item in queries:
        datasets[item].append(queries[item].filter(User.age <= 19).all())
        datasets[item].append(queries[item].filter(User.age <= 29, User.age >19).all())
        datasets[item].append(queries[item].filter(User.age <= 39, User.age >29).all())
        datasets[item].append(queries[item].filter(User.age <= 49, User.age >39).all())

    return datasets

def get_chart_dict(averages):

    return { 
        "labels": ["10-19", "20-29", "30-39", "40-49"],
        "datasets": [
            {
                "label": "Cis Men",
                "backgroundColor": "rgba(91,162,163,0.2)",
                "borderColor": "rgba(91,162,163,1)",
                "pointBackgroundColor": "rgba(91,162,163,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(91,162,163,1)",
                "data": averages["m"]
            },
            {
                "label": "Cis Women",
                "backgroundColor": "rgba(193,66,66,0.2)",
                "borderColor": "rgba(193,66,66,1)",
                "pointBackgroundColor": "rgba(193,66,66,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(193,66,66,1)",
                "data": averages["f"]
            },
            {
                "label": "Trans Men",
                "backgroundColor": "rgba(149,89,175,0.2)",
                "borderColor": "rgba(149,89,175,1)",
                "pointBackgroundColor": "rgba(149,89,175,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(149,89,175,1)",
                "data": averages["tm"]
            },
            {
                "label": "Trans Women",
                "backgroundColor": "rgba(89,128,175,0.2)",
                "borderColor": "rgba(89,128,175,1)",
                "pointBackgroundColor": "rgba(89,128,175,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(89,128,175,1)",
                "data": averages["tw"]
            },
            {
                "label": "Nonbinary",
                "backgroundColor": "rgba(159,161,161,0.2)",
                "borderColor": "rgba(159,161,161,1)",
                "pointBackgroundColor": "rgba(159,161,161,1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(159,161,161,1)",
                "data": averages["nb"]
            }
        ]
    }