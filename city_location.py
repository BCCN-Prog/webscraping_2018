import requests
import time


def get_coordinates(city):
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + city)

    resp_json_payload = response.json()
    return resp_json_payload['results'][0]['geometry']['location']




def map_cities(cities):
    dic = {}
    for city in cities:
        print(city)
        dic[city] = get_coordinates(city)
        print()
        time.sleep(10)
    return dic
