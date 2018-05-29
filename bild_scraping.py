
# coding: utf-8

# Created by Pooja Subramaniam and Marc Aurel Vischer on Tue, May 8.

# Temperature is given as a tuple of daily high and low value, both in degrees Celsius as ints.
# 
# Precipitation is given as "probability" as float.
# 
# Wind is given as a tuple of strength in Bft (int) and direction (e.g. "NE" if wind _comes from_ north east).

# In[76]:

import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import warnings


# In[77]:

#These are the urls referring directly to high, low temperature
hi_lo_url = "https://wetter.bild.de/web2014/ifr-wetter-deutschland.asp"
prec_url = "https://wetter.bild.de/web2014/ifr-niederschlag-deutschland.asp"
wind_url = "https://wetter.bild.de/web2014/ifr-windstaerken-deutschland.asp"


# In[78]:

#load and parse page
http = urllib3.PoolManager()
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category = urllib3.exceptions.InsecureRequestWarning)
    hi_lo_bs = BeautifulSoup(http.request('GET', hi_lo_url).data, "html.parser")
    prec_bs = BeautifulSoup(http.request('GET',prec_url).data, "html.parser")
    wind_bs = BeautifulSoup(http.request('GET',wind_url).data, "html.parser")
#print(hi_lo.prettify())


# In[79]:

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


# In[80]:

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


# In[81]:

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


# In[82]:

import time
import datetime

Date_of_acquisition = datetime.datetime.now()
Website = ['Bild.de']
City = {"Berlin":"Berlin", "Frankfurt":"Frankfurt", "Hamburg":"Hamburg", "Köln":"Cologne", "München":"Munich"}


Daily_dict = {'Date_of_acquisition':[],'Website':[],'City':[],
              'Date_of_prediction':[],'high_temp':[],'low_temp':[],'wind_speed':[],'wind_direction':[], 'precipitation':[]}


# In[83]:

for i,city in enumerate(City):
    for days in range(6):
        
        Daily_dict['Date_of_acquisition'].append(datetime.datetime.now().strftime('%Y%m%d%H'))
        Daily_dict['Website'].append(Website)
        Daily_dict['City'].append(City[city])
        Daily_dict['Date_of_prediction'].append(Date_of_acquisition+datetime.timedelta(days))
        Daily_dict['high_temp'].append(temp_dicts[days][city][0])
        Daily_dict['low_temp'].append(temp_dicts[days][city][1])
        Daily_dict['wind_speed'].append(wind_dicts[days][city][0])
        Daily_dict['wind_direction'].append(wind_dicts[days][city][1])

        if days<2:
            Daily_dict['precipitation'].append(prec_dicts[days+1][city]*100)
            


# In[84]:

Daily = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in Daily_dict.items() ]))


# In[85]:

# filename = '/home/danielv/webscraping_2018/data_bild/'
filename = './'
timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
pd.DataFrame.to_csv(Daily, filename + timestamp)

