import requests
import time
import json
KEY = "ba3288780ec658cc"
BASE_URL = "http://api.wunderground.com/api/"+ KEY +"/forecast10day/q/"
FILENAME = "Weather_forecast.json"
CITIES = ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"]
COUNTRY = "Germany"

def get_response(country, city):
	return requests.get(BASE_URL + country + "/" + city + ".json").json()

def collect_forecast(country, city):
	response = get_response(country, city)
	filename = str(time.time()) + "_" + country + "_" + city + "_" + FILENAME
	f = open(filename, 'w')
	json.dump(response, f)
	f.close()


[collect_forecast(COUNTRY, city) for city in CITIES]
