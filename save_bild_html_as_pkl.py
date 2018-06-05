
# coding: utf-8

# In[11]:

from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import os
import json
import pandas as pd
import urllib3
import pickle
import warnings



# In[8]:

cities=['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt']

base_urls=['https://wetter.bild.de/web2014/vorhersage-ort.asp?id=10115-berlin',
           'https://wetter.bild.de/web2014/vorhersage-ort.asp?id=22305-hamburg',
           'https://wetter.bild.de/web2014/vorhersage-ort.asp?id=80331-muenchen',
           'https://wetter.bild.de/web2014/vorhersage-ort.asp?id=50668-koeln',
           'https://wetter.bild.de/web2014/vorhersage-ort.asp?id=65931-frankfurt-am-main']


# In[9]:

def collect_htmls(city_base_url):
    http = urllib3.PoolManager()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category = urllib3.exceptions.InsecureRequestWarning)
        city_html = BeautifulSoup(http.request('GET', city_base_url).data, "html.parser")
        
    return city_html


# In[19]:

filename = '/home/danielv/Documents/webscraping_2018/data_bild_html/'
#filename = './'
for i,city in enumerate(cities):
    html_dict = {}
    current_time = pd.Timestamp(datetime.now())

    html_dict['website'] = 'www.bild.de'   
    html_dict['city'] = city
    html_dict['date_of_aquisition'] = str(current_time)
    html_dict['htmls'] = collect_htmls(base_urls[i])
    pkl_name=filename+city+str(current_time)[:13]+'.pkl'
    f = open(pkl_name,"wb")
    with open(pkl_name, 'w') as f:
        json.dump(html_dict,f)


# In[ ]:



