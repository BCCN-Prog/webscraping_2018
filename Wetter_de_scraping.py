from bs4 import BeautifulSoup
import urllib3
import time
import datetime
import pandas as pd
import numpy as np
import pickle
import os


days_to_predict = 15
http = urllib3.PoolManager()
cities = ['Berlin','Hamburg', 'Munich', 'Cologne', 'Frankfurt']
cities_tags = ['berlin-18228265/' ,'hamburg-18219464/', 'muenchen-18225562/', 'koeln-18220679/', 'frankfurt-18221009/']
url_hourly_base = 'https://www.wetter.de/deutschland/wetter-'
tag_tags = ['tag-'+str(tag) for tag in range(9,days_to_predict+1)]
hourly_website_tags = ['wetterbericht-aktuell', 'wetterbericht-morgen', 'wetterbericht-uebermorgen','wetter-bericht','wettervorhersage','wetter-vorhersage','wettervorschau','wetter-vorschau']
hourly_website_tags.extend(tag_tags)

wind_mapping = { 'Nord': 'N', 'Ost':'E', 'West':'W', 'Süd':'S',
                'Nordost':'NE','Nordnordost':'NNE', 'Nordostost':'NEE',
                'Südost':'SE','Südsüdost':'SSE', 'Südostost':'SEE',
                'Ostnordost':'ENE', 'Ostsüdost':'ESE',
                'Nordwest':'NW', 'Nordnordwest':'NNW', 'Nordwestwest':'NWW',
                'Südwest':'SW', 'Südsüdwest':'SSW', 'Südwestwest':'SWW',
                'Westnordwest':'WNW', 'Westsüdwest':'WSW',
                'Ostnord':'EN', 'Ostostnord':'EEN', 'Ostnordnord':'ENN',
                'Westnord':'WN','Westwestnord':'WWN', 'Westnordnord':'WNN',
                'Nordostnord':'NEN', 'Nordwestnord':'NWN',
                'Ostsüd':'ES', 'Ostostsüd':'EES', 'Ostsüdsüd':'ESS',
                'Westsüd':'WS','Westwestsüd':'WWS', 'Westsüdsüd':'WSS',
                'Südostsüd':'SES', 'Südwestsüd':'SWS',
               }
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


number_of_features = 9 #e.g. date_for_which_weather_is_predicted, cities, temperature, wind ect.
number_of_cities = len(cities)
number_of_predictions = number_of_cities*len(hourly_website_tags)*25

current_time_date = datetime.datetime.now().strftime('%Y%m%d%H')
hourly_dict = {}
hourly_dict['website'] = ['Wetter.de']*number_of_predictions
hourly_dict['date_of_acquisition'] = [current_time_date]*number_of_predictions

all_features = np.empty((number_of_cities,len(hourly_website_tags),25,number_of_features), dtype=object)
for ci, city in enumerate(cities):
    url_hourly_base_city = url_hourly_base+cities_tags[ci]
    for i, tag in enumerate(hourly_website_tags):
        url = url_hourly_base_city+tag+'.html'
        soup = BeautifulSoup(http.request('GET',url).data, "html5lib")
        dates_for_predicted_days = [str(datetime.date.today() + datetime.timedelta(days=i)) for i in range(days_to_predict)]
        day_to_predict = dates_for_predicted_days[i].replace("-","")
        hourly_info = soup.findAll('div',class_="column column-4 forecast-detail-column-1h")
        for hi, info in enumerate(hourly_info):
            all_features[ci][i][hi][0] = city
            hour = info.find('div',class_="forecast-date").text[0:2]
            prediction_for = str(day_to_predict)+str(hour)
            all_features[ci][i][hi][1] = prediction_for
            temp_info = info.find('div', class_="forecast-temperature")
            temp = temp_info.find('span',class_="temperature").text.replace("°","")
            all_features[ci][i][hi][2] = temp
            wind_info = info.find('div',class_="forecast-wind")
            wind = wind_info.find('span',class_="wt-font-semibold").text.split("/")[0][1:-3]
            all_features[ci][i][hi][3] = wind
            humidity_info = info.find('div',class_="forecast-humidity-text")
            humidity = humidity_info.find('span',class_="wt-font-semibold").text.replace("%","")
            all_features[ci][i][hi][4] = humidity
            rain_info = info.find('div',class_="forecast-rain")
            rain_perecnt = rain_info.find('span',class_="wt-font-semibold").text.replace("%","")
            all_features[ci][i][hi][5] = rain_perecnt
            if int(rain_perecnt) > 0:
                rain_liter = rain_info.find_all('span',class_="wt-font-semibold")[-1].text.split("/")[0][0:-2]
                all_features[ci][i][hi][6] = rain_liter
            else:
                all_features[ci][i][hi][6] = None
            wind_text_ger = wind_info.find('div',class_="forecast-wind-text").text.split("aus")[1].split("\n")[0].replace(" ","")
            if wind_text_ger in wind_mapping:
                wind_text = wind_mapping[wind_text_ger]
            else:
                wind_text = None
            all_features[ci][i][hi][7] = wind_text
            temp_condition = temp_info.find('span',class_="temperature-condition").text
            all_features[ci][i][hi][8] = temp_condition
all_features = all_features.reshape(number_of_predictions,number_of_features)

hourly_dict['city'] = list(all_features[:,0])
hourly_dict['date_for_which_weather_is_predicted'] = list(all_features[:,1])
hourly_dict['temperature'] = list(all_features[:,2])
hourly_dict['wind_speed'] = list(all_features[:,3])
hourly_dict['humidity'] = list(all_features[:,4])
hourly_dict['precipation_per'] = list(all_features[:,5])
hourly_dict['precipation_l'] = list(all_features[:,6])
hourly_dict['wind_direction'] = list(all_features[:,7])
hourly_dict['condition'] = list(all_features[:,8])
hourly_dict['snow'] = [None]*number_of_predictions
hourly_dict['uvi'] = [None]*number_of_predictions

data_frame_daily = pd.DataFrame(data=hourly_dict)
filename = os.path.expanduser('~/Documents/webscraping_2018/data_wetter_de/hourly_period_')
timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
filename += timestamp + ".pkl"
data_frame_daily.to_pickle(filename)
