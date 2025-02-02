import requests
from database import get_db_connection, close_db_connection, save_movie

conn = get_db_connection()

excist = True
page = 0
while excist:
    page = page + 1
    url = "https://www.filimo.com/api/fa/v1/movie/movie/loadmore/tagid/1/more_type/infinity/show_serial_parent/1/other_data/iran-fa_sub/perpage/100/page/" + str(page) + "?show_listinfo"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Mzg0MzkxOTYsImFmY24iOiIxNjkyNDg0MDMwMzQxNzQiLCJzdWIiOiJBRDI2MEM5NC04NTFGLTg3NTQtMTkwRi01REY2QzZERDhCNTMiLCJ0b2tlbiI6IjgyODdmZTlkMWU4MjhkYWVhMDRmMGU4NjYxOWY2ZDM1In0.xN7ddm_V6o4TDcILJmZMGRLwOTdYPvfWhkOugVTU-dk',
        'jsontype': 'simple',
        'priority': 'u=1, i',
        'referer': 'https://www.filimo.com/asparagus/tag/1/iran-fa_sub',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'trackerabtest': '{"snapppay_gateway":"gmd"}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        'useragent': '{"os":"react","pf":"site"}'
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        for movie in response.json()['data'][0]['movies']['data']:
            save_movie(conn, movie['id'], movie['uid'], movie['type'], movie['movie_title'])
        
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text) # Print the error message

    excist = response.json()['data'][0]['movies']['data'] != []

close_db_connection(conn)