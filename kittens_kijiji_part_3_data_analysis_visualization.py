# This part of code to analyze and visualize the data

#!pip install geopy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

import seaborn as sns
sns.set(style="ticks", color_codes=True) 

import plotly.offline as py
import plotly.graph_objs as go 
import plotly.express as px

py.init_notebook_mode(connected=True) #to display the plot inside the notebook

import folium

from geopy.geocoders import Nominatim #the geocoder used to get latitude and longitude for location

#read the data from csv file to the dataframe with particular types of the columns set
data_file = os.path.dirname(sys.argv[0]) + '/data/kittens_clean.csv' 
kittens = pd.read_csv(data_file, dtype = {'Province':'string', 'listing_date':'string', 'breed':'string',                                'color':'string', 'hair':'string', 'gender':'string',                               'Location': 'string', 'Url':'string'})

#change the breed names into correct one (e.g. both 'maine and 'coon' should be changed to 'maine coon')
def replace_breed(part_1, part_2, full_name):
    kittens['breed'].replace(
    to_replace=[part_1, part_2],
    value=full_name,
    inplace=True)

replace_breed('maine', 'coon', 'maine coon')    
replace_breed('british', 'shorthair', 'british shorthair')
replace_breed('russian', 'blue', 'russian blue')  
replace_breed('scottish', 'fold', 'scottish fold')  
replace_breed('highland', 'lynx', 'highland lynx')  

#increase the default timeout setting from 1s to 10s to not get a TimedOut exception 
#enter a name (any name) for the ‘user_agent’ attribute
geolocator = Nominatim(timeout=10, user_agent = "myGeolocator")

#create an address line to pass to the geocoder
kittens['address_line'] = kittens['Location'] +', ' + kittens['Province'] +', ' + 'Canada'
#get gecode for each listing location
kittens['gcode'] = kittens['address_line'].apply(geolocator.geocode, exactly_one = True)
#create longitude, laatitude and altitude from location column (returns tuple)
kittens['point'] = kittens['gcode'].apply(lambda loc: tuple(loc.point) if loc else None)
#split point column into latitude, longitude and altitude columns
kittens[['latitude', 'longitude', 'altitude']] = pd.DataFrame(kittens['point'].tolist(),                                                               index = kittens.index)
#add lat, long for each location without duplicates
map_data = kittens[['Location', 'latitude', 'longitude']] .drop_duplicates('Location').set_index('Location') .join(kittens.groupby('Location')[['Record_id']].count(), how = 'inner')

#dropping nan in dataframe, only long and lat columns
map_data=map_data.dropna(subset=['longitude'])
map_data=map_data.dropna(subset=['latitude'])

#Create an empty map. Center it on Toronto downtown centre.
m = folium.Map(
    location=[43.642567, -79.387054],
    zoom_start=11
)

for x in map_data.iterrows(): #iterrows row by row (index, [values])
    folium.Marker([x[1].latitude, x[1].longitude], #add marker for each listing to the map
                 popup = x[0]).add_to(m) # display popup as index, neirbourhood name; # add_to - add to map
m


#a bar diagram with number of listings by province
kittens['Province'].value_counts().plot(kind = 'bar', title = 'Listing by province')
plt.xlabel('Province')
plt.ylabel('Listings')

#a bar diagram with number of listings by gender
kittens['gender'].value_counts().plot(kind = 'bar', title = 'Listing by gender')
plt.xlabel('Gender', fontsize = 16)
plt.ylabel('Listings', fontsize = 16)
plt.title(label = 'Listing by gender', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

#a bar diagram with number of listings by hair
kittens['hair'].value_counts().plot(kind = 'bar', title = 'Listing by hair')
plt.xlabel('Hair', fontsize = 16)
plt.ylabel('Listings', fontsize = 16)
plt.title(label = 'Listing by hair', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

#a pie cahrt with split of listing with price given, and without price provided
kittens_price = kittens['Price_new']
no_price = np.sum(kittens['Price_new'].isna()) #number of listings without price given
with_price = len(kittens_price) - np.sum(kittens['Price_new'].isna()) #the rest are listings with price given
fig1, ax1 = plt.subplots(figsize=(6, 5))

#the function calculates shares of pie slices and return back label values as % and absolute value
def func(pct, allvalues): 
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d} )".format(pct, absolute)
colors = ( 'cornflowerblue', 'lightcoral') #color for slices
l = ['no_price', 'with_price'] #names for labels
textprops = {"fontsize":15} #fontsize for labels
plt.pie([no_price/len(kittens_price), with_price/len(kittens_price)], labels=l, textprops =textprops,        autopct = lambda pct: func(pct, len(kittens_price)), colors = colors,         shadow = True, startangle = 90, radius=1)  #pie chart is drawn
plt.title('Listing with and without price split', fontsize = 16) #title and font size set


#the pie chart with listing by province split 
listing_by_province = kittens['Province'].value_counts()
fig1, ax1 = plt.subplots(figsize=(6, 5))
colors = ( 'cornflowerblue', 'burlywood', 'lightsteelblue',
          'khaki', 'cadetblue', 'sandybrown', 'lightcoral', 'mediumseagreen', 'grey') #colors for slices are set
explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1) #offsetting a slice
plt.pie(listing_by_province/len(kittens.index), explode = explode, colors = colors, shadow = True, startangle = 90,        radius=1) #pie chart is drawn

