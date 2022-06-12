#!/usr/bin/env python
# coding: utf-8

# In[2]:


import cx_Oracle
import datetime 
import pandas as pd
import matplotlib.dates as mdates
import numpy as np
import openpyxl
import os
import ntpath

## DB Connection
dsn_tns = cx_Oracle.makedsn('pdcex-scan.dc.dialog.lk', '1521', service_name='ICT') 
conn = cx_Oracle.connect(user='ictprdi', password='ictprdi', dsn=dsn_tns) 

c = conn.cursor()

### ************ Reading the Sql Scripts to get data ************ ###
### ************************************************************* ###

# empty list to store dataframes
plot_df = []

### Calling the proc for data collecting *****
c.callproc('SP_GET_DATA_DAILY_REPORT_TEST')

sqlscripts_dir = (r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Sql_Scripts')

def get_filepaths(path):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    f_paths_names = []  # List which will store all of the filenames in the given directory.

    # Walk the tree.
    for root, directories, files in os.walk(path):
        for file_name in files:
           # print(directories)
           # Can have the full file path alone with the file name by using join (path and file name as two variables).
            f_path_name = os.path.join(root, file_name)
            f_paths_names.append(f_path_name)  # Add file names to the list.

    return f_paths_names  

### ****************** Creating data frames ************ ###
### **************************************************** ###

def create_dataframes(f_path_name):  
    with open(f_path_name) as file_iv:
        ict_ivsql = file_iv.readline()
    
    setcdr_df = pd.read_sql(ict_ivsql, conn)
    ## Convert the column 'MESSAGE_DATE' to pands datetime data type
    setcdr_df['MESSAGE_DATE']= pd.to_datetime(setcdr_df['MESSAGE_DATE'])
    ## Set 'MESSAGE_DATE' column as 'pandas.core.indexes.datetimes.DatetimeIndex'
    setcdr_df = setcdr_df.set_index('MESSAGE_DATE')
    plot_df.append(setcdr_df)     
    
    return plot_df

#def main():
# Run 'get_filepaths' function and assing the return list of file names into a list. 
file_paths_names = get_filepaths(sqlscripts_dir)
[create_dataframes(f_path_name) for f_path_name in file_paths_names]

c.close()
conn.close()

# In[ ]:




