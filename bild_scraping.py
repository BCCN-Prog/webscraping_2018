# coding: utf-8
#
# Created by Pooja Subramaniam and Marc Aurel Vischer on Tue, May 8.
# Temperature is given as a tuple of daily high and low value, both in degrees Celsius as ints.
# Precipitation is given as "probability" as float.
# Wind is given as a tuple of strength in Bft (int) and direction
#(e.g. "NE" if wind _comes from_ north east).


import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import warnings
import os
import datetime
import db_manager

#FIRST PART: ONCE-A-DAY PREDICTIONS
#These are the urls referring directly to high, low temperature
hi_lo_url = "https://wetter.bild.de/web2014/ifr-wetter-deutschland.asp"
prec_url = "https://wetter.bild.de/web2014/ifr-niederschlag-deutschland.asp"
wind_url = "https://wetter.bild.de/web2014/ifr-windstaerken-deutschland.asp"

#load and parse page
http = urllib3.PoolManager()
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category = urllib3.exceptions.InsecureRequestWarning)
    hi_lo_bs = BeautifulSoup(http.request('GET', hi_lo_url).data, "html.parser")
    prec_bs = BeautifulSoup(http.request('GET',prec_url).data, "html.parser")
    wind_bs = BeautifulSoup(http.request('GET',wind_url).data, "html.parser")
#print(hi_lo.prettify())

#EXTRACT DATA AND SAVE INTO DICTIONARIES:
#TEMPERATURE HIGH/LOW, bild has today + 5 days forecast for that
#iterate over days, extract day layer for each
temp_dicts = []
for day in range(6):
    # extract current day layer
    day_layer = hi_lo_bs.find_all('div', id="wk_layer_wr{}".format(day))
    #print(day_layer[0]['id'])
    if len(day_layer)!=1:
        raise Exception("Found more than one layer for single day.")

    # extract all the cities from that layer
    day_cities = day_layer[0].find_all('div', class_="wk_map_text")
    day_dict = {}
    for city in day_cities:
        hi_lo_str = city.nobr.next_sibling.next_sibling
        high = int(hi_lo_str.split('|')[0].split('°')[0])
        low = int(hi_lo_str.split('|')[1].split('°')[0])
        day_dict[city.nobr.string] = (high, low)
    temp_dicts.append(day_dict)

#PRECIPITATION,  bild has only today + 2 days forecast for that
#iterate over days, extract day layer for each
prec_dicts = []
for day in range(1,4): #layer 0 corresponds to next 6 hrs, layer 1 to entire current day
    # extract current day layer
    day_layer = prec_bs.find_all('div', id="wk_layer_wr{}".format(day))
    #print(day_layer[0]['id'])
    if len(day_layer)!=1:
        raise Exception("Found more than one layer for single day.")

    # extract all the cities from that layer
    day_cities = day_layer[0].find_all('div', class_="wk_map_text")
    day_dict = {}
    for city in day_cities:
        prec_str = city.nobr.next_sibling.next_sibling
        prec_value = int(prec_str.split()[0])/100
        day_dict[city.nobr.string] = prec_value
    prec_dicts.append(day_dict)

#WIND,  bild again has today + 5 days forecast
WIND_GER_ENG = {"w":"W", "nw":"NW", "n":"N", "no":"NE", "o":"E", "so":"SE", "s":"S", "sw":"SW"}
#iterate over days, extract day layer for each
wind_dicts = []
for day in range(6):
    # extract current day layer
    day_layer = wind_bs.find_all('div', id="wk_layer_wr{}".format(day))
    #print(day_layer[0]['id'])
    if len(day_layer)!=1:
        raise Exception("Found more than one layer for single day.")

    # extract all the cities from that layer
    day_cities = day_layer[0].find_all('div', class_="wk_map_text")
    day_dict = {}
    for city in day_cities:
        wind_str = city.nobr.next_sibling.next_sibling
        wind_strength = int(wind_str.split()[0])
        wind_symbol_url = city.parent.img['src']
        wind_direction_raw = wind_symbol_url.split('.')[0].split('/')[-1]
        wind_direction = WIND_GER_ENG[wind_direction_raw]
        day_dict[city.nobr.string] = (wind_strength,wind_direction)
    wind_dicts.append(day_dict)

#BUNDLE THE INDIVIDUAL DICTIONARIES INTO A SINGLE DICT, SAVE AS PD DATAFRAME
date_of_acquisition = datetime.datetime.now() #for timestamp
website = ['Bild.de']
#storing cities as a dictionary of german name : english name,
#so .keys() and .values() gives the list of cities in german and english respectively
cities = {"Berlin":"Berlin", "Frankfurt":"Frankfurt", "Hamburg":"Hamburg",
          "Köln":"Cologne", "München":"Munich"}

daily_dict = {'website':[], 'date_for_which_weather_is_predicted':[], 'city':[],
              'date_of_aquisition':[], 'temperature_max':[], 'temperature_min':[],
              'wind_speed':[], 'humidity':[], 'precipitation_per':[],
              'precipitation_l':[], 'wind_direction':[], 'condition':[], 'snow':[], 'UVI':[]}


