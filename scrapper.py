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

washer_dryer =[]
washer_dryer_title = []
washer_dryer_id = []
washer_footage = []
washer_bedroom = []
washer_price = []
washer_neighborhood = []

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

def Serialize(data_frame,file):
    
    data_frame['footage'] = data_frame['footage'].replace(0,np.nan)
    data_frame['bedroom'] = data_frame['bedroom'].replace(0,np.nan)
    data_frame['neighborhood'] = data_frame['neighborhood'].str.strip().str.strip('(|)')
    data_frame['neighborhood'] = data_frame['neighborhood'].str.lower()
    pd.set_option('display.width',None)

    FuzzyComparision(data_frame)

    data_frame = data_frame.drop_duplicates('title')
    data_frame = data_frame.drop_duplicates(['footage','bedroom','price'])
    print(len(data_frame))
    data_frame = data_frame.dropna(subset=['footage','bedroom'],how='all')
    data_frame.to_csv(file+".csv",index=False)

def bedroom(post):
    a_bedroom_count = []
    a_sqft = []
    if post.find(class_='housing') is not None:
        if 'ft2' in post.find(class_='housing').text.split()[0]:
            post_bedroom = np.nan
            post_footage = post.find(class_='housing').text.split()[0][:-3]
            a_bedroom_count.append(post_bedroom)
            a_sqft.append(post_footage)
        elif len(post.find(class_='housing').text.split())>2:
            post_bedroom = post.find(class_='housing').text.replace("br","").split()[0]
            post_footage = post.find(class_='housing').text.split()[2][:-3]
            a_bedroom_count.append(post_bedroom)
            a_sqft.append(post_footage)
        elif len(post.find(class_='housing').text.split())==2:
            post_bedroom = post.find(class_='housing').text.replace("br","").split()[0]
            post_footage = np.nan
            a_bedroom_count.append(post_bedroom)
            a_sqft.append(post_footage)       
    else:
        post_bedroom = np.nan
        post_footage = np.nan
        a_bedroom_count.append(post_bedroom)
        a_sqft.append(post_footage)
    return(post_bedroom,post_footage)

def neighborhood_data(post):
    post_url = post.find(class_='result-title hdrlnk')
    post_link = post_url['href']
    link.append(post_link)
    post_id.append(str(post_url['data-id']))
    title.append(post_url.text)
    post_neighborhood = post.find(class_='result-hood').text
    post_price = int(post.find(class_='result-price').text.strip().replace('$',''))
    return(post_neighborhood,post_price)



def initData(url):
    response = get(url)
    html_result = BeautifulSoup(response.text, 'html.parser')
    results = html_result.find('div', class_='search-legend')
    total = int(results.find(class_='totalcount').text)
    pages = np.arange(0,total+1,120)
    return(pages)

def Posts(page,pages,url):
    print('scrapping results: '+str(page)+' of '+str(pages[-1]))
    response = get(url+str(page))

    html_result = BeautifulSoup(response.text, 'html.parser')

    return(html_result.find_all(class_='result-row'))
def WasherDryer(post):
    post_url = post.find(class_='result-title hdrlnk')
    washer_dryer_id.append(str(post_url['data-id']))
    washer_dryer.append(True)
    washer_dryer_title.append(post_url.text)
    post_price = int(post.find(class_='result-price').text.strip().replace('$',''))
    #washer_price.append(post_price)
    post_neighborhood = post.find(class_='result-hood').text
    #washer_neighborhood.append(post_neighborhood)

    
    

def scrapData(pages,url,type):
    
    for page in pages:
        
        # print('scrapping results: '+str(page)+' of '+str(pages[-1]))
        # response = get(url+str(page))

        # html_result = BeautifulSoup(response.text, 'html.parser')

        # posts = html_result.find_all(class_='result-row')
        for post in Posts(page,pages,url):
            if type == 'Washer_Dryer':
                if post.find(class_='result-hood') is not None:
                    WasherDryer(post)
                    n_result = neighborhood_data(post)
                    b_result = bedroom(post)
                    washer_neighborhood.append(n_result[0])
                    washer_price.append(n_result[1])
                    washer_bedroom.append(b_result[0])
                    washer_footage.append(b_result[1])
            elif type == 'Bed':
                if post.find(class_='result-hood') is not None:
                    n_result = neighborhood_data(post)
                    b_result = bedroom(post)
                    neighborhood.append(n_result[0])
                    price.append(n_result[1])
                    bedroom_count.append(b_result[0])
                    sqft.append(b_result[1])


#script to actual scrap craigs list
scrapData(initData('https://washingtondc.craigslist.org/search/apa'),'https://washingtondc.craigslist.org/search/apa?s=','Bed')

# scrapData(initData('https://washingtondc.craigslist.org/search/apa?laundry=1&sale_date=all+dates'),'https://washingtondc.craigslist.org/search/apa?laundry=1&s=','Washer_Dryer')

data_frame = pd.DataFrame({
    'id':post_id,
    'title':title,
    'neighborhood':neighborhood,
    'footage':sqft,
    'bedroom':bedroom_count,
    'price':price,
    'link':link})
Serialize(data_frame,'rent_clean')
# Analyze(data_frame)
#print(washer_dryer_id)

scrapData(initData('https://washingtondc.craigslist.org/search/apa?laundry=1&sale_date=all+dates'),'https://washingtondc.craigslist.org/search/apa?laundry=1&s=','Washer_Dryer')

washer_dryer_data_frame = pd.DataFrame({
    'id':washer_dryer_id,
    'title':washer_dryer_title,
    'neighborhood':washer_neighborhood,
    'footage':washer_footage,
    'bedroom':washer_bedroom,
    'price':washer_price,
    'included':washer_dryer})
Serialize(washer_dryer_data_frame,'washer_dryer')

#print(washer_dryer_id)



