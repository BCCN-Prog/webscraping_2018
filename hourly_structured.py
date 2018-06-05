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
        response = requests.get(constants.BASE_URL + query+ ".json")
        return response.json() if response.ok else None
    except Exception as e:
        raise e


def collect_forecast_coords(coords, city):
    """
    Stores the json object corresponding to the weather forecast of city in a file.
    Parameters:
    coords: dictionary with the city names as keys, and tuple of coordinates as value
    city: name of the city in a string format 
    """
    latitude, longitude= constants.coordinates.get(city)
    location = str(latitude)+ "," + str(longitude)
    response = get_response(location)
    simple_forecast = response.get("hourly_forecast")
    filename = str(time.time()) + "_" + city + "_" + constants.FILENAME
    f = open(filename, 'w')
    json.dump(simple_forecast, f)
    f.close()

def extract_parameters(hourly_forecast, city, data):
    fcttime = hourly_forecast.get('FCTTIME')
    year, month, day, hour = fcttime.get('year'), fcttime.get('mon_padded'), fcttime.get('mday_padded'), fcttime.get('hour_padded')
    temperature = hourly_forecast.get('temp').get('metric')
    wind_speed  = hourly_forecast.get('wspd').get('metric')
    humidity    = hourly_forecast.get('humidity')
    precipitation_per = hourly_forecast.get('qpf').get('metric') #convert
    wind_direction = hourly_forecast.get('wdir').get('dir')
    condition = hourly_forecast.get('condition')
    snow = hourly_forecast.get('snow').get('metric')
    UVI = hourly_forecast.get('uvi')
    precipitation_l = None
    website = 'The Weaher Channel'

    data['website'].append(website)
    data['city'].append(city)
    data['date_of_acquisition'].append(datetime.datetime.now().strftime('%Y%m%d%H'))
    data['date_for_which_weather_is_predicted'].append(year + month + day + hour)
    data['temperature'].append(temperature)
    data['wind_speed'].append(wind_speed)
    data['humidity'].append(humidity)
    data['precipitation_per'].append(precipitation_per )
    data['precipitation_l'].append(precipitation_l)
    data['wind_direction'].append(wind_direction)
    data['condition'].append(condition)
    data['snow'].append(snow)
    data['uvi'].append(UVI)
    return data
    #df = pd.DataFrame(data, index=[0])

def gather_hourly_city(city, data):
    latitude, longitude= constants.coordinates.get(city)
    location = str(latitude)+ "," + str(longitude)
    response = get_response(location)
    hourly_forecasts = response.get("hourly_forecast")

    for hourly_forecast in hourly_forecasts:
        data = extract_parameters(hourly_forecast, city, data)
    return data

def gather_hourly_information():
    data = {
        'website' :  [],
        'city' : [],
        'date_of_acquisition' : [],
        'date_for_which_weather_is_predicted' : [],
        'temperature' : [],
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
        data = gather_hourly_city(city, data)
    df = pd.DataFrame(data)
    return df

df = gather_hourly_information()
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M')
filename = "/home/danielv/Documents/webscraping_2018/data_hourly/" + timestamp + ".pkl"
df.to_pickle(filename)
