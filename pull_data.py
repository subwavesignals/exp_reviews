"""Pull data from IGDB. Used with seed.py to build local DB"""

import unirest
import os

key = os.environ["IGDB_API_KEY"]
base_url = "https://igdbcom-internet-game-database-v1.p.mashape.com"


def make_request(url):
    """Makes request to correct enpoint and for given fields based on url"""

    # IGDB has 50 item/request limit
    limit = "&limit=50"
    
    # Set initial offset
    offset = "&offset="
    offset_value = 0

    # Variables to hold return data and control request loop
    response_list = []
    data_left = True

    # If the endpoint has data left, query again
    while data_left:

        # Sets limit to 49 to circumvent IGDB error of 10,000+ items requested
        if offset_value + 50 >= 10000:
            limit = limit[:-2] + str(49)

        # Query IGDB with given url and added limit/offset
        response = unirest.get(url + limit + offset + str(offset_value),
                               headers={"X-Mashape-Key": key})

        # Add data to the list of all data, increment offset by 50
        response_list.extend(response.body)
        offset_value += 50

        # If we didn't get 50 items back, there's no more data to get
        if len(response.body) < 50:
            data_left = False

        # To show progress
        if len(response_list) % 500 == 0:
            print len(response_list)

    return response_list 


################################################################################
# URL get functions

# Each of the below specifies a certain endpoint for the API, the desired
# return fields (id, name, etc.) and any extra sorting/searching needed

# The URLs from these functions should be handed to make_request() to get data


def get_game_url():
    """Return all needed game data for most recent 10,000 in JSON object for seeding"""

    endpoint = "/games"

    field_list = ["id", "name", "summary", "storyline", "franchise", "genres",
                  "first_release_date", "videos", "cover", "developers",
                  "screenshots"]
    fields = "/?fields=" + "%2C".join(field_list) 

    sort_by = "&order=first_release_date%3Adesc"

    return base_url + endpoint + fields + sort_by


def get_franchise_url():
    """Return id and name from franchises"""

    endpoint = "/franchises"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    return base_url + endpoint + fields


def get_company_url(dev_id):
    """Return id and name from companies"""

    endpoint = "/companies"

    search = "/" + str(dev_id)

    field_list = ["name"]
    fields = "?fields=" + "%2C".join(field_list)

    return base_url + endpoint + search + fields


def get_genre_url():
    """Return id and name from genres"""

    endpoint = "/genres"

    field_list = ["id", "name"]
    fields = "/?fields=" + "%2C".join(field_list)

    return base_url + endpoint + fields


def get_platform_url():
    """Return id, name, and games list from platforms"""

    endpoint = "/platforms"

    field_list = ["id", "name", "games"]
    fields = "/?fields=" + "%2C".join(field_list)
    
    return base_url + endpoint + fields



