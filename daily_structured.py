import requests
import time
import datetime
import json
import constants
import pandas as pd
import pickle

def get_response(query):
    """
    Access wunderground API to do a get request
    """
    try:
        response = requests.get(constants.DAILY_BASE_URL + query+ ".json")
        return response.json() if response.ok else None
    except Exception as e:
        raise e

def extract_parameters(daily_forecast, city, data):
    date_ = daily_forecast.get('date')
    date_predicted = datetime.datetime.fromtimestamp(int(date_.get('epoch'))).strftime('%Y%m%d%H%M')
    temperature_max = daily_forecast.get('high').get('celsius')
    temperature_min = daily_forecast.get('low').get('celsius')
    wind_speed  = daily_forecast.get('avewind').get('kph')
    humidity    = daily_forecast.get('avehumidity')
    precipitation_per  = daily_forecast.get('pop')
    wind_direction = daily_forecast.get('avewind').get('dir')
    condition = daily_forecast.get('conditions') 
    snowcm = daily_forecast.get('snow_allday').get('cm')
    if snowcm: snow = snowcm * 10
    else: snow = snowcm
    UVI = None
    precipitation_l = None
    website = 'The Weather Channel'

    data['website'].append(website)
    data['city'].append(city)
    data['date_of_acquisition'].append(datetime.datetime.now().strftime('%Y%m%d%H'))
    data['date_for_which_weather_is_predicted'].append(date_predicted)
    data['temperature_max'].append(temperature_max)
    data['temperature_min'].append(temperature_min)
    data['wind_speed'].append(wind_speed)
    data['humidity'].append(humidity)
    data['precipitation_per'].append(precipitation_per )
    data['precipitation_l'].append(precipitation_l)
    data['wind_direction'].append(wind_direction)
    data['condition'].append(condition)
    data['snow'].append(snow)
    data['uvi'].append(UVI)
    return data

def gather_daily_city(city, data):
    latitude, longitude= constants.coordinates.get(city)
    location = str(latitude)+ "," + str(longitude)
    response = get_response(location)
    iterations = 100
    while(response == None and iterations > 0):
        response = get_response(location)
        time.sleep(10)
        iterations -= 1
    if(response == None):
        return data

    daily_forecasts = response.get("forecast").get("simpleforecast").get("forecastday")

    for daily_forecast in daily_forecasts:
        data = extract_parameters(daily_forecast, city, data)
    return data

def gather_daily_information():
    data = {
        'website' :  [],
        'city' : [],
        'date_of_acquisition' : [],
        'date_for_which_weather_is_predicted' : [],
        'temperature_max' : [],
        'temperature_min' : [],
        'wind_speed' : [],
        'humidity' : [],
        'precipitation_per' : [],
        'precipitation_l' : [],
        'wind_direction' : [],
        'condition' : [],
        'snow' : [],
        'uvi' : [],
    }
    for city in constants.coordinates.keys():
        data = gather_daily_city(city, data)

    df = pd.DataFrame(data)
    return df

df = gather_daily_information()

if(df.size > 0): 
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
    filename = "/home/danielv/Documents/webscraping_2018/data_daily/" + timestamp + ".pkl"
    df.to_pickle(filename)
