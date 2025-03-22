import requests
from bs4 import BeautifulSoup
from database import get_db_connection, close_db_connection, get_episodes, update_episode_status, update_episode_text

conn = get_db_connection()

def getEpisodeText(url, hash):
  response = requests.get(url, allow_redirects=True)
  data = ''
  if response.status_code == 200:
    data = response.text
    # print(data)
    soup = BeautifulSoup(data, 'html.parser')
    post_body_div = soup.find('div', class_='post-body')
    
    # Extract all <p> tags inside the div
    if post_body_div:
        paragraphs = [p.get_text(strip=True) for p in post_body_div.find_all('p')]
        update_episode_text(conn, hash, str(paragraphs))
        update_episode_status(conn, hash, 'DONE')
        print(f'hash {hash} has been done!')
    else:
        print(f'hash {hash} error post_body_dev')
        return []
    
  else:
    print(f"Request failed with status code: {response.status_code}")

episodes = get_episodes(conn)
for episode in episodes:
  if episode[6] != 'DONE':
    getEpisodeText(episode[3], episode[0])

# getEpisodeText('https://virgool.io/@ali.nikoei1981/%D8%AF%D8%A7%D8%B3%D8%AA%D8%A7%D9%86%D9%90-%D8%AF%D8%A7%D8%B3%D8%AA%D8%A7%D9%86-%D9%87%D8%A7-%D8%AF%D8%A7%D8%B3%D8%AA%D8%A7%D9%86-%D9%87%D8%A7%DB%8C-%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87-%D9%81%D8%B1%D8%AF%D9%88%D8%B3%DB%8C-40-q1blt26ddzqx','q1blt26ddzqx')

close_db_connection(conn)