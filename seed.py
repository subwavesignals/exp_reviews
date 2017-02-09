"""Utility file to seed games database from IGDB API and fake user/reviews"""

from sqlalchemy import func
from model import (User, Review, Game, Franchise, Cover, GamePlatform, Platform,
                   GameDeveloper, Developer, GameGenre, Genre, Screenshot)

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

    # Clears table in event of preexisting data
    Game.query.delete()

    # Iterate over games_list and pull info from item dictionary
    for index, item in enumerate(games_list):
        game_id = item["id"]
        name = item["name"]
        summary = item.get("summary")
        storyline = item.get("storyline")
        epoch = item["first_release_date"]
        franchise_id = item.get("franchise")

        # Set the correct time from the UNIX epoch given by IGDB
        first_release_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                           time.localtime(epoch))


        game = Game(game_id=game_id, name=name, summary=summary,
                         storyline=storyline, release_date=first_release_date,
                         franchise_id=franchise_id)

        db.session.add(game)

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_covers(games_list):

    print "Covers"

    # Clears table in event of preexisting data
    Cover.query.delete()

    # Iterate through games, get cover info and make cover if game has cover(s)
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

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_franchises():
    """Loads franchise_id and name into franchises table"""

    # Get all franchise info
    franchise_url = pull_data.get_franchise_url()
    franchises_list = pull_data.make_request(franchise_url)

    print "Franchises"

    # Clears table in event of preexisting data
    Franchise.query.delete()

    # Iterate over franchises and add each to db
    for item in franchises_list:
        franchise_id = item["id"]
        name = item["name"]

        franchise = Franchise(franchise_id=franchise_id, name=name)

        db.session.add(franchise)

    db.session.commit()


def load_genres():
    """Loads genre_id and name into genres table"""

    #Get all genre info
    genre_url = pull_data.get_genre_url()
    genres_list = pull_data.make_request(genre_url)

    print "Genres"

    # Clears table in event of preexisting data
    Genre.query.delete()

    # Iterate over genres and add each to db
    for item in genres_list:
        genre_id = item["id"]
        genre = item["name"]

        genre = Genre(genre_id=genre_id, genre=genre)

        db.session.add(genre)

    db.session.commit()


def load_developers(games_list): 
    """Loads developer_id and name into developers table"""

    print "Developers"

    # Clears table in event of preexisting data
    Developer.query.delete()

    # Dict of already added dev_ids to preserve ref. integ.
    all_dev_ids = {}

    # Iterate over games, if the game has developers and the dev_id isn't
    # already in the dict, request info on the dev
    for index, item in enumerate(games_list):
        if item.get("developers"):
            developers = item["developers"]
            for developer_id in developers:
                if developer_id not in all_dev_ids:
                    all_dev_ids[developer_id] = developer_id

                    company_url = pull_data.get_company_url(developer_id)
                    company = pull_data.make_request(company_url)

                    # Get the dev name and add the row to the db
                    if (company[0].get("name")):
                        name = company[0]["name"]

                        developer = Developer(developer_id=developer_id, name=name)

                        db.session.add(developer)

        # Show progress and inbetween commits to help load
        if index % 500 == 0:
            db.session.commit()
            print index

    db.session.commit()


def load_platforms(platforms_list):
    """Loads platform_id and name into platforms table"""

    print "Platforms"

    # Clears table in event of preexisting data
    Platform.query.delete()

    # Iterate over platforms and add each to db
    for item in platforms_list:
        platform_id = item["id"]
        name = item["name"]

        platform = Platform(platform_id=platform_id, name=name)

        db.session.add(platform)

    db.session.commit()


def load_screenshots(games_list):
    """Loads screenshot_id, url, width, and height into screenshots table"""

    print "Screenshots"

    # Clears table in event of preexisting data
    Platform.query.delete()

    # Iterate over games and add each screenshot to the db
    for index, item in enumerate(games_list):
        game_id = item["id"]
        if item.get("screenshots"):
            screenshots = item["screenshots"]
            for picture in screenshots:
                url = picture["url"]
                width = picture["width"]
                height = picture["height"]

                screenshot = Screenshot(url=url, width=width, height=height)

                db.session.add(screenshot)

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_game_genres(games_list):
    """Load association table game_genre"""

    print "Game Genres"

    # Clears table in event of preexisting data
    GameGenre.query.delete()

    # Iterate over games, if the game has genres, add it to the db
    for index, item in enumerate(games_list):
        game_id = item["id"]
        if item.get("genres"):
            genres = item["genres"]
            for genre in genres:
                game_genre = GameGenre(game_id=game_id, genre_id=genre)

                db.session.add(game_genre);

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_game_devs(games_list):
    """Load association table game_developers"""

    print "Game Developers"

    # Clears table in event of preexisting data
    GameDeveloper.query.delete()

    # Iterate over games, if the game has devs, add it to the db
    for index, item in enumerate(games_list):
        game_id = item["id"]
        if item.get("developers"):
            developers = item["developers"]
            for developer in developers:
                game_dev = GameDeveloper(game_id=game_id, developer_id=developer)

                db.session.add(game_dev);

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


def load_game_platforms(platforms_list):
    """Load association table game_developers"""

    print "Game Platforms"

    # Clears table in event of preexisting data
    GamePlatform.query.delete()

    # Iterate over platforms, if the platform has games, add them to the db
    for index, item in enumerate(platforms_list):
        platform_id = item["id"]
        if item.get("games"):
            games = item["games"]
            for game in games:
                game_platform = GameDeveloper(platform_id=platform_id, game_id=game)

                db.session.add(game_platform);

        # Show progress and inbetween commits to help load
        if (index % 500 == 0):
            db.session.commit()
            print index

    db.session.commit()


################################################################################
# Run when called from main (for testing; will eventually change)

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Get games data before seeding since it has data needed for other tables
    print "Games List"
    game_url = pull_data.get_game_url()
    games_list = pull_data.make_request(game_url)

    # print "Platforms List"
    # platform_url = pull_data.get_platform_url()
    # platforms_list = pull_data.make_request(platform_url)

    # # Call load methods in order to not annoy relationships
    # load_users()
    # load_reviews()
    # load_genres()
    # load_developers(games_list)
    # load_platforms(platforms_list)
    # load_franchises()
    # load_games(games_list)
    # load_covers(games_list)
    load_screenshots(games_list)
    # load_game_genres(games_list)
    # load_game_devs(games_list)
    # load_game_platforms(platforms_list)







