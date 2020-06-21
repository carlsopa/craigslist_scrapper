from bs4 import BeautifulSoup
import json
from requests import get
import numpy as np
import pandas as pd
import csv
from fuzzywuzzy import fuzz as fw
import re

print('Craigs list appartment scrapper')
#get the initial page for the listings, to get the total count

neighborhood = []
bedroom_count =[]
sqft = []
price = []
link = []
title = []
post_id = []
#count = 0
def Analyze(data_frame):
    neighborhood_unique_list = []
    neighborhood_max_list = []
    neighborhood_min_list = []
    neighborhood_mean_list = []
    neighborhood_list = data_frame.neighborhood.unique()
    for index,value in enumerate(neighborhood_list):
        max_price = (data_frame.loc[data_frame['neighborhood']==neighborhood_list[index]].price.max())
        min_price = (data_frame.loc[data_frame['neighborhood']==neighborhood_list[index]].price.min())
        mean_price = int((data_frame.loc[data_frame['neighborhood']==neighborhood_list[index]].price.mean()))
        neighborhood_unique_list.append(value)
        neighborhood_max_list.append(max_price)
        neighborhood_min_list.append(min_price)
        neighborhood_mean_list.append(mean_price)
    pd.DataFrame({'neighborhood':neighborhood_unique_list,'max price':neighborhood_max_list,'min price':neighborhood_min_list,'average price':neighborhood_mean_list}).to_csv('neighborhood_analyze.csv',index=False)

def FuzzyComparision(data_frame):
    for i in range(len(data_frame)):
    	for j in range(i + 1, len(data_frame)):
    		ratio = fw.partial_ratio(data_frame['neighborhood'][i].lower(),data_frame['neighborhood'][j].lower())
    		if ratio>90:
    			data_frame['neighborhood'][j] = data_frame['neighborhood'][i]
    data_frame['neighborhood'].to_csv('neighborhood_clean_a.csv',index=False)

def Serialize(data_frame):
    
    data_frame['footage'] = data_frame['footage'].replace(0,np.nan)
    data_frame['bedroom'] = data_frame['bedroom'].replace(0,np.nan)
    data_frame['neighborhood'] = data_frame['neighborhood'].str.strip().str.strip('(|)')
    data_frame['neighborhood'] = data_frame['neighborhood'].str.lower()
    pd.set_option('display.width',None)

    FuzzyComparision(data_frame)

    print(len(data_frame))
    data_frame = data_frame.drop_duplicates('title')
    data_frame = data_frame.drop_duplicates(['footage','bedroom','price'])
    print(len(data_frame))
    data_frame = data_frame.dropna(subset=['footage','bedroom'],how='all')
    data_frame.to_csv("rent_clean.csv",index=False)

def bedroom(post):
    if post.find(class_='housing') is not None:
        if 'ft2' in post.find(class_='housing').text.split()[0]:
            post_bedroom = np.nan
            post_footage = post.find(class_='housing').text.split()[0][:-3]
            bedroom_count.append(post_bedroom)
            sqft.append(post_footage)
        elif len(post.find(class_='housing').text.split())>2:
            post_bedroom = post.find(class_='housing').text.replace("br","").split()[0]
            post_footage = post.find(class_='housing').text.split()[2][:-3]
            bedroom_count.append(post_bedroom)
            sqft.append(post_footage)
        elif len(post.find(class_='housing').text.split())==2:
            post_bedroom = post.find(class_='housing').text.replace("br","").split()[0]
            post_footage = np.nan
            bedroom_count.append(post_bedroom)
            sqft.append(post_footage)
    else:
        post_bedroom = np.nan
        post_footage = np.nan
        bedroom_count.append(post_bedroom)
        sqft.append(post_footage)

def neighborhood_data(post):
    post_url = post.find(class_='result-title hdrlnk')
    post_link = post_url['href']
    link.append(post_link)
    post_id.append(str(post_url['data-id']))
    title.append(post_url.text)
    post_neighborhood = post.find(class_='result-hood').text
    post_price = int(post.find(class_='result-price').text.strip().replace('$',''))
    neighborhood.append(post_neighborhood)
    price.append(post_price)


def initData(url):
    response = get(url)
    html_result = BeautifulSoup(response.text, 'html.parser')
    results = html_result.find('div', class_='search-legend')
    total = int(results.find(class_='totalcount').text)
    pages = np.arange(0,total+1,120)
    return(pages)

def scrapData(pages,url):
    for page in pages:
        print('scrapping results: '+str(page)+' of '+str(pages[-1]))
        response = get(url+str(page))

        html_result = BeautifulSoup(response.text, 'html.parser')

        posts = html_result.find_all(class_='result-row')
        for post in posts:
            if post.find(class_='result-hood') is not None:
                neighborhood_data(post)
                bedroom(post)

    
#script to actual scrap craigs list
scrapData(initData('https://washingtondc.craigslist.org/search/apa'),'https://washingtondc.craigslist.org/search/apa?s=')
data_frame = pd.DataFrame({
    'id':post_id,
    'title':title,
    'neighborhood':neighborhood,
    'footage':sqft,
    'bedroom':bedroom_count,
    'price':price,
    'link':link})

Serialize(data_frame)
Analyze(data_frame)

