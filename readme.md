Final project for SI 507 final
League of Legends Player stats and Champion stats Program


Data source:
1. Riot API https://developer.riotgames.com/apis for API 
2. OP.GG https://www.op.gg/ for crawling data
3. champions.json from Github https://github.com/ngryman/lol-champions for champion detailed data and turned into SQL database


API keys:
The API keys need to get from https://developer.riotgames.com/ and It will expire in every 24 hours. In order to run this program, the user has to get a key and put it inside a file called API_key.py. 


Packages in this program:
1.	BeautifulSoup
2.	Plotly
3.	Requests
4.	sqlite3


Functionalities:
1.	Compare two champions’ data from the SQL database(Data retrieved from champion.json): use Radar Charts to show each abilities and also printed in command line prompt.
The user will have to provide two champion names in this option
2.	Top 3 Mastery Champions used by a given Summoner(Player) ID. Data is retrieved from the RIOT API. Then plot the Bar chart of the Mastery points for each of the top 3 champions and also printed in command line prompt.
The user will have to provide one summoner name in this option
3.	The winning trend of a given champion and lane. Data is retrieved from the OP.GG website by crawling .The winning percentage and date are plotted in Line chart and also printed in command line prompt.
The user will have to provide one champion name and it’s lane
4.	List free champions for this week. Data is retrieved from RIOT API. Then the Champion names will be printed in the command line prompt.
The user do not have to provide anything in this option

