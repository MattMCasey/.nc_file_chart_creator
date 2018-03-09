import numpy as np
import math
from datetime import timedelta
from operator import attrgetter
from netCDF4 import Dataset
from netCDF4 import MFDataset
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import os

"""
This python file is designed to extract data from a folder of .nc files and turn
the resulting data into charts of monthly averages with standard error bars.

written in python 3.6, and should be executed with python 3.6

This section is extracting the data from the folder of .nc files. In this
deployment, we assume that the files are called 'Cyclonic' and 'Anticyclonic'.

You will have to customize the source folder, which is flagged as such.
"""

print('extracting data from nc files')



#This section builds a list of files to extract from
anticyclonic = []
cyclonic = []
for item in os.listdir('followup'): #change this to the name of the folder with your .nc files
    if 'Anticyclonic' in item:
        anticyclonic.append(item)

for item in os.listdir('followup'):
    if 'Cyclonic' in item:
        cyclonic.append(item)

anticyclonic.sort()
cyclonic.sort()


#This section extracts the data from the identified files
anti_size = []
anti_date = []

for entry in anticyclonic:
    dataset = Dataset('./followup/' + entry)
    anti_size.append(dataset.dimensions['Nobs'].size)
    anti_date.append(dataset.variables['j1'][4])

cyc_size = []
cyc_date = []

for entry in cyclonic:
    dataset = Dataset('./followup/' + entry)
    cyc_size.append(dataset.dimensions['Nobs'].size)
    cyc_date.append(dataset.variables['j1'][4])

#This section turns the extracted lists into dataframes
print('building dataframes')

anti_df = pd.DataFrame([anti_size, anti_date]).T
cyc_df = pd.DataFrame([cyc_size, cyc_date]).T

anti_df.columns = ['size', 'date']
cyc_df.columns = ['size', 'date']

anti_df['date'] = pd.to_datetime(anti_df['date'], origin='julian', unit='D')
# cyc_df['date'] = pd.to_datetime(anti_df['date'], origin='julian', unit='D')
anti_df = anti_df.set_index('date')

"""
The below section re-extracts the datafame data into lists to prepare them for
the arrays.

I've set the starting month as '5'. You shouldn't need to change this, but
can if you want to.

Note in case someone else works on this code: There is certainly a more
efficient way to do this.
"""

a_year = []
c_year = []
a_month = []
c_month = []
current_month = 5

for i in range(len(anti_df)):
    a_row = anti_df.iloc[i]
    c_row = cyc_df.iloc[i]
    month = anti_df.iloc[[i]].index.month[0]
    if month == current_month:
        a_month.append(a_row['size'])
        c_month.append(c_row['size'])
    else:
        current_month = month
        a_year.append(a_month)
        c_year.append(c_month)
        a_month = []
        c_month = []
        a_month.append(a_row['size'])
        c_month.append(c_row['size'])

"""
This section extends the month lists with the month average.
"""

print('extending months for matrix')
for i in range(len(a_year)):
    while len(a_year[i]) < 31:
        a_year[i].append(sum(a_year[i])/len(a_year[i]))
        c_year[i].append(sum(c_year[i])/len(c_year[i]))

"""
This section turns the resulting 2d lists into arrays and then charts them.
"""
lbls = []
months = [‘Jan’,
         ‘Feb’,
         ‘Mar’,
         ‘Apr’,
         ‘May’,
         ‘Jun’,
         ‘Jul’,
         ‘Aug’,
         ‘Sep’,
         ‘Oct’,
         ‘Nov’,
         ‘Dec’]

m = 4   #change this to suit your starting month
y = 2009   #change this to suit your starting year

for i in range(len(a_year)):
   month = months[m]
   year = str(y)
   lbls.append(month + ' ' + year)
   m += 1
   
   if m > 11:
       m -=12
       y += 1
       

sb.set(font_scale=2)
plt.figure(figsize=(20, 8))
sb.tsplot(np.array(c_year).T)
sb.tsplot(np.array(a_year).T, color='r')
plt.legend(['cyclonic', 'anticyclonic'])
plt.xticks(lbls)
plt.savefig('chart.png') ### you may want to change this filename