for i,city in enumerate(cities):
    for days in range(6):
        daily_dict['website'].append(website)
        daily_dict['date_for_which_weather_is_predicted'].append(
                datetime.datetime.now().strftime('%Y%m%d%H'))
        daily_dict['city'].append(cities[city])
        daily_dict['date_of_aquisition'].append(
                (date_of_acquisition+datetime.timedelta(days)).strftime('%Y%m%d%H'))
        daily_dict['temperature_max'].append(temp_dicts[days][city][0])
        daily_dict['temperature_min'].append(temp_dicts[days][city][1])
        daily_dict['wind_speed'].append(wind_dicts[days][city][0])
        daily_dict['wind_direction'].append(wind_dicts[days][city][1])
        daily_dict['wind_speed'].append(None)
        daily_dict['humidity'].append(None)

        #bild has precipitation forecasts only for the next 2 days
        if days<2:
            daily_dict['precipitation_per'].append(prec_dicts[days+1][city]*100)
        else:
            daily_dict['precipitation_per'].append(None)

        daily_dict['precipitation_l'].append(None)
        daily_dict['wind_direction'].append(None)
        daily_dict['condition'].append(None)
        daily_dict['snow'].append(None)
        daily_dict['UVI'].append(None)

DailyPrediction = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in daily_dict.items() ]))

filename = os.path.expanduser('~/Documents/webscraping_2018/data_bild/daily/daily_')
timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
filename += timestamp + ".pkl"
DailyPrediction.to_pickle(filename)

#SECOND PART: FOUR-TIMES-A-DAY PREDICTIONS
#scrape specified cities for morning, noon, afternoon, night, extract temperature,
# precipitation in percent and condition

PREDICTION_TIMES = [datetime.timedelta(days=0, hours=8), #morning
                    datetime.timedelta(days=0, hours=14), #afternoon
                    datetime.timedelta(days=0, hours=20), #evening
                    datetime.timedelta(days=1, hours=2)] #night (tomorrow)


#first we need the specific url for each city
city_query_url = 'https://wetter.bild.de/web2014/vorhersage-ort.asp?id='
city_ids_dict = {'Berlin': '10115-berlin',
                 'Frankfurt': '65931-frankfurt-am-main',
                 'Hamburg': '22305-hamburg',
                 'Köln' : '50668-koeln',
                 'München' : '80331-muenchen'}


#for the sake of clarity, i tried to be as consistent as possible with
#Pooja's code (daily_dict above) when it comes to saving the data as a dataframe
#
#data will be saved into this dictionary before being converted to a dataframe
daily_periods_dict = {'website':[],'date_for_which_weather_is_predicted':[],
                      'city':[],'time_for_which_weather_is_predicted':[],
                      #'date_of_acquisition':[],
                      'temperature':[],'wind_speed':[],'precipitation_per':[],
                      'precipitation_l':[],'wind_direction':[],'condition':[]}

for city in cities:
    #parse html for each city
    city_url = city_query_url + city_ids_dict[city]
    city_html = http.request('GET', city_url).data.decode('utf-8')
    #CAREFUL!!! there is a mistake in the website: there is a /span that doesn't have a match
    #we need to remove it manually before parsing
    city_html_fixed = city_html.replace("VORMITTAG</span>","VORMITTAG")
    city_bs = BeautifulSoup(city_html_fixed, "html.parser")

    #get the table containing the four-times-a-day forecast and extract the data
    four_table = city_bs.find_all('table', class_='wk_forecast_tbl')[1]
    # using the magic number here to index this is a bit shitty but there are several
    #tables that are all of the class 'wk_forecast_tbl'

    daytimes = four_table.find_all('td', class_="wk_bottomline wk_subheader")
    for i,daytime in enumerate(daytimes):
        siblings = [sibling for sibling in daytime.next_siblings]
        temp_raw = siblings[3]
        temp = int(temp_raw.text.split('°')[0])
        condition = siblings[5].text
        precip_raw = siblings[7].span.next_sibling.next_sibling.next_sibling.next_sibling
        precip = int(precip_raw.split('%')[0])
        #a bit of date arithmetic here:
        today_00 = datetime.datetime.combine(
                datetime.date.today(), datetime.time(0,0,0)) #gives today at 00
        prediction_datetime = today_00 + PREDICTION_TIMES[i] #time delta from today 00:00

        daily_periods_dict['website'].append(city_url)
        daily_periods_dict['date_for_which_weather_is_predicted'].append(
            prediction_datetime.strftime('%Y%m%d%H'))
        daily_periods_dict['city'].append(city)
        #this is a duplicate of date_for_which_weather_is_predicted, don't know why we need it here
        daily_periods_dict['time_for_which_weather_is_predicted'].append(
            prediction_datetime.strftime('%Y%m%d%H'))
        #would have been nice to know, don't know why it's not in the standard
        #daily_periods_dict['date_of_acquisition'].append(
        #    datetime.datetime.now().strftime('%Y%m%d%H'))
        daily_periods_dict['temperature'].append(temp)
        daily_periods_dict['wind_speed'].append(None)
        daily_periods_dict['precipitation_per'].append(precip)
        daily_periods_dict['precipitation_l'].append(None)
        daily_periods_dict['wind_direction'].append(None)
        daily_periods_dict['condition'].append(condition)


#convert to dataframe and save to file
df = pd.DataFrame(daily_periods_dict)
try:
    pass
    db_manager.insert_df("DailyPeriodPrediction", df)
finally:
    filename = os.path.expanduser('~/Documents/webscraping_2018/data_bild/daily_period/daily_period_')
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
    filename += timestamp + ".pkl"
    df.to_pickle(filename)
