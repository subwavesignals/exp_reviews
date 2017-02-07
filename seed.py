"""Utility file to seed games database from IGDB API and fake user/reviews"""

from sqlalchemy import func
from model import (User, Review, Game, Franchise, Cover, Video,
                   GamePlatform, Platform, GamePublisher, Publisher,
                   GameDeveloper, Developer, GameGenre, Genre)

from model import connect_to_db, db
from server import app
from datetime import datetime
import time

import pull_data


def load_users():
    """Loads fake users from local file in users table"""

    pass


def load_reviews():
    """Loads fake reviews from local file in reviews table"""

    pass


def load_games(games_list):
    """Loads game data into games table

    Cols: game_id, name, summary, storyline, release date, franchise_id
    """

    print "Games"

    Game.query.delete()

    for index, item in enumerate(games_list):
        game_id = item["id"]
        name = item["name"]
        summary = item.get("summary")
        storyline = item.get("storyline")
        epoch = item["first_release_date"]
        franchise_id = item.get("franchise")

        first_release_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                           time.localtime(epoch))

        publisher = Game(game_id=game_id, name=name, summary=summary,
                         storyline=storyline, release_date=first_release_date,
                         franchise_id=franchise_id)

        db.session.add(publisher)

        if (index % 1000 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_covers(games_list):

    print "Covers"

    Cover.query.delete()

    for index, item in enumerate(games_list):
        game_id = item["id"]
        if item.get("cover"):
            cover = item["cover"]
            url = cover["url"]
            width = cover["width"]
            height = cover["height"]

            new_cover = Cover(game_id=game_id, url=url, width=width,
                              height=height)

            db.session.add(new_cover)

        if (index % 1000 == 0):
            db.session.commit()
            print index

    db.session.commit()



def load_franchises():
    """Loads franchise_id and name into franchises table"""

    franchise_url = pull_data.get_franchise_url()
    franchises_list = pull_data.make_request(franchise_url)

    print "Franchises"

    Franchise.query.delete()

    for item in franchises_list:
        franchise_id = item["id"]
        name = item["name"]

        franchise = Franchise(franchise_id=franchise_id, name=name)

        db.session.add(franchise)

    db.session.commit()


def load_genres():
    """Loads genre_id and name into genres table"""

    genre_url = pull_data.get_genre_url()
    genres_list = pull_data.make_request(genre_url)

    print "Genres"

    Genre.query.delete()

    for item in genres_list:
        genre_id = item["id"]
        genre = item["name"]

        genre = Genre(genre_id=genre_id, genre=genre)

        db.session.add(genre)

    db.session.commit()


def load_developers(): #PULL FROM GAMES_LIST
    """Loads developer_id and name into developers table"""

    dev_url = pull_data.get_developer_url()
    devs_list = pull_data.make_request(dev_url)

    print "Developers"

    Developer.query.delete()

    for item in devs_list:
        developer_id = item["id"]
        name = item["name"]

        developer = Developer(developer_id=developer_id, name=name)

        db.session.add(developer)

    db.session.commit()


def load_publishers(): #PULL FROM GAMES LIST
    """Loads publisher_id and name into publishers table"""

    pub_url = pull_data.get_publisher_url()
    pubs_list = pull_data.make_request(pub_url)

    print "Publishers"

    Publisher.query.delete()

    for item in pubs_list:
        publisher_id = item["id"]
        name = item["name"]

        publisher = Publisher(publisher_id=publisher_id, name=name)

        db.session.add(publisher)

    db.session.commit()


def load_platforms():
    """Loads platform_id and name into platforms table"""

    platform_url = pull_data.get_platform_url()
    platform_list = pull_data.make_request(platform_url)

    print "Platforms"

    Platform.query.delete()

    for item in platform_list:
        platform_id = item["id"]
        name = item["name"]

        platform = Platform(platform_id=platform_id, name=name)

        db.session.add(platform)

    db.session.commit()



if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Get games data before seeding since it has data needed for other tables
    game_url = pull_data.get_game_url()
    games_list = pull_data.make_request(game_url)

    # Call load methods in order to not annoy relationships
    load_users()
    load_reviews()
    load_genres()
    print "Genres loaded"
    # load_developers()
    # load_publishers()
    load_platforms()
    print "Platforms loaded"
    load_franchises()
    print "Franchises loaded"
    load_games(games_list)
    print "Games loaded"
    load_covers(games_list)
    print "Covers loaded"






