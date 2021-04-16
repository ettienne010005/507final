import requests
from bs4 import BeautifulSoup

baseurl = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Gainmoreran"

params = {"api_key":"RGAPI-0f5ba7c1-33e2-4a90-ab90-c337808009c6"}

response = requests.get(baseurl, params)
print(response.json())

site_url = "https://na.op.gg/champion/cassiopeia/statistics/mid"

html = requests.get(site_url).text
soup = BeautifulSoup(html, 'html.parser')
counter_champs = soup.find("table", class_="champion-stats-header-matchup__table champion-stats-header-matchup__table--strong tabItem")
# print(counter_champs.prettify())

