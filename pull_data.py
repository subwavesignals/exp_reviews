import unirest
import os

key = os.environ["IGDB_API_KEY"]
base_url = "https://igdbcom-internet-game-database-v1.p.mashape.com"

def make_request(url):
    """Makes request to correct enpoint and for given fields based on url"""

    limit = "&limit=50"
    
    offset = "&offset="
    offset_value = 0

    response_list = []
    data_left = True

    while data_left:
        if offset_value + 50 >= 10000:
            limit = limit[:-2] + str(49)
        response = unirest.get(url + limit + offset + str(offset_value),
                               headers={"X-Mashape-Key": key})
        response_list.extend(response.body)
        offset_value += 50
        if len(response.body) < 50:
            data_left = False
        print len(response_list)

    return response_list 

def get_games():
    """Return all needed game data for most recent 10,000 in JSON object for seeding"""

    endpoint = "/games"

    field_list = ["id", "name", "summary", "storyline", "collection", "franchise",
                  "developers", "publishers", "genres", "first_release_date",
                  "videos", "cover"]
    fields = "/?fields=" + "%2C".join(field_list) 

    sort_by = "&order=first_release_date%3Adesc"

    return base_url + endpoint + fields + sort_by


def get_collections():
    """Return id and name from collections"""

    endpoint = "/collections"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    return base_url + endpoint + fields


def get_franchises():
    """Return id and name from franchises"""

    endpoint = "/franchises"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    return base_url + endpoint + fields


def get_genres():
    """Return id and name from genres"""

    endpoint = "/genres"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    return base_url + endpoint + fields


def get_platforms():
    """Return id, name, and games list from platforms"""

    endpoint = "/platforms"

    field_list = ["id", "name", "games"]
    fields = "/?fields=" + "%2C".join(field_list)
    
    return base_url + endpoint + fields


def get_videos():
    """Return name and YouTube slug from videos"""

    endpoint = "/videos"

    field_list = ["name", "slug"]
    fields = "/?fields=" + "%2C".join(field_list)
  
    return base_url + endpoint + fields



