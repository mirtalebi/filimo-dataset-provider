import os
import requests
from pathlib import Path

def downloadMovieAudio(movieKey, link):
    result = os.system('ffmpeg -i "'+ link + '" ./../../filimo/' + movieKey +'/' + movieKey + '.mp3')
    if result != 0:
        print('ERROR_WHILE_DOWNLOADING_AUDIO')

    return result == 0

def getLinks(movieKey):
    url = "https://api.filimo.com/api/fa/v1/movie/watch/watch/uid/" + movieKey

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Mzg0MzkxOTYsImFmY24iOiIxNjkyNDg0MDMwMzQxNzQiLCJzdWIiOiJBRDI2MEM5NC04NTFGLTg3NTQtMTkwRi01REY2QzZERDhCNTMiLCJ0b2tlbiI6IjgyODdmZTlkMWU4MjhkYWVhMDRmMGU4NjYxOWY2ZDM1In0.xN7ddm_V6o4TDcILJmZMGRLwOTdYPvfWhkOugVTU-dk",
        "origin": "https://www.filimo.com",
        "priority": "u=1, i",
        "referer": "https://www.filimo.com/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "trackerabtest": '{"snapppay_gateway":"gmd"}',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "useragent": '{"os":"react","pf":"site"}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Links gotten successfully")

        sublink = ''
        if 'tracks' not in response.json()['data']['attributes'] or not response.json()['data']['attributes']['tracks']:
            print(f"NO_TRACKS: {response.status_code}")
            return []
        for subtitle in response.json()['data']['attributes']['tracks']:
            if subtitle['srclang'] == 'fa':
                sublink = subtitle['src']
                break
        if sublink == '':
            print(f"NO_FA_TRACKS: {response.status_code}")
            return []
    

        return [response.json()['data']['attributes']['multiSRC'][0][0]['src'], sublink]
    
    else:
        print(f"GET_LINKS_ERROR: {response.status_code}")
        return []
    
def downloadSubtitle(movieKey, sublink):
    Path('./../../filimo/' + movieKey +'/').mkdir(parents=True, exist_ok=True)
    subtitle = requests.get(sublink)
    with open('./../../filimo/' + movieKey +'/' + movieKey + '.srt', 'wb') as file:
        file.write(subtitle.content)

def proccessMovie(movieKey):
    links = getLinks(movieKey)
    if len(links) == 0:
        return False
    
    downloadSubtitle(movieKey, links[1])
    
    result = downloadMovieAudio(movieKey, links[0])
    if not result:
        return False
    
    return True

print(getLinks('lvk80'))