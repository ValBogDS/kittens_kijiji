# -*- coding: utf-8 -*-
# This part of the code to clean the data

import pandas as pd
import numpy as np

#the sets of keywords to extract breeds, type of hair, gender, color, listing type
cat_breed_set = ('maine', 'coon', 'bengal', 'persian', 'british', 'shorthair', 'scottish', 'fold', 'siamese',                    'ragdoll', 'siberian', 'russian', 'blue', 'european', 'shorthair', 'highland', 'lynx',                    'himalayan', 'chinchilla', 'sphynx', 'savannah', 'calico', 'oriental', 'mixed')

cat_hair_set = ('short', 'long', 'hairless', 'na')

cat_gender_set = ('male', 'female', 'boy', 'girl', 'na')

cat_color_set = ('white', 'black', 'orange', 'red', 'grey', 'pearl', 'cream', 'tabby', 'tortoise', 'blue', 'na')

listing_type_set = ('rehoming', 'wanted', 'looking for')

#the data from csv file is loaded as a dataframe, define column's data types
kittens = pd.read_csv('C:/Users/Principal/Desktop/WeCloudData/Week 2/kittens_for_pandas.csv',                       dtype = {'Province':'string', 'Date':'string', 'Title':'string',                               'Price':'string', 'Location':'string', 'Num_listing':np.int32,                                'Url':'string', 'Description':'string'})

#both description and title are splitted into single words to extract breed/gender/color/hair 
#information if possible
kittens['all_words'] = kittens['Title'].str.lower().replace('/', ' /').replace('(', ' ( ').                         replace(')', ' ) ').replace(':', ' : ').str.split()
kittens['all_words'] = kittens['all_words'] + kittens['Description'].str.lower().replace('/', ' / ').replace('(', ' ( ').                 replace(')', ' ) ').replace(':', ' : ').str.split()

#the function to create a new column for breed/hair/gender/color 
#function looks for keyword from key sets in the column 'all words', returns the first keyword found
#if no keywords find, returns default value (usually, 'na')
def new_column(key_set, default_value):
    new_list = [] #the list of data for new column 
    
    for index, row in kittens.iterrows(): #go row by row
        split_res = row['all_words']
        res = [x for x in split_res if (x in key_set)] #if there is a particular breed/color/gender/hair in the title/description
        if res == []:     
            new_list.append(default_value)
        else:
            new_list.append(res[0]) 
    
    return new_list

#convert current time into datetime format
kittens['Current_time'] = pd.to_datetime(kittens['Current_time'])
kittens['listing_date'] = kittens['Current_time']

#if listing date is "yesterday', convert it to the date format using current date
filter_1 = (kittens['Date']=='Yesterday')
kittens.loc[filter_1, 'listing_date'] = kittens.loc[filter_1, 'Current_time'] + pd.DateOffset(days=-1)
 
#if listing date is "x hours/minutes/seconds ago', convert it to the date format using current date    
filter_2 = kittens['Date'].str.contains('ago', na = False)
kittens.loc[filter_2, 'listing_date'] = kittens.loc[filter_2, 'Current_time'] 

#otherwise convert existing listing date into the datetime format
filter_3 = ~(filter_1 | filter_2)
kittens.loc[filter_3, 'listing_date'] = pd.to_datetime(kittens.loc[filter_3, 'Date'], format = '%d/%m/%Y')

kittens['listing_date'] = kittens['listing_date'].dt.date

#create new columns breed/color/listing type/hair/gender using function above
kittens['breed'] = new_column(cat_breed_set, 'other')
kittens['color'] = new_column(cat_color_set, 'na')
kittens['listing_type'] = new_column(listing_type_set, 'na')
kittens['hair'] = new_column(cat_hair_set, 'na')
kittens['gender'] = new_column(cat_gender_set, 'na')
kittens['gender'] = kittens['gender'].replace({'boy':'male', 'girl':'female'})

#extract the price as numeric data
kittens['Price_new'] = kittens['Price'].str.replace('$', '', regex = False).str.replace(',','', regex = False)
kittens['Price_new'] = pd.to_numeric(kittens['Price_new'], errors = 'coerce')

#create dataframe with clean data, choose the columns needed only
kittens_clean = kittens.loc[:, ['Record_id', 'Province', 'listing_date', 'Price_new', 'breed', 'color',                                 'hair', 'gender', 'Location', 'Owner_id', 'Num_listing', 'Url']]

#write dataframe with clean data in to csv file
kittens_clean.to_csv('kittens_clean.csv')

