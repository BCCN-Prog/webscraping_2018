
# coding: utf-8

# In[23]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import timedelta
import pandas as pd
import urllib3
import datetime
import time
import os

# -*- coding: utf -*-


# In[24]:


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""
    
def cut_string(s, cut):
    try:
        cut_from = s.index(cut) + len(cut)
        return s[cut_from:]
    except ValueError:
        return ""


# In[25]:


class forecast(object):
    def __init__(max_temp, min_temp, proc_date, acc_date):
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.proc_date = proc_date
        self.acc_date = acc_date
        
def create_weather_df(url, http, current_time):
    
    data = {}
    soup = BeautifulSoup(http.request('GET',url).data,'lxml')
    daily_periods_dict = {}

    proc_date = []
    temp_min = []
    temp_max = []
    condition = []

    for day in range(15):
        dt = (current_time + timedelta(days=day)).date()
        proc_date.append(dt.strftime('%Y%m%d%H'))

    day_forcast = soup.findAll("div", {"class":'forecast-day'})
    for day in day_forcast:    

        temps = day.find('div', {"class":'forecast-day-temperature'})
        temp_min.append(int(temps.find('span', {'class':"wt-color-temperature-max"}).text[:-1]))
        temp_max.append(int(temps.find('span', {'class':"wt-color-temperature-min"}).text[:-1]))

        cond = str(day.find('div', {'class':"forecast-day-image"}))
        condition.append(find_between(cond,'<!-- key: ','  -->'))

    daily_periods_dict['date_for_which_weather_is_predicted'] = proc_date

    daily_periods_dict['temperature_min'] = temp_min
    daily_periods_dict['temperature_max'] = temp_max
    daily_periods_dict['condition'] = condition

    daily = pd.DataFrame(daily_periods_dict)
    return daily


# In[26]:


cities=['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt_am_Main']

urls=['https://www.wetter.de/deutschland/wetter-berlin-18228265/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-hamburg-18219464/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-muenchen-18225562/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-koeln-18220679/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-frankfurt-18221009/wetterprognose.html']

http = urllib3.PoolManager()
current_time = pd.Timestamp(datetime.datetime.now())
df = pd.DataFrame()

for i,city in enumerate(cities):
    url = urls[i]
    cdf = create_weather_df(url,http,current_time)    
    cdf['city'] = city
    df = df.append(cdf)

df['wind_speed'] = None
df['humidity'] = None
df['precipitation_per'] = None
df['precipitation_l'] = None
df['wind_direction'] = None
df['snow'] = None
df['UVI'] = None

df['website'] = 'https://www.wetter.de'
df['date_of_acquisition'] = current_time.strftime('%Y%m%d%H')
    
#pkl_name='./wetter_de/daily/'+current_time.strftime('%Y%m%d%H')+'.pkl'
filename = os.path.expanduser('~/Documents/webscraping_2018/data_wetter_de/daily')
timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
filename += timestamp + ".pkl"
df.to_pickle(filename)
