"""Makes fake users and fake reviews"""
import random
from model import db, connect_to_db, Game
from server import app

fnames = ["Meggie", "Leslie", "Kiko", "Stephanie", "Lindsey", "Anne",
          "Erica", "Gina", "Ryan", "Dennis", "Ethan", "Todd", "Mark", "Jack",
          "Joel", "Henry", "Ronan", "Sam", "Gansey", "Kyle"]

lnames = ["Smith", "Johnson", "Inge", "Glassman", "Weinberg", "Carroll", 
          "Mahnken", "Yeh", "Goodman", "Winchester", "Burton", "Conrad",
          "Chen", "Boyette", "Lonne", "Fischbach", "Wickham", "Horvatic",
          "Yoder", "Hardin"]

genders = ["f", "m", "tw", "tm", "nb_gf", "pref"]

lorems = ["Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce " +
          "auctor ex vitae nulla tempor, fermentum.", "Lorem ipsum dolor sit " +
          "amet, consectetur adipiscing elit. Morbi euismod congue tellus eget " +
          "dapibus. Suspendisse eu sapien pretium, sollicitudin lacus in, " +
          "facilisis erat. Duis quam purus, dictum id dictum in.", "Lorem " +
          "ipsum dolor sit amet, consectetur adipiscing elit. Phasellus tempor " +
          "neque augue, eget viverra augue porttitor ut. Proin facilisis varius " +
          "urna, elementum pulvinar ex. Class aptent taciti sociosqu ad litora " +
          "torquent per conubia nostra, per inceptos himenaeos. Proin iaculis, " +
          "metus sed placerat viverra, libero risus fermentum felis, sit amet " +
          "tincidunt."
          ]

def fake_users():

    # Empties the file before each run
    with open("static/data/user_data.txt", "w"):
        pass
    file = open("static/data/user_data.txt", "r+")

    for fname in fnames:
        for lname in lnames:
            username = fname[:2].lower() + lname[:5]
            email = username + "@fakeUser.com"
            password = username + str(123)
            age = random.randrange(15, 50)
            gender = random.choice(genders)

            line = "|".join([username, email, password, fname, lname, str(age), 
                            gender])

            file.write(line + "\n")

    file.close()

# Ignored during tests due to db integrity issues
def fake_reviews(): # pragma: no cover

    connect_to_db(app)

    review_list = Game.query.filter(Game.release_date < '2017-02-28 00:00:00').order_by(Game.release_date.desc()).limit(1000)

    # Empties the file before each run
    with open("static/data/review_data.txt", "w"):
        pass
    file = open("static/data/review_data.txt", "r+")

    user_id = 1

    while user_id <= 400:
        offset = 0
        num_review = 0
        while num_review < 100:
            game = random.choice(review_list[offset:offset + 10])
            game_id = game.game_id
            score = score = random.randrange(50, 100)
            comment = random.choice(lorems)

            line = "|".join([str(game_id), str(user_id), str(score), comment])
            file.write(line + "\n")

            num_review += 1
            offset += 10

        user_id += 1
        print user_id

    file.close()
    

