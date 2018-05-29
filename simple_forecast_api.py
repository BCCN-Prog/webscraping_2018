import requests
import time
import json
import constants

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
    filename = constants.FOLDERNAME + str(round(time.time())) + "_" + city + "_" + constants.FILENAME
    f = open(filename, 'w')
    json.dump(simple_forecast, f)
    f.close()

[collect_forecast_coords(constants.coordinates, city) for city in constants.coordinates.keys()]
