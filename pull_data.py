import unirest
import os

def get_games_data():
    """Return all needed game data for most recent 10,000 in JSON object for seeding"""

    base_url = "https://igdbcom-internet-game-database-v1.p.mashape.com/games/?"

    fields = ("fields=*")
    limit = "&limit=50"
    offset = "&offset="
    offset_value = 0
    sort_by = "&order=first_release_date%3Adesc"

    key = os.environ["IGDB_API_KEY"]

    all_games = []
    games_left = True

    while games_left:
        if offset_value + 50 >= 10000:
            limit = "&limit=49"
        response = unirest.get(base_url + fields + limit + offset + str(offset_value),
                               headers={"X-Mashape-Key": key})
        all_games.extend(response.body)
        offset_value += 50
        if len(response.body) < 50:
            games_left = False
        print len(all_games)

    return all_games


