
# coding: utf-8

# In[5]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import timedelta
import pandas as pd
import urllib3
import datetime
import time

# -*- coding: utf -*-


# In[6]:


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


# In[7]:


class forecast(object):
    def __init__(max_temp, min_temp, proc_date, acc_date):
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.proc_date = proc_date
        self.acc_date = acc_date
        
def create_weather_df(url, http):
    
    data = {}
    soup = BeautifulSoup(http.request('GET',url).data,'lxml')
    daily_periods_dict = {}
    current_time = pd.Timestamp(datetime.datetime.now())

    proc_date = []
    temp_min = []
    temp_max = []
    condition = []

    for day in range(15):
        dt = (current_time + timedelta(days=day)).date()
        proc_date.append(dt)

    day_forcast = soup.findAll("div", {"class":'forecast-day'})
    for day in day_forcast:    

        temps = day.find('div', {"class":'forecast-day-temperature'})
        temp_min.append(int(temps.find('span', {'class':"wt-color-temperature-max"}).text[:-1]))
        temp_max.append(int(temps.find('span', {'class':"wt-color-temperature-min"}).text[:-1]))

        cond = str(day.find('div', {'class':"forecast-day-image"}))
        condition.append(find_between(cond,'<!-- key: ','  -->'))

    daily_periods_dict['website'] = 'https://www.wetter.de/deutschland/wetter-berlin-18228265/wetterprognose.html'
    daily_periods_dict['date_for_which_weather_is_predicted'] = proc_date
    daily_periods_dict['city'] = 'Berlin'
    daily_periods_dict['date_of_acquisition'] = current_time

    daily_periods_dict['temperature_min'] = temp_min
    daily_periods_dict['temperature_max'] = temp_max
    daily_periods_dict['condition'] = condition

    daily_periods_dict['wind_speed'] = None
    daily_periods_dict['humidity'] = None
    daily_periods_dict['precipation_per'] = None
    daily_periods_dict['precipation_l'] = None
    daily_periods_dict['wind_direction'] = None
    daily_periods_dict['snow'] = None
    daily_periods_dict['UVI'] = None

    daily = pd.DataFrame(daily_periods_dict)
    return daily


# In[8]:


cities=['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt_am_Main']

urls=['https://www.wetter.de/deutschland/wetter-berlin-18228265/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-hamburg-18219464/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-muenchen-18225562/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-koeln-18220679/wetterprognose.html',
      'https://www.wetter.de/deutschland/wetter-frankfurt-18221009/wetterprognose.html']

http = urllib3.PoolManager()

for i,city in enumerate(cities):
    url = urls[i]
    df = create_weather_df(url,http)
    current_time = pd.Timestamp(datetime.datetime.now())
    pkl_name='./wetter_de/wetter_de_day_periods_'+city+'_'+str(current_time)[:10]+'.pkl'
    df.to_pickle(pkl_name)

