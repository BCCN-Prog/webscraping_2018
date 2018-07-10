import pandas as pd
import os
import sys
import datetime

path = sys.argv[1]
for file_ in os.listdir(path):
    df = pd.read_pickle(path + file_)
    try:
        df.date_for_which_weather_is_predicted = df.date_for_which_weather_is_predicted.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M'))
        df.date_of_acquisition = df.date_of_acquisition.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H'))
    except: 
        try:
            df.date_of_acquisition = df.date_of_acquisition.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H'))
        except: pass
    finally:
        df.to_pickle(path + file_)
