# -*- coding: utf-8 -*-
"""
"""

# This part of code scraps the data from Kijiji


#!pip install selenium 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome('chromedriver.exe')
from bs4 import BeautifulSoup # For HTML parsing
import requests # Website connections
from time import sleep # To prevent overwhelming the server between connections
from collections import Counter # Keep track of our term counts
import pandas as pd # For converting results to a dataframe and bar chart plots
import json # For parsing json
import random
#%matplotlib inline
from os.path import exists
import datetime
import sys
import traceback
import os

# **** input parameters begin
# the name of province was choosen manually. I can write 'for-loop' to download data province by 
#province (or randomly choose a province for every next listing), but I wanted to have a control 
#over the process. As the time of the task was limited, I downloaded the data and tested the 
#scrapping part of the code at the same time.
province = 'ontario'
#the path to the file data are saved to
data_file = os.path.dirname(sys.argv[0]) + '/data/kittens2.csv' 

#for debugging purposes it is possible to limit the amount of records downloaded for each page
#if zero, all recorrds will be downloaded
max_counter = 0
# **** input parameters end

# The list of the urls for different provinces is created, to filter by province
province_urls = [ 'https://www.kijiji.ca/b-cats-kittens/alberta/c125l9003','https://www.kijiji.ca/b-cats-kittens/british-columbia/c125l9007','https://www.kijiji.ca/b-cats-kittens/manitoba/c125l9006','https://www.kijiji.ca/b-cats-kittens/new-brunswick/c125l9005','https://www.kijiji.ca/b-cats-kittens/newfoundland/c125l9008','https://www.kijiji.ca/b-cats-kittens/nova-scotia/c125l9002','https://www.kijiji.ca/b-cats-kittens/ontario/c125l9004','https://www.kijiji.ca/b-cats-kittens/prince-edward-island/c125l9011','https://www.kijiji.ca/b-cats-kittens/saskatchewan/c125l9009','https://www.kijiji.ca/b-cats-kittens/territories/c125l9010','https://www.kijiji.ca/b-chats-chatons/quebec/c125l9001']

#the dictionary of the province name and the province code used in url is created
province_urls = {x.split('/')[-2]:x.split('/')[-1] for x in province_urls}

# The function generated the url for the province and page number given
def get_page_url(page_num, province): 
    province_code = province_urls[province] # find the province code for province name in dictionary
    if page_num == 1:  # created page url differently for page number 1
        page_name = ''
    else:               #and any different page number, except for page number 1
        page_name = f'page-{page_num}/'
    return f'https://www.kijiji.ca/b-cats-kittens/{province}/{page_name}{province_code}'

# the function scrap data from the given page
def scrab_record(page_url):
    driver.get(page_url) #the page for particular listing opens using Selenium
    html = driver.execute_script("return document.documentElement.innerHTML")
    #result = requests.get(page_url)
    #soup = BeautifulSoup(result.content)
    soup = BeautifulSoup(html) #the data are scrapped using BeautifulSoup
    
    #the function scraps description, owner_id and number of listing made by every owner
    description_ = soup.find('div', itemprop ="description")
    owner_id_ = soup.find('div', class_ = "itemInfoSidebar-408428561").find('a', class_ = 'link-2686609741')
    num_listing = soup.find('div', class_ = "itemInfoSidebar-408428561").contents[2].contents[0].contents[1].find('span').get_text()
        
    description  = description_.get_text()  
    owner_id = owner_id_.get('href').split('/')[2] #the exact owner id returns (unique owner identificator)
    
    return description, owner_id, num_listing   

#the scrapped data are downloaded to the file
# the set of processed record_id is created. The record_id is the unique identificator of the listing
#in order to avoid dublicates, all record_ids are saved in the set
#if file exists, the set is taken from the downloaded record_ids
#if file does not exist, the set is an empty set. File is created, and data columns names are defined
if exists(data_file): 
    df = pd.read_csv(data_file, dtype = {'Record_id':str}) 
    processed_records = set(df['Record_id'].values)  
    f = open(data_file, 'a', encoding = 'utf-8')  
else:
    processed_records = set()
    f = open(data_file, 'w', encoding = 'utf-8')
    f.write(','.join(['Record_id', 'Province', 'Current_time', 'Date', 'Title', 'Price', 'Location', 'Owner_id', 'Num_listing', 'Url', 'Description']))
    f.write('\n')

#the main part of the data scrapping code
for page_num in range(1, 101): #the maximum number of pages per province is 100
    page_url = get_page_url(page_num, province) #page url is created
    result = requests.get(page_url) #BeautifulSoup initiated 
    soup = BeautifulSoup(result.content)                 
    print('loading page ' + str(page_num)) #the message of what page's listings are downloaded is printed
    date_now = datetime.datetime.now() 
    current_date = datetime.datetime.strftime(date_now, '%Y-%m-%d %H:%M:%S') 
#as some listings' date is downloaded as 'Yesterday' or 'X hours ago', the current date and time
#is added to every row of data (to every listing record)
    
    i = 0
#from each page the info of price, title, record_id, location and date are scrapped
    for container in soup.find_all('div', class_ = 'info-container'):
        if max_counter > 0 and i >= max_counter:
            break
        i += 1
        price_ = container.find('div', class_ = 'price') #price of the listing
        title_ = container.find('div', class_ = 'title') #title of the listing
        url_ = title_.contents[1]
        url = url_['href'] #url of the listing
        record_id = url.split('/')[-1] #record_id (unique identifier) of the listing
        if record_id in processed_records: #check if record_id was already processed, and skip if it was
            continue
#if record was not processed yet, the page url for the listing created to open with Selenium 
#I have to use Selenium here, as otherwise some fields are not available to download
        url = 'https://kijiji.ca'+url

#the location, price, title and date information are scrapped
        location_ = container.find('div', class_ = 'location')

        price = price_.text.strip().replace(',', '')
        title = title_.contents[1].get_text().strip().replace(',', ' ').replace('\n', ' ')
        
        location = location_.contents[1].get_text().strip().replace(',', ' ')
        date = location_.contents[3].get_text().strip()

#the separate page for the listing opens (with try/except command)
        try:

            sleep(random.randint(3,20)) #the sleep set up 
            #the function to scrap description, owner_id, num_listing is called
            description, owner_id, num_listing = scrab_record(url) 
            #the record_id is added to the set of record_ids
            processed_records.add(record_id)
            #downloaded fields are cleaned
            description = description.strip().replace(',', ' ')
            description = description.strip().replace('\n', ' ')
            owner_id = owner_id.strip().replace(',', '')
            num_listing = num_listing.strip().replace(',', '')
#downloaded fields are added to the file with data
            f.write(','.join([record_id, province, current_date, date, title, price, location, owner_id, num_listing, url, description]))
            f.write('\n')
        #as some of the listings were not downloaded, the error description is created
        except Exception as e:
            print('error', e.__class__, 'occurred', str(e))
            print(traceback.format_exc())
            print('error while loading record {},url = {}'.format(record_id, url))
        f.flush() #force data in buffer to be saved to file
        
f.close() #the file closes after all info for the province is downloaded
                  