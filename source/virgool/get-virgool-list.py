import requests
import re
from database import get_db_connection, close_db_connection, save_episode

conn = get_db_connection()

def getEpisodes(castName, castHash):
    hasMorePages = True
    page = 0
    while (hasMorePages):
        page += 1
        url = f"https://virgool.io/api2/app/playlists/{castHash}/sounds?page={page}&perPage=10"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if len(data['data']) == 0:
                hasMorePages = False
                break
            for episode in data['data']:
                if episode['post'] is not None:
                    save_episode(conn, episode['hash'], episode['post']['title'], episode['url'], episode['post']['url'], castHash, castName)
                else:
                    print(f"Skipping episode with hash {episode['hash']} because it has no post")
                    print(episode)
        else:
            print(f"Request failed with status code: {response.status_code}")

def getCasts():
    hasMorePages = True
    page = 0
    while (hasMorePages):
        page += 1
        url = "https://virgool.io/api2/app/playlists?page=" + str(page)

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if len(data['data']) == 0:
                hasMorePages = False
                break
            for cast in data['data']:
                castName = cast['name']
                castHash = cast['hash']
                print(f"Getting episodes for {castName}")
                getEpisodes(castName, castHash)
        else:
            print(f"Request failed with status code: {response.status_code}")


getCasts()

close_db_connection(conn)