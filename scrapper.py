from bs4 import BeautifulSoup
import json
from requests import get
import numpy as np
import pandas as pd
import csv
from fuzzywuzzy import fuzz as fw

print('hello world')
#get the initial page for the listings, to get the total count

neighborhood = []
bedroom_count =[]
sqft = []
price = []
link = []
count = 0
def Analyze(data_frame):
    neighborhood_unique_list = []
    neighborhood_max_list = []
    neighborhood_min_list = []
    neighborhood_mean_list = []
    #data = pd.read_csv(data_frame)
    #pd.set_option('display.max_rows',None)
#    count = data['neighborhood'].value_counts()
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

def Serialize(data_frame):
    data_frame['footage'] = data_frame['footage'].replace(0,np.nan)
    data_frame['bedroom'] = data_frame['bedroom'].replace(0,np.nan)
    data_frame['neighborhood'] = data_frame['neighborhood'].str.strip().str.strip('(|)')
    data_frame['neighborhood'] = data_frame['neighborhood'].str.lower()
    for i in range(len(data_frame)):
    	for j in range(i + 1, len(data_frame)):
    		ratio = fw.partial_ratio(data_frame['neighborhood'][i].lower(),data_frame['neighborhood'][j].lower())
    		if ratio>90:
    			data_frame['neighborhood'][j] = data_frame['neighborhood'][i]
    data_frame['neighborhood'].to_csv('neighborhood_clean_a.csv',index=False)
    data_frame.drop_duplicates(subset='link')
    data_frame = data_frame.dropna(subset=['footage','bedroom'],how='all')
    data_frame.to_csv("rent_clean.csv",index=False)

response = get('https://washingtondc.craigslist.org/search/apa')
html_result = BeautifulSoup(response.text, 'html.parser')
results = html_result.find('div', class_='search-legend')
total = int(results.find('span',class_='totalcount').text)
pages = np.arange(0,total+1,120)

for page in pages:
    
    response = get('https://washingtondc.craigslist.org/search/apa?s='+str(page))
    html_result = BeautifulSoup(response.text, 'html.parser')

    posts = html_result.find_all('li', class_='result-row')
    for post in posts:
        if post.find('span',class_='result-hood') is not None:
            post_url = post.find('a',class_='result-title hdrlnk')
            post_link = post_url['href']
            link.append(post_link)
            post_neighborhood = post.find('span',class_='result-hood').text
            post_price = int(post.find('span',class_='result-price').text.strip().replace('$',''))
            neighborhood.append(post_neighborhood)
            price.append(post_price)
            if post.find('span',class_='housing') is not None:
                if 'ft2' in post.find('span',class_='housing').text.split()[0]:
                    post_bedroom = np.nan
                    post_footage = post.find('span',class_='housing').text.split()[0][:-3]
                    bedroom_count.append(post_bedroom)
                    sqft.append(post_footage)
                elif len(post.find('span',class_='housing').text.split())>2:
                    post_bedroom = post.find('span',class_='housing').text.replace("br","").split()[0]
                    post_footage = post.find('span',class_='housing').text.split()[2][:-3]
                    bedroom_count.append(post_bedroom)
                    sqft.append(post_footage)
                elif len(post.find('span',class_='housing').text.split())==2:
                    post_bedroom = post.find('span',class_='housing').text.replace("br","").split()[0]
                    post_footage = np.nan
                    bedroom_count.append(post_bedroom)
                    sqft.append(post_footage)
            else:
                post_bedroom = np.nan
                post_footage = np.nan
                bedroom_count.append(post_bedroom)
                sqft.append(post_footage)
        count+=1
       
print(count)
#create results data frame
data_frame = pd.DataFrame({'neighborhood':neighborhood,'footage':sqft,'bedroom':bedroom_count,'price':price,'link':link})
# data_frame.to_csv('dirty_data.csv',index=False)
# #clean up results
Serialize(data_frame)
Analyze(data_frame)
# data_frame = data_frame.dropna(subset=['footage','bedroom'],how='all')
# data_frame.to_csv("rent_clean.csv",index=False)
# print(len(data_frame))