#a legend for pie chart 
plt.legend(
    loc='upper left',
    labels=['%s, %1.1f%%' % (
        l, (float(s) / len(kittens.index) * 100)) for l, s in zip(listing_by_province.index, listing_by_province)],
    prop={'size': 12},
    bbox_to_anchor=(0, 0.3), #bbox_to_anchor for manual legend placement in axes coordinates
    bbox_transform=fig1.transFigure #the transFigure do the transformation. The coordinate system:(0, 0) is bottom left of the figure
)


#a bar-line chart with primary and secondary Y-axis to show number of listings and price by breed
kittens_breed_count = kittens['breed'].value_counts().reset_index()
kittens_breed_count.columns=['breed', 'count']
kittens_breed_mean = kittens.groupby('breed', as_index = False).mean()
kittens_breed_mean = kittens_breed_mean[['breed', 'Price_new']]

#new dataframe is created with breed/mean for each breed
kittens_plt = pd.merge(kittens_breed_count, kittens_breed_mean, on = 'breed', how = 'inner')
x1 = kittens_plt['breed'] #data for x and both y coordinates are chosen
y1 = kittens_plt['count']
y2 = kittens_plt['Price_new']

fig, ax1 = plt.subplots(figsize=(20, 10))
color = 'cadetblue'
ax1.set_title('Listing and Price by Breed', fontsize=18)
ax1.set_xlabel('breed', fontsize=16)
ax1.set_ylabel('number_of_listings', fontsize=16, color=color)
ax1.bar(x1, height=y1, color=color) #the bar chart for primary y-axis
ax1.tick_params(axis='y', colors=color)

ax2 = ax1.twinx()  # share the x-axis, new y-axis
color = 'maroon'
ax2.set_ylabel('average_price', fontsize=16, color=color)
ax2.plot(x1, y2, marker='d', color=color) #the line plot for secondary y-axis
ax2.tick_params(axis='y', colors=color)

plt.show()

#a marker chart with the most popular breed by province 
kittens_breed = kittens.where(kittens['breed'] != 'other')
kittens_temp = kittens_breed.groupby('Province', as_index = False).agg('breed').value_counts()
kittens_temp.columns = ['Province', 'Breed', 'Listing_num']
kittens_top_breeds = kittens_temp.groupby(['Province'])['Listing_num'].transform(max) == kittens_temp['Listing_num']
breed_top_province = kittens_temp[kittens_top_breeds]
ax = plt.figure(figsize=(20,10))
x = breed_top_province['Province']
y = breed_top_province['Breed']
plt.scatter(x, y, s=800, c='maroon', marker=(5, 1))
plt.xticks(fontsize=16)
plt.yticks(fontsize=20)
plt.title('The most popular breed by province', fontsize = 18)
plt.grid()

#a bar-line chart with primary and secondary Y-axis to show number of listings and price by color
kittens_color_count = kittens['color'].value_counts().reset_index()
kittens_color_count.columns=['color', 'count']
kittens_color_mean = kittens.groupby('color', as_index = False).mean()
kittens_color_mean = kittens_color_mean[['color', 'Price_new']]

#new dataframe with color/mean for each color
kittens_plt_2 = pd.merge(kittens_color_count, kittens_color_mean, on = 'color', how = 'inner')
x1 = kittens_plt_2['color']
y1 = kittens_plt_2['count']
y2 = kittens_plt_2['Price_new']

fig, ax1 = plt.subplots(figsize=(20, 10))
color = 'sienna'
plt.rcParams['font.size'] = '16'

for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
    label.set_fontsize(16) #the fontsize for labels is set
    
ax1.set_title('Listing and Price by Color', fontsize=18)
ax1.set_xlabel('color', fontsize=20)
ax1.set_ylabel('number_of_listings', fontsize=16, color=color)
ax1.bar(x1, height=y1, color=color)
ax1.tick_params(axis='y', colors=color)#the bar chart for primary y-axis

for label in (ax2.get_xticklabels() + ax2.get_yticklabels()):
    label.set_fontsize(16) #the fontsize for labels is set
    
ax2 = ax1.twinx()  # share the x-axis, new y-axis
color = 'darkslategray'
ax2.set_ylabel('average_price', fontsize=16, color=color)
ax2.plot(x1, y2, marker='d', color=color) #the line plot for secondary y-axis
ax2.tick_params(axis='y', colors=color)

plt.show()

#a marker chart with the most popular color by province 
kittens_color = kittens.where(kittens['color'] != 'na')
kittens_temp_2 = kittens_color.groupby('Province', as_index = False).agg('color').value_counts()
kittens_temp_2.columns = ['Province', 'Color', 'Listing_num']
kittens_top_colors = kittens_temp_2.groupby(['Province'])['Listing_num'].transform(max) == kittens_temp_2['Listing_num']
color_top_province = kittens_temp_2[kittens_top_colors]
plt.figure(figsize=(20,5))
x = color_top_province['Province']
y = color_top_province['Color']
plt.scatter(x, y, s=800, c='olive', marker=(5, 2))
plt.xticks(fontsize=16)
plt.yticks(fontsize=20)
plt.title('The most popular color by province', fontsize = 18)
plt.grid()

#a pivot table with average price per breed and province 
province_breed_price = kittens.pivot_table('Price_new', index='breed', columns='Province', aggfunc='mean')
province_breed_price.round()