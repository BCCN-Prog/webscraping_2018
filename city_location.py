import requests
import time


def get_coordinates(city):
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + city)

    resp_json_payload = response.json()
    return resp_json_payload['results'][0]['geometry']['location']




def map_cities(cities):
    dic = {}
    for city in cities:
        time.sleep(5)
        print(city)
        coordinates = get_coordinates(city)
        dic[city] = (coordinates['lat'], coordinates['lng'])
        print()
        time.sleep(10)
        print(dic[city])
    return dic

cities=['BERLIN', 'HAMBURG', 'MUNICH', 'FRANKFURT', 'COLOGNE']
print(map_cities(cities))
