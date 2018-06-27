
# coding: utf-8

# In[51]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
#from datetime import datetime
from datetime import timedelta
import pandas as pd
import urllib3
import datetime
import time
import os
import db_manager

# -*- coding: utf -*-


# In[52]:


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


# In[53]:


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
    temp = []
    rain = []
    wind = []
    condition = []
    rain_l = []

    for day in range(15):
        for h in range(4):
            dt = (current_time + timedelta(days=day)).date()
            proc_date.append(datetime.datetime.combine(dt,datetime.time(h*6+2)).strftime('%Y%m%d%H'))

    period_forcast = soup.findAll("div", {"class":'forecast-column column-1 wt-border-radius-6'})
    for period in period_forcast:

        temp.append(int(period.find('div', {'class':"forecast-text-temperature wt-font-light"}).text[:-1]))
        condition.append(period.find('div', {'class':"forecast-column-condition"}).text)

        rain_html = period.find("div", {"class":'forecast-column-rain'})

        r = rain_html.findAll('span', {'class':"wt-font-semibold"})
        if len(r) > 1:
            rain.append(int(r[0].text[:-1]))
            rain_l.append(r[1].text[:-4])
        else:
            rain.append(int(rain_html.find('span', {'class':"wt-font-semibold"}).text[:-1]))    
            rain_l.append(None)

        wind_html = period.find("div", {"class":'forecast-column-wind'})
        wind.append(int(wind_html.find('span', {'class':"wt-font-semibold"}).text[1:-5])) 

    daily_periods_dict['date_for_which_weather_is_predicted'] = proc_date

    daily_periods_dict['temperature'] = temp
    daily_periods_dict['wind_speed'] = wind
    daily_periods_dict['precipitation_per'] = rain

    daily_periods_dict['precipitation_l'] = rain_l
    daily_periods_dict['condition'] = condition

    daily = pd.DataFrame(daily_periods_dict)
    return daily


# In[54]:


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

df['website'] = 'https://www.wetter.de'
df['wind_direction'] = None
df['date_of_acquisition'] = current_time.strftime('%Y%m%d%H')
    
# pkl_name='./wetter_de/day_periods/'+current_time.strftime('%Y%m%d%H')+'.pkl'
df.date_of_acquisition = df.date_of_acquisition.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H').date())
df.date_for_which_weather_is_predicted = df.date_for_which_weather_is_predicted.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M').date())

#pkl_name='./wetter_de/daily/'+current_time.strftime('%Y%m%d%H')+'.pkl'
try:
    db_manager.insert_df("DailyPeriodPrediction", df)
finally:
    filename = os.path.expanduser('~/Documents/webscraping_2018/data_wetter_de/day_periods')
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H')
    filename += timestamp + ".pkl"
    df.to_pickle(filename)



