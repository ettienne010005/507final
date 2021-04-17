import requests
import createdb_champ
from bs4 import BeautifulSoup
import sqlite3
import API_key
import os.path
from os import path
import plotly.graph_objects as go 
import json


CACHE_FILENAME = "LOL_Cache.json"
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    #TODO Implement function
    response = requests.get(baseurl, params=params)
    return response.json()


def request_or_crawling_with_cache(request_type,champ_name,lane,summoner_name,encrypted_id):
    '''
    Parameters
    ----------
    request_type: string
        Whether the type of action is making requests or crawling webpage
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    base_url = ''
    top_champ_url = "https://www.op.gg/champion/statistics"
    winning_trend_champ_url = f"https://www.op.gg/champion/{champ_name}/statistics/{lane}"
     
    summoner_info_api_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    summoner_mastery_api_url = f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_id}"

    CACHE_DICT = open_cache()

    if request_type == "top_champ" or request_type == "winning_trend":
        # if the command is to Crawl the OPGG webpage
        if request_type == "top_champ":
            base_url = top_champ_url
        elif request_type == "winning_trend":
            base_url = winning_trend_champ_url

        if base_url in CACHE_DICT:
            print("Using Cache")
            return CACHE_DICT[base_url]
        else:
            print("Fetching")
            html = requests.get(base_url).text
            soup = BeautifulSoup(html, 'html.parser')
            #TODO: add parsing
            counter_champs = soup.find("table", class_="champion-stats-header-matchup__table champion-stats-header-matchup__table--strong tabItem")
            CACHE_DICT[base_url] = counter_champs
            save_cache(CACHE_DICT)
            return counter_champs

    elif request_type == "summoner_info" or request_type == "summoner_mastery":
        if request_type == "summoner_info":
            base_url = summoner_info_api_url
        elif request_type == "summoner_mastery":
            base_url = summoner_mastery_api_url
        
        if base_url in CACHE_DICT:
            print("Using Cache")
            return CACHE_DICT[base_url]
        else:
            print("Fetching")
            CACHE_DICT[base_url] = make_request(base_url,API_key.key)
            save_cache(CACHE_DICT)
            return CACHE_DICT[base_url]

def query_sql(champ_list):
    # query the database
    cursor = check_sql()
    
    query_1 = f'''
    SELECT * 
    From championData A, championID B
    Where B.ChampName = "{champ_list[0]}" and B.ChampId = A.Id
    '''
    result_1 = cursor.execute(query_1).fetchall()

    query_2 = f'''
    SELECT * 
    From championData A, championID B
    Where B.ChampName = "{champ_list[1]}" and B.ChampId = A.Id
    '''
    result_2 = cursor.execute(query_2).fetchall()

    return result_1[0], result_2[0]


def plot_radar(champ_list, result_1, result_2):
    # plot the radar plot for the given data
    categories = ['Hp','Mp','Move Speed',
              'Armor', 'Attack Range', 'Attack Damage', 'Attack Speed']

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[result_1[4],result_1[5],result_1[6],result_1[7],result_1[8],result_1[9],result_1[10]],
        theta=categories,
        fill='toself',
        name=champ_list[0]
    ))
    fig.add_trace(go.Scatterpolar(
        r=[result_2[4],result_2[5],result_2[6],result_2[7],result_2[8],result_2[9],result_2[10]],
        theta=categories,
        fill='toself',
        name=champ_list[1]
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0, 700]
        )),
    showlegend=False
    )

    fig.show()



def check_sql():
    #check whether the SQL database exists(create one if not) and return the cursor of them
    if not path.exists('champion.sqlite'):
        createdb_champ.createdb_data()
        print('create champion.sqlite')

    connection1 = sqlite3.connect('champion.sqlite')
    cursor_data = connection1.cursor()
        

    return cursor_data


if __name__ == "__main__":
    #Functionalities:
    #1. compare two champions : use Radar Charts to show each abilities
    #2. Top 3 Mastery Champions used by a given Summoner ID. Then plot the Line chart of the winning trend of the given champion
    #3. Most popular top five champion in a given lane: the ranking is plotted in Bar chart

    while True:
        cmd = input("Enter the number of option you want:\n 1. compare two champions (<champ1_name> <champ2_name>)\n 2. Top 3 Mastery Champions used by a given Summoner ID(<Summoner_ID>)\n 3. Most popular top five champion in a given lane \nPlease enter number(1-3) or exit: ")
        if cmd == "exit":
            break
        
        if cmd.isnumeric() and int(cmd) >=1 and int(cmd) <= 3:
            if cmd == '1':
                champ_string = input("1. compare two champions (<champ1_name> <champ2_name>)")
                champ_list = champ_string.split()
                r1,r2 = query_sql(champ_list)
                plot_radar(champ_list,r1,r2)
                #TODO: print data in prompt here
            
            elif cmd == '2':
                summoner_name = input("2. Top 3 Mastery Champions used by a given Summoner ID(<Summoner_ID>)")
                request_type = 'summoner_info'
                data = request_or_crawling_with_cache(request_type,'','',summoner_name,'')
                print(data)


            elif cmd == '3':
                pass

            
        else:
            print("Error number of option. Please enter number 1-3")

                
                







    # baseurl = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Gainmoreran"

    # params = {"api_key":"RGAPI-0f5ba7c1-33e2-4a90-ab90-c337808009c6"}

    # response = requests.get(baseurl, params)
    # print(response.json())

    # site_url = "https://na.op.gg/champion/cassiopeia/statistics/mid"

    # html = requests.get(site_url).text
    # soup = BeautifulSoup(html, 'html.parser')
    # counter_champs = soup.find("table", class_="champion-stats-header-matchup__table champion-stats-header-matchup__table--strong tabItem")
    # print(counter_champs.prettify())

    
