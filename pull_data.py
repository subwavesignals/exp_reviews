import unirest
import os

key = os.environ["IGDB_API_KEY"]
base_url = "https://igdbcom-internet-game-database-v1.p.mashape.com"

def set_games():
    """Return all needed game data for most recent 10,000 in JSON object for seeding"""

    endpoint = "/games"

    field_list = ["id", "name", "summary", "storyline", "collection", "franchise",
                  "developers", "publishers", "genres", "first_release_date",
                  "videos", "cover"]
    fields = "/?fields=" + "%2C".join(field_list) 

    limit = "&limit=50"

    offset = "&offset="
    offset_value = 0

    sort_by = "&order=first_release_date%3Adesc"

    all_games = []
    games_left = True

    while games_left:
        if offset_value + 50 >= 10000:
            limit = "&limit=49"
        response = unirest.get(base_url + endpoint + fields + limit + offset 
                               + str(offset_value), headers={"X-Mashape-Key": key})
        all_games.extend(response.body)
        offset_value += 50
        if len(response.body) < 50:
            games_left = False
        print len(all_games)

    return all_games


def get_collections():
    """Return id and name from collections"""

    endpoint = "/collections"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    limit = "&limit=50"

    offset = "&offset="
    offset_value = 0

    all_collections = []
    collections_left = True

    while collections_left:
        response = unirest.get(base_url + endpoint + fields + limit + offset 
                               + str(offset_value), headers={"X-Mashape-Key": key})
        all_collections.extend(response.body)
        offset_value += 50
        if len(response.body) < 50:
            collections_left = False
        print len(all_collections)

    return all_collections




