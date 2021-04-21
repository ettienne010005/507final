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
    rotation_api_url = "https://na1.api.riotgames.com/lol/platform/v3/champion-rotations"

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
            data = soup.find(class_="champion-box-content")
            script = data.find("script")
            rate_list = []
            date_list = []
            for i in script:
                s = str(i)
            l = s.split('\n')
            l2 = l[2].split(",")
            for i in range(8,33,5):
                if i == 8:
                    rate_list.append(l2[i][7:])
                else:
                    rate_list.append(l2[i][5:])
            for i in range(10,35,5):
                date_list.append(l2[i][13:-1])
            result = [rate_list,date_list]
            CACHE_DICT[base_url] = result
            save_cache(CACHE_DICT)
            return result

    elif request_type == "summoner_info" or request_type == "summoner_mastery" or request_type == "rotation":
        if request_type == "summoner_info":
            base_url = summoner_info_api_url
        elif request_type == "summoner_mastery":
            base_url = summoner_mastery_api_url
        elif request_type == "rotation":
            base_url = rotation_api_url
        
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

    if len(result_1) == 0 or len(result_2) == 0:
        return []

    return [result_1[0], result_2[0]]


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


def plotline(champ_name,lane,data):
    #plot the line chart with the given data
    xvals = data[1]
    yvals = data[0]
    scatter_data = go.Scatter(x=xvals, y=yvals,mode='lines+markers')
    basic_layout = go.Layout(title=f"Winning Rate for {champ_name} on {lane} lane")
    fig = go.Figure(data=scatter_data, layout=basic_layout)
    fig.show()


def plotbar(x_axis,y_axis,player_name):
    #plot the bar chart with the given data

    bar_data = go.Bar(x=x_axis, y=y_axis)
    basic_layout = go.Layout(title=f"Chiampion of Mastery for player: {player_name}")
    fig = go.Figure(data=bar_data, layout=basic_layout)

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
    #2. Top 3 Mastery Champions used by a given Summoner ID. Then plot the Line chart of the Mastery points for each champion
    #3. Plot the line chart of the winning trend of a given champion and lane
    #4. List free champions for this week

    while True:
        cmd = input("Enter the number of option you want:\n 1. compare two champions (<champ1_name> <champ2_name>)\n 2. Top 3 Mastery Champions used by a given Summoner ID(<Summoner_ID>)\n 3. The winning trend of a given champion and lane \n 4. List free champions for this week \nPlease enter number(1-3) or exit: ")
        if cmd == "exit":
            break
        print('\n')
        if cmd.isnumeric() and int(cmd) >=1 and int(cmd) <= 4:
            if cmd == '1':
                champ_string = input("1. compare two champions (<champ1_name> <champ2_name>)")
                champ_string = champ_string.lower()
                champ_list = champ_string.split()
                r = query_sql(champ_list)
                if len(r) == 0:
                    print("no results for champion name, please try again")
                else:
                    r1 = r[0]
                    r2 = r[1]
                    plot_radar(champ_list,r1,r2)
                    categories = ['Name','Hp','Mp','Move Speed',
                    'Armor', 'Attack Range', 'Attack Damage', 'Attack Speed']

                    #print data in prompt here
                    for i in categories:
                        print('{:<18}'.format(i), end="")
                    print('\n')
                    for x in range(3,11):
                        if x == 3:
                            print('{:<18}'.format(champ_list[0]), end="")
                        else:
                            print('{:<18}'.format(r1[x]), end="")
                    print('\n')
                    for x in range(3,11):
                        if x == 3:
                            print('{:<18}'.format(champ_list[1]), end="")
                        else:
                            print('{:<18}'.format(r2[x]), end="")
                    print('\n')
                
            
            elif cmd == '2':
                summoner_name = input("2. Top 3 Mastery Champions used by a given Summoner ID(<Summoner_ID>)")
                request_type = 'summoner_info'
                info = request_or_crawling_with_cache(request_type,'','',summoner_name,'')
                if 'id' not in info:
                    if info['status']['message'] == 'Forbidden':
                        print('Key Invalid')
                    else:
                        print(info['status']['message'])

                else:
                    champ_list = [] 
                    point_list = []
                    request_type = 'summoner_mastery'
                    data = request_or_crawling_with_cache(request_type,'','','',info['id'])
                    cnt = 0

                    for i in data:
                        point_list.append(i['championPoints']) 
                        for x in createdb_champ.champ_list:
                            if x[0] == i['championId']:
                                champ_list.append(x[1])
                        cnt = cnt +1
                        if cnt == 3:
                            break
                    #plot bar 
                    plotbar(champ_list,point_list,summoner_name)
                    # print cmd prompt 
                    print(f"{summoner_name} plays:\n{champ_list[0]} with {point_list[0]} points; \n{champ_list[1]} with {point_list[1]} points; \n{champ_list[2]} with {point_list[2]} points.")
                print('\n')

            elif cmd == '3':
                command = input('The winning trend of a given champion and lane(<lane> <champion_name>)')
                l = command.split()
                result = request_or_crawling_with_cache('winning_trend',l[1],l[0],'','')
                plotline(l[1],l[0],result)
                print(f'The Winning Rate for {l[1]} on {l[0]} lane')
                cnt = 0
                for i in result[1]:
                    if cnt == 0:
                        print('{:<13}'.format("Date :"), end="")
                    print('{:<13}'.format(i), end="")
                    cnt = cnt + 1
                print('\n')
                cnt = 0
                for i in result[0]:
                    if cnt == 0:
                        print('{:<13}'.format("Winning% :"), end="")
                    print('{:<13}'.format(i), end="")
                    cnt = cnt + 1
                print('\n')

            elif cmd == '4':
                result = request_or_crawling_with_cache('rotation','','','','') 
                if 'freeChampionIds' not in result:
                    print('Key Invalid')
                else:
                    print("Free Champions for this week are:")
                    for i in result['freeChampionIds']:
                        for x in createdb_champ.champ_list:
                            if x[0] == i:
                                print(x[1])

                print('\n')
        else:
            print("Error number of option. Please enter number 1-3")
