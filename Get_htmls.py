
# coding: utf-8

# In[24]:


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import pandas as pd
import urllib3
import pickle


# In[5]:


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


# In[6]:


cities=['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt am Main']

base_url=['https://www.wetter.de/deutschland/wetter-berlin-18228265/','https://www.wetter.de/deutschland/wetter-hamburg-18219464/','https://www.wetter.de/deutschland/wetter-muenchen-18225562/','https://www.wetter.de/deutschland/wetter-koeln-18220679/','https://www.wetter.de/deutschland/wetter-frankfurt-18221009/']


# In[18]:


def collect_htmls(city_base_url):
    raw_html=[]
    days_to_predict = 15
    http = urllib3.PoolManager()
    url_hourly_base = city_base_url
    tag_tags = ['tag-'+str(tag) for tag in range(9,days_to_predict+1)]
    hourly_website_tags = ['wetterbericht-aktuell', 'wetterbericht-morgen', 'wetterbericht-uebermorgen','wetter-bericht','wettervorhersage','wetter-vorhersage','wettervorschau','wetter-vorschau']
    hourly_website_tags.extend(tag_tags)
    for i, tag in enumerate(hourly_website_tags):
        url = url_hourly_base+tag+'.html'
        raw_html.append(simple_get(url))
        
    return raw_html


# In[26]:


for i,city in enumerate(cities):
    html_dict = {}
    current_time = pd.Timestamp(datetime.now())

    html_dict['website'] = 'www.wetter.de'   
    html_dict['city'] = city
    html_dict['date_of_aquisition'] = current_time
    html_dict['htmls'] = collect_htmls(base_url[i])
    pkl_name=city+str(current_time)[:10]+'.pkl'
    f = open(pkl_name,"wb")
    pickle.dump(html_dict,f)
    f.close()

