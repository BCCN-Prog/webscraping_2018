# webscraping_2018
This repository has the set of files that gather information from the websites bild.de and wetter.de as a webscraping service, and from the weather channel by RESTful API calls.
The scripts that __gather the data__ run on a server as cronjobs. The way they run is described by: `crontab_info.txt`

The structure for the RESTful API calls is the following:
  - `api_info.py` has the necessary information to access the wunderground API.
  
  - `constants.py` has the global constants used across API scripts.
  
  - `city_location.py` is the script that gets the coordinates of specified named cities.
  
  - `daily_structured.py` is the script that __gathers daily data__.
  
  - `hourly_structured.py` is the script that __gathers hourly data__.
  
