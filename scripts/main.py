#!/usr/bin/env python
# coding: utf-8

# In[1]:


from data_collecting import plot_df
import datetime 
import pandas as pd
import matplotlib as mlpt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import openpyxl
import os
import warnings
import itertools
import statsmodels.api as sm
import cx_Oracle
from statsmodels.tsa.arima_model import ARIMA
import pmdarima as pm
from statsmodels.tsa.stattools import acf
from scipy.stats import linregress
import math
import daily_ict_all_stats_email as ise
import anomaly_analysis as ana
import prep_sms_mail_alrts as sma
import shutil
import stat

for setcdr_df in plot_df:
    if setcdr_df.columns[0] == 'ICT_CDR_COUNT' :
        totcdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'LSMS_COUNT' :
        lscdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'ISMS_COUNT' :
        iscdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'LVOICE_COUNT' :
        lvcdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'IVOICE_COUNT' :
        ivcdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'BSMS_COUNT' :
        bscdr_df= setcdr_df
    elif setcdr_df.columns[0] == 'FILE_COUNT' :
        filestats_df= setcdr_df
    else :
        ndcdr_df= setcdr_df
        
mf_date = ((datetime.date.today()).replace(day=1)).strftime('%m/%d/%Y')
month_name = (totcdr_df.index[-1]).strftime('%b')
start_year = (totcdr_df.index[0]).strftime('%Y')
end_year = (totcdr_df.index[-1]).strftime('%Y')
              
def modelbuild_tobuplots(onplot_df):
    global mf_date
    
    savebufig_path = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\Business_Streams_Stats'
    savetotcdrfig_path = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\InFile_TotCDR_Stats'
    
    model = pm.auto_arima(onplot_df, start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=5, max_q=5, # maximum p and q
                      m=7,             # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=True,    #  Seasonality
                      start_P=0,
                      D=1, 
                      trace=False,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
        
    train = onplot_df.head(int(len(onplot_df)*(80/100)))
    test = onplot_df.tail(int(len(onplot_df)*(20/100)))
        
    model = model.fit(train)
        
        ## *********************************  Forecast  *********************************** ##
    future_forecast, confit = model.predict(n_periods=len(test.index) ,return_conf_int=True,alpha=0.05)
        
    future_forecast = pd.DataFrame(future_forecast,index=test.index,columns=['Test'])       
    f_lower_series = pd.Series(confit[:, 0], index=test.index)
    f_upper_series = pd.Series(confit[:, 1], index=test.index)
        
        ## *****************************  Future Predict  ********************************* ##
    n_periods = 21
    
    n_last_date = pd.to_datetime(onplot_df.index[-1])
    
    n_new_date = n_last_date + pd.to_timedelta(n_periods, unit='D')
        
    fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

    index_of_fc = pd.to_datetime(np.arange(n_last_date, n_new_date,datetime.timedelta(1)))
        
    fc_series = pd.DataFrame(fc,index=index_of_fc,columns=['Prediction'] )
        
    lower_series = pd.Series(confint[:, 0], index=index_of_fc)
    upper_series = pd.Series(confint[:, 1], index=index_of_fc)
    
        ## ****************************** Plotting ***************************************** ##
        
    fig = plt.figure(figsize=(50,12))
    ax = plt.axes()
    
       ## ******* Actual ******* ## 
               
    ax.plot(onplot_df,color='g',label='Actual')
    
       ## ***** Forecaste ***** ##

    ax.plot(future_forecast,label='Test')
    ax.fill_between(f_lower_series.index, 
                         f_lower_series,
                         f_upper_series, 
                         color='k', alpha=.1)
    
        ## ***** Prediction ***** ##
                     
    ax.plot(fc_series,label='Prediction')             
    ax.fill_between(lower_series.index, 
                         lower_series, 
                         upper_series, 
                         color='k', alpha=.1) 
    
        ## ***** Trend Line ***** ##
    onplot_df_trline = onplot_df
        
    z = np.polyfit(mdates.date2num(onplot_df_trline.index), onplot_df_trline.iloc[:,0], 1)
    p = np.poly1d(z)

    ax.plot(mdates.date2num(onplot_df_trline.index), p(mdates.date2num(onplot_df_trline.index)), "r--",label='Trend Line',alpha=1)
            
    ax.margins(x=0)
    ax.legend(fontsize=21)
            
        ## ********************************************************************************* ##        
          
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('\n%b\n%Y'))
    plt.gca().xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=(0),interval=1))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    
        ## Highlight weekends based on the x-axis units
    xmin, xmax = plt.gca().get_xlim() 
    days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
    weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
        ## Colour the weekends in plot
    plt.fill_between(days, *plt.gca().get_ylim(), where=weekends, facecolor='r', alpha=.06)
        ## set limits back to default values
    ax.set_xlim(xmin, xmax)


    if (onplot_df.columns[0] == 'ICT_CDR_COUNT'):
        suptitle_head = 'Total'
        savefig_name = '\ICT_TotVol_MOM_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'LSMS_COUNT'):
        suptitle_head = 'Local SMS A2P-P2P'
        savefig_name = '\ICT_LSVol_MOM_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'ISMS_COUNT'):
        suptitle_head = 'INT SMS A2P-P2P'
        savefig_name = '\ICT_ISVol_MOM_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'IVOICE_COUNT'):
        suptitle_head = 'IDD & Transit Voice'
        savefig_name = '\ICT_IVVol_MOM_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'LVOICE_COUNT'):
        suptitle_head = 'Local Voice'
        savefig_name = '\ICT_LVVol_MOM_Trend_fig.jpg'
    else:
        suptitle_head = 'BULK SMS'
        savefig_name = '\ICT_BSVol_MOM_Trend_fig.jpg'
        
    plt.gcf().suptitle(suptitle_head+' CDR Monthly - ' + start_year + '/' + end_year + '\n(Weekends are Highlighted)' ,fontsize=40)
    plt.grid() 
    plt.gca().tick_params(axis='both', which='both', labelsize=22, pad=20)
    plt.gca().set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
    plt.gca().set_ylabel('CDR_Count',fontsize=21, color="Black",labelpad=15)         
    plt.gca().yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.legend(fontsize=21)

    if suptitle_head == 'Total':
        plt.savefig(savetotcdrfig_path+savefig_name, bbox_inches='tight')
    else:
        plt.savefig(savebufig_path+savefig_name, bbox_inches='tight')       
    
      ## ********************************************************************************* ##
    if (datetime.date.today()).strftime('%d') == '02':
        yd_date = (datetime.date.today()- datetime.timedelta(2)).strftime('%m/%d/%Y')
        curmonplot_df = onplot_df.loc[yd_date:mf_date]
        curmonff_df = future_forecast.loc[yd_date:mf_date]
        
        if len(curmonplot_df) != 0 :
            curmonplot_df.plot(figsize=(50,13))
            plt.plot(curmonff_df)
        
        plt.fill_between(f_lower_series.loc[yd_date:mf_date].index, 
                         f_lower_series.loc[yd_date:mf_date], 
                         f_upper_series.loc[yd_date:mf_date], 
                         color='k', alpha=.1)
            

    else:
        yd_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%m/%d/%Y')
        
        if (datetime.date.today()).strftime('%d') == '01':
            mf_date = ((datetime.date.today() - datetime.timedelta(1)).replace(day=1)).strftime('%m/%d/%Y')
        
        curmonplot_df = onplot_df.loc[mf_date:yd_date]
        curmonff_df = future_forecast.loc[mf_date:yd_date]
        
        if len(curmonplot_df) != 0 :
            curmonplot_df.plot(figsize=(50,13))
            plt.plot(curmonff_df)

        plt.fill_between(f_lower_series.loc[mf_date:yd_date].index, 
                         f_lower_series.loc[mf_date:yd_date], 
                         f_upper_series.loc[mf_date:yd_date], 
                         color='k', alpha=.1)
                                    
    
    if (onplot_df.columns[0] == 'ICT_CDR_COUNT'):
        savefig_name_a = '\ICT_TotVol_DL_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'LSMS_COUNT'):
        savefig_name_a = '\ICT_LSVol_DL_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'ISMS_COUNT'):
        savefig_name_a = '\ICT_ISVol_DL_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'IVOICE_COUNT'):
        savefig_name_a = '\ICT_IVVol_DL_Trend_fig.jpg'
    elif (onplot_df.columns[0] == 'LVOICE_COUNT'):
        savefig_name_a = '\ICT_LVVol_DL_Trend_fig.jpg'
    else:
        savefig_name_a = '\ICT_BSVol_DL_Trend_fig.jpg'
    
    if (len(curmonplot_df) != 0) :
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            
        xmin, xmax = plt.gca().get_xlim() 
        days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
        weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
        plt.fill_between(days, *plt.gca().get_ylim(), where=weekends, facecolor='r', alpha=.06)
        plt.gca().set_xlim(xmin, xmax)
        
        plt.margins(x=0)
        plt.gca().tick_params(axis='both', which='both', labelsize=22, pad=20)
        plt.gca().set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
        plt.gca().set_ylabel('CDR_Count',fontsize=21, color="Black",labelpad=15)         
        plt.gca().yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        plt.legend(['Actual','Test'],fontsize=21)
        #plt.gcf().autofmt_xdate()
        plt.grid()
        plt.gcf().suptitle(suptitle_head+' CDR Daily - ' + month_name+ ' ' +end_year + '\n(Weekends are Highlighted)' ,fontsize=40) 

        if suptitle_head == 'Total':
            plt.savefig(savetotcdrfig_path+savefig_name_a, bbox_inches='tight')
            
        else:
            plt.savefig(savebufig_path+savefig_name_a, bbox_inches='tight')
            
        
        ## ************************************* Anomaly Detection ************************************ ##
            
    actual_value = onplot_df.iloc[-1].squeeze()
    lowerlim_value = f_lower_series.iloc[-1]
    upperlim_value = f_upper_series.iloc[-1]
    saveanomlyfig_name = 'Anomly_Plot.jpg'

            
    if ( actual_value < lowerlim_value ) or ( upperlim_value < actual_value):
        pricing_isactive = None
        event_date = (onplot_df.index[-1]).strftime('%Y/%m/%d')
        
        if actual_value < lowerlim_value :
            pricing_isactive = ana.ict_pricing_check()
               
        if suptitle_head == 'Total':
            obj_name = suptitle_head+ ' CDR Count'
            
        else:
            obj_name = suptitle_head
            
        if suptitle_head == 'Total':
                
            sma.send_sms_mailalert(obj_name,event_date,actual_value,lowerlim_value,upperlim_value,ise.alrt_tot_mbtxt_dir,
                              '',ise.analys_tot_mbtxt_dir,'','',
                              '',pricing_isactive)

            if len(os.listdir(ise.alrt_tot_plot_dir)) != 0:
                    for f in os.listdir(ise.alrt_tot_plot_dir):
                        os.remove(os.path.join(ise.alrt_tot_plot_dir, f))

            plt.savefig(ise.alrt_tot_plot_dir+'\\'+saveanomlyfig_name, bbox_inches='tight')

            ise.mailer(ise.alrt_tot_msubject,ise.alrt_tot_mbtxt_dir,ise.alrt_tot_plot_dir)
            
            if actual_value < lowerlim_value:        
                ise.mailer('',ise.analys_tot_mbtxt_dir,'','')
            
        else :
            
            sma.send_sms_mailalert(obj_name,event_date,actual_value,lowerlim_value,upperlim_value,ise.alrt_bu_mbtxt_dir,
                              '',ise.analys_bu_mbtxt_dir,'','',
                              '',pricing_isactive)

            if len(os.listdir(ise.alrt_bu_plot_dir)) != 0:
                    for f in os.listdir(ise.alrt_bu_plot_dir):
                        os.remove(os.path.join(ise.alrt_bu_plot_dir, f))

            plt.savefig(ise.alrt_bu_plot_dir+'\\'+saveanomlyfig_name, bbox_inches='tight')

            ise.mailer(ise.alrt_bu_msubject,ise.alrt_bu_mbtxt_dir,ise.alrt_bu_plot_dir,'',suptitle_head)
            
            if upperlim_value < actual_value:
                report_dir = ana.hike_anomly_analysing(suptitle_head)
                ise.mailer('',ise.analys_bu_mbtxt_dir,'',report_dir,suptitle_head)
                
            else:
                ise.mailer('',ise.analys_bu_mbtxt_dir,'','',suptitle_head)
            
    #plt.show()
    
    
##**** Remove previously saved figures **** ##
savebufig_path = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\Business_Streams_Stats'
if len(os.listdir(savebufig_path)) != 0:
        for f in os.listdir(savebufig_path):
            os.remove(os.path.join(savebufig_path, f))
            
for onplot_df in (totcdr_df,lscdr_df,iscdr_df,lvcdr_df,ivcdr_df,bscdr_df):
        modelbuild_tobuplots(onplot_df)
ise.mailer(ise.bu_msubject,ise.bu_mbtxt_dir,ise.bu_plot_dir)
    
    
def modelbuild_tondplot(ndplotdf):
    global mf_date
    savendfig_path = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\Node_wise_Stats'
    savendfigmon_name = '\CDR_Node_Wise_MoM_Trend_Fig.jpg'
    savendfigdly_name = '\CDR_Node_Wise_DL_Trend_Fig.jpg'
    
    ## List the column names in DF
    channels=[]
    for i in ndplotdf:
        channels.append(i)

    row_count=int((len(channels)-1)/2)
    
    fig, axes = plt.subplots((row_count+1),2,sharex=False, figsize=(50,80), squeeze=False)
    fig2, axes2 = plt.subplots((row_count+1),2,sharex=False, figsize=(50,80), squeeze=False)
    
    axe=axes.ravel()
    axe2=axes2.ravel()
    axe3=np.concatenate((axe,axe2)) #that the arrays to be concatenated must be supplied as a tuples
    
    for i, c in enumerate(ndplotdf.columns):
            ndplotdf_a = ndplotdf[c].dropna()
            model = pm.auto_arima(ndplotdf_a, start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=5, max_q=5, # maximum p and q
                      m=7,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=True,    #  Seasonality
                      start_P=0, 
                      D=1, 
                      trace=False,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
        
            train = ndplotdf_a.head(int(len(ndplotdf_a)*(80/100)))
            test = ndplotdf_a.tail(int(len(ndplotdf_a)*(20/100)))
            
            model.fit(train)
        
            ###### Forecast #######
            future_forecast, confit = model.predict(n_periods=len(test.index) , return_conf_int=True)
        
            future_forecast = pd.DataFrame(future_forecast,index = test.index,columns=['Test'])       
        
            f_lower_series = pd.Series(confit[:, 0], index=test.index)
            f_upper_series = pd.Series(confit[:, 1], index=test.index)
            
            ###### Future predict #######
            n_periods = 7
            n_last_date = pd.to_datetime(ndplotdf_a.index[-1])
            n_new_date = n_last_date + pd.to_timedelta(n_periods, unit='D')
        
            fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

            index_of_fc = pd.to_datetime(np.arange(n_last_date, n_new_date,datetime.timedelta(1)))
        
            fc_series = pd.DataFrame(fc, index=index_of_fc,columns=['Prediction'] )

            lower_series = pd.Series(confint[:, 0], index=index_of_fc)
            upper_series = pd.Series(confint[:, 1], index=index_of_fc) 
            
            plotOnaxe = ndplotdf_a
            plotOnaxe.plot(ax=axe[i],label='Actual')
            future_forecast.plot(ax=axe[i])
            axe[i].fill_between(f_lower_series.index, 
                          f_lower_series, 
                          f_upper_series, 
                          color='k', alpha=.1)
            fc_series.plot(ax=axe[i], color='darkgreen')
            axe[i].fill_between(lower_series.index, 
                          lower_series, 
                          upper_series, 
                          color='k', alpha=.1)
            
            axe[i].xaxis.set_major_locator(mdates.YearLocator())
            axe[i].xaxis.set_major_formatter(mdates.DateFormatter('\n%Y'))
            axe[i].xaxis.set_minor_locator(mdates.MonthLocator())
            axe[i].xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
            axe[i].legend(['Actual','Test','Prediction'],fontsize=18)
            axe[i].set_title('%s' % c,fontsize=31, color="Black",pad=21)
            fig.suptitle('ICT Node wise CDR Monthly - ' + start_year + '/' + end_year + '\n(Weekends are Highlighted)' ,fontsize=40)
            
            if (datetime.date.today()).strftime('%d') == '02':
                yd_date = (datetime.date.today() - datetime.timedelta(2)).strftime('%m/%d/%Y')
                dftoMonSubPlots = ndplotdf_a.loc[yd_date:mf_date]
                ##### Forecast Plot
                future_Monforecast = future_forecast.loc[yd_date:mf_date]
                
                f_lower_series_index = f_lower_series.loc[yd_date:mf_date].index
                f_lower_series       = f_lower_series.loc[yd_date:mf_date]
                f_upper_series       = f_upper_series.loc[yd_date:mf_date]
                                   

            else:
                yd_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%m/%d/%Y')
                
                if (datetime.date.today()).strftime('%d') == '01':
                    mf_date = ((datetime.date.today() - datetime.timedelta(1)).replace(day=1)).strftime('%m/%d/%Y')
                    
                dftoMonSubPlots = ndplotdf_a.loc[mf_date:yd_date]
                ##### Forecast Plot
                future_Monforecast = future_forecast.loc[mf_date:yd_date]
                
                f_lower_series_index = f_lower_series.loc[mf_date:yd_date].index
                f_lower_series       = f_lower_series.loc[mf_date:yd_date]
                f_upper_series       = f_upper_series.loc[mf_date:yd_date]
                
            
            dftoMonSubPlots.plot(ax=axe2[i],label='Actual')
            future_Monforecast.plot(ax=axe2[i])
            axe2[i].fill_between(f_lower_series_index, 
                          f_lower_series, 
                          f_upper_series, 
                          color='k', alpha=.1)
                           
            axe2[i].xaxis.set_major_locator(mdates.DayLocator())
            axe2[i].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            axe2[i].set_title('%s' % c,fontsize=31, color="Black",pad=21)
            axe2[i].legend(['Actual','Test'],fontsize=18)
            
            fig2.suptitle('ICT Node wise CDR Daily - ' + month_name+ ' ' +end_year + '\n(Weekends are Highlighted)' ,fontsize=40) 
            
            ## ************************************* Anomaly Detection ************************************ ##
            
            actual_value = dftoMonSubPlots.iloc[-1]
            lowerlim_value = f_lower_series.iloc[-1]
            upperlim_value = f_upper_series.iloc[-1]

            if ( actual_value < lowerlim_value ) or ( upperlim_value < actual_value):
                
                event_date = (dftoMonSubPlots.index[-1]).strftime('%Y/%m/%d')
                obj_name = 'Node: '+c
                
                lastfile_date = None
                error_count = None
                diff_hours = None
                pricing_isactive = None
                    
                if actual_value < lowerlim_value:
                    lastfile_date = ana.nodedrop_file_analysing(c)
                    error_count,report_dir = ana.nodedrop_error_analysing(c)
                    pricing_isactive = ana.ict_pricing_check()
                
                    eod_time = datetime.datetime.now() - datetime.timedelta(1)
                    eod_time = eod_time.replace(hour=23, minute=59, second=59, microsecond=999999)
                    difference = eod_time - lastfile_date
                    diff_hours = int(difference.total_seconds()/3600)           
          
                    lastfile_date = lastfile_date.strftime("%Y/%m/%d %H:%M:%S")
                sma.send_sms_mailalert(obj_name,event_date,actual_value,lowerlim_value,upperlim_value,ise.alrt_nd_mbtxt_dir,
                                   lastfile_date,ise.analys_nd_mbtxt_dir,error_count,diff_hours,
                                   ise.analys_sec_nd_mbtxt_dir,pricing_isactive)
                
                if len(os.listdir(ise.alrt_nd_plot_dir)) != 0:
                    for f in os.listdir(ise.alrt_nd_plot_dir):
                        os.remove(os.path.join(ise.alrt_nd_plot_dir, f))
                        
                fig3 = plt.figure(figsize=(50,12))
                ax = plt.axes()
                
                dftoMonSubPlots.plot(ax=ax,label='Actual')
                future_Monforecast.plot(ax=ax)
                ax.fill_between(f_lower_series.index, 
                              f_lower_series, 
                              f_upper_series, 
                              color='k', alpha=.1)
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                ax.set_title('%s' % c,fontsize=31, color="Black",pad=21)
                ax.legend(['Actual','Test'],fontsize=18)
                
                ax.margins(x=0)
                ax.grid()
                ax.yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                ax.tick_params(axis='both', which='both', labelsize=22, pad=20)
                ax.set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
                ax.set_ylabel('CDR_Count',fontsize=21, color="Black",labelpad=15)
                    ## Highlight weekends based on the x-axis units
                    ### ** function to Return the x-axis view limits. - left, right(float, float)
                xmin, xmax = ax.get_xlim() 
                days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
                weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
                    ## Colour the weekends in plot
                ax.fill_between(days, *ax.get_ylim(), where=weekends, facecolor='r', alpha=.06)
                    ## set limits back to default values
                ax.set_xlim(xmin, xmax)
            
                
                fig3.savefig(ise.alrt_nd_plot_dir+"\\"+c+".jpg")
                    
                ise.mailer(ise.alrt_nd_msubject,ise.alrt_nd_mbtxt_dir,ise.alrt_nd_plot_dir)
                
                if upperlim_value < actual_value:
                    report_dir = ana.hike_anomly_analysing(c)
                    ise.mailer('',ise.analys_nd_mbtxt_dir,'',report_dir)
                    
                if actual_value < lowerlim_value:
                    ise.mailer('',ise.analys_nd_mbtxt_dir,'',report_dir)
                    
                    if (diff_hours >= 1) and error_count == 'None' and pricing_isactive == 'Yes':
                        ise.med_mailer('',ise.analys_sec_nd_mbtxt_dir)
                
                    if (diff_hours < 1) and error_count == 'None' and pricing_isactive == 'Yes':
                        ise.med_mailer('',ise.analys_sec_nd_mbtxt_dir)
    
            
    ## Formatting all the subplots.
    for x, c in enumerate(axe3):
        
        axe3[x].margins(x=0)
        axe3[x].grid()
        axe3[x].yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        axe3[x].tick_params(axis='both', which='both', labelsize=22, pad=20)
        axe3[x].set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
        axe3[x].set_ylabel('CDR_Count',fontsize=21, color="Black",labelpad=15)
            ## Highlight weekends based on the x-axis units
            ### ** function to Return the x-axis view limits. - left, right(float, float)
        xmin, xmax = axe3[x].get_xlim() 
        days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
        weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
            ## Colour the weekends in plot
        axe3[x].fill_between(days, *axe3[x].get_ylim(), where=weekends, facecolor='r', alpha=.06)
            ## set limits back to default values
        axe3[x].set_xlim(xmin, xmax)

    axes.flat[-1].set_visible(False)
    fig.tight_layout(pad=2.5)
    fig.subplots_adjust(top=0.95)
    fig.savefig(savendfig_path+savendfigmon_name, bbox_inches='tight')
    axes2.flat[-1].set_visible(False)
    fig2.tight_layout(pad=2.5)
    fig2.subplots_adjust(top=0.95)
    fig2.savefig(savendfig_path+savendfigdly_name, bbox_inches='tight')
    
    ise.mailer(ise.nd_msubject,ise.nd_mbtxt_dir,ise.nd_plot_dir)

    
modelbuild_tondplot(ndcdr_df)

def modelbuild_tofsplot(fsplot_mdf):
    global mf_date
    savefsfig_path = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\InFile_TotCDR_Stats'
    savefsfigmon_name = '\Inputfile_MoM_Trend_Fig.jpg'
    savefsfigdly_name = '\Inputfile_DL_Trend_Fig.jpg'
    
    channels=[]
    for i in fsplot_mdf:
        channels.append(i)

    row_count=int(len(channels)/2)
    
    fig, axes = plt.subplots((row_count),2,sharex=False, figsize=(50,26), squeeze=False)
    fig2, axes2 = plt.subplots((row_count),2,sharex=False, figsize=(50,26), squeeze=False)
    axe=axes.ravel()
    axe2=axes2.ravel()
    axe3=np.concatenate((axe,axe2)) #that the arrays to be concatenated must be supplied as a tuples
    
    for i, c in enumerate(fsplot_mdf.columns):
            fsplotdf = pd.DataFrame(fsplot_mdf[c])
            model = pm.auto_arima(fsplotdf, start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=5, max_q=5, # maximum p and q
                      m=7,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=True,    #  Seasonality
                      start_P=0, 
                      D=1, 
                      trace=False,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
        
            train = fsplotdf.head(int(len(fsplotdf)*(80/100)))
            test = fsplotdf.tail(int(len(fsplotdf)*(20/100)))
            
            model.fit(train)
        
            ###### Forecast #######
            future_forecast, confit = model.predict(n_periods=len(test.index) , return_conf_int=True)
        
            future_forecast = pd.DataFrame(future_forecast,index = test.index,columns=['Test'])       
        
            f_lower_series = pd.Series(confit[:, 0], index=test.index)
            f_upper_series = pd.Series(confit[:, 1], index=test.index)
            
            ###### Future predict #######
            n_periods = 7
            n_last_date = pd.to_datetime(fsplotdf.index[-1])
            n_new_date = n_last_date + pd.to_timedelta(n_periods, unit='D')
        
            fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

            index_of_fc = pd.to_datetime(np.arange(n_last_date, n_new_date,datetime.timedelta(1)))
        
            fc_series = pd.DataFrame(fc, index=index_of_fc,columns=['Prediction'] )

            lower_series = pd.Series(confint[:, 0], index=index_of_fc)
            upper_series = pd.Series(confint[:, 1], index=index_of_fc) 
            
            fsplotdf.plot(ax=axe[i],label='Actual')
            future_forecast.plot(ax=axe[i])
            axe[i].fill_between(f_lower_series.index, 
                          f_lower_series, 
                          f_upper_series, 
                          color='k', alpha=.1)
            fc_series.plot(ax=axe[i], color='darkgreen')
            axe[i].fill_between(lower_series.index, 
                          lower_series, 
                          upper_series, 
                          color='k', alpha=.1)
            
            axe[i].xaxis.set_major_locator(mdates.YearLocator())
            axe[i].xaxis.set_major_formatter(mdates.DateFormatter('\n%Y'))
            axe[i].xaxis.set_minor_locator(mdates.MonthLocator())
            axe[i].xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
            axe[i].set_title('%s' % c,fontsize=31, color="Black",pad=21)
                
            if (fsplotdf.columns[0] == 'FILE_COUNT'):
                yax_label = 'File_Count'
            elif (fsplotdf.columns[0] == 'EVENT_COUNT'):
                yax_label = 'Event_Count'
            elif (fsplotdf.columns[0] == 'PRICED_COUNT'):
                yax_label = 'Priced_Count'
            else:
                yax_label = 'Error_Count'
            
            axe[i].set_ylabel(yax_label,fontsize=21, color="Black",labelpad=15)            
            axe[i].legend(['Actual','Test','Prediction'],fontsize=18)
            fig.suptitle('Processed File Stats Monthly - ' + start_year + '/' + end_year + '\n(Weekends are Highlighted)' ,fontsize=40)
            
            if (datetime.date.today()).strftime('%d') == '02':
                yd_date = (datetime.date.today()-datetime.timedelta(2)).strftime('%m/%d/%Y')
                dftoMonSubPlots = fsplotdf.loc[yd_date:mf_date]
                ##### Forecast Plot
                future_Monforecast = future_forecast.loc[yd_date:mf_date]
                
                f_lower_series_index = f_lower_series.loc[yd_date:mf_date].index
                f_lower_series       = f_lower_series.loc[yd_date:mf_date]
                f_upper_series       = f_upper_series.loc[yd_date:mf_date]

            else:
                yd_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%m/%d/%Y')
                
                if (datetime.date.today()).strftime('%d') == '01':
                    mf_date = ((datetime.date.today() - datetime.timedelta(1)).replace(day=1)).strftime('%m/%d/%Y')
                
                dftoMonSubPlots = fsplotdf.loc[mf_date:yd_date]
                ##### Forecast Plot
                future_Monforecast = future_forecast.loc[mf_date:yd_date]
                
                f_lower_series_index = f_lower_series.loc[mf_date:yd_date].index
                f_lower_series       = f_lower_series.loc[mf_date:yd_date]
                f_upper_series       = f_upper_series.loc[mf_date:yd_date]
            
            dftoMonSubPlots.plot(ax=axe2[i],label='Actual')
            future_Monforecast.plot(ax=axe2[i])
            axe2[i].fill_between(f_lower_series_index, 
                          f_lower_series, 
                          f_upper_series, 
                          color='k', alpha=.1)
                           
            axe2[i].xaxis.set_major_locator(mdates.DayLocator())
            axe2[i].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            axe2[i].set_title('%s' % c,fontsize=31, color="Black",pad=21)
            
            axe2[i].set_ylabel(yax_label,fontsize=21, color="Black",labelpad=15)
            axe2[i].legend(['Actual','Test'],fontsize=18)
            fig2.suptitle('Processed File Stats Daily - ' + month_name+ ' ' +end_year + '\n(Weekends are Highlighted)' ,fontsize=40) 
            
           ## ************************************* Anomaly Detection ************************************ ##
            actual_value = dftoMonSubPlots.iloc[-1].squeeze()
            lowerlim_value = f_lower_series.iloc[-1]
            upperlim_value = f_upper_series.iloc[-1]          
            
            if ( actual_value < lowerlim_value ) or ( upperlim_value < actual_value):
                pricing_isactive = None
                event_date = (dftoMonSubPlots.index[-1]).strftime('%Y/%m/%d')
                #if actual_value < lowerlim_value :
                pricing_isactive = ana.ict_pricing_check()
                obj_name = c
                
                sma.send_sms_mailalert(obj_name,event_date,actual_value,lowerlim_value,upperlim_value,ise.alrt_tot_mbtxt_dir,
                                   '',ise.analys_tot_mbtxt_dir,'','',
                                   '',pricing_isactive)
                
                if len(os.listdir(ise.alrt_tot_plot_dir)) != 0:
                    for f in os.listdir(ise.alrt_tot_plot_dir):
                        os.remove(os.path.join(ise.alrt_tot_plot_dir, f))
                        
                fig3 = plt.figure(figsize=(50,12))
                ax = plt.axes()
                        
                dftoMonSubPlots.plot(ax=ax,label='Actual')
                future_Monforecast.plot(ax=ax)
                ax.fill_between(f_lower_series.index, 
                              f_lower_series, 
                              f_upper_series, 
                              color='k', alpha=.1)
                           
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                ax.set_title('%s' % c,fontsize=31, color="Black",pad=21)
            
                ax.set_ylabel(yax_label,fontsize=21, color="Black",labelpad=15)
                ax.legend(['Actual','Test'],fontsize=18)
                ax.margins(x=0)
                ax.grid()
                ax.yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
                ax.tick_params(axis='both', which='both', labelsize=22, pad=20)
                ax.set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
                xmin, xmax = ax.get_xlim() 
                days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
                weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
                ax.fill_between(days, *ax.get_ylim(), where=weekends, facecolor='r', alpha=.06)
                ## set limits back to default values
                ax.set_xlim(xmin, xmax)
                        
                fig3.savefig(ise.alrt_tot_plot_dir+"\\"+c+".jpg")
                
                ise.mailer(ise.alrt_tot_msubject,ise.alrt_tot_mbtxt_dir,ise.alrt_tot_plot_dir)
                
                if c == 'ERROR_COUNT':
                    report_dir = ana.erroranomly_analysing()
                    ise.mailer('',ise.analys_tot_mbtxt_dir,'',report_dir)
                    
                else :
                    if actual_value < lowerlim_value:
                        ise.mailer('',ise.analys_tot_mbtxt_dir,'','')                    
                        
    ## Formatting all the subplots.
    for x, c in enumerate(axe3):
        
        axe3[x].margins(x=0)
        axe3[x].grid()
        axe3[x].yaxis.set_major_formatter(mlpt.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        axe3[x].tick_params(axis='both', which='both', labelsize=22, pad=20)
        axe3[x].set_xlabel('Event_Date',fontsize=21, color="Black",labelpad=15)
        xmin, xmax = axe3[x].get_xlim() 
        days = np.arange(np.floor(xmin), np.ceil(xmax)+2)
        weekends = [(dt.weekday()>=5)|(dt.weekday()==0) for dt in mdates.num2date(days)]
        axe3[x].fill_between(days, *axe3[x].get_ylim(), where=weekends, facecolor='r', alpha=.06)
        # set limits back to default values
        axe3[x].set_xlim(xmin, xmax)

    fig.tight_layout(pad=3.5)
    fig.subplots_adjust(top=0.90)
    fig.savefig(savefsfig_path+savefsfigmon_name, bbox_inches='tight')
    fig2.tight_layout(pad=3.5)
    fig2.subplots_adjust(top=0.90)
    fig2.savefig(savefsfig_path+savefsfigdly_name, bbox_inches='tight')
    
    ise.mailer(ise.tot_msubject,ise.tot_mbtxt_dir,ise.tot_plot_dir)
    
    orgrej_files,duprej_files = ana.file_rejection_checking()
    
    if orgrej_files or duprej_files:
        sma.file_rejmbody(orgrej_files,duprej_files,ise.alrt_frej_mbtxt_dir)
        ise.med_mailer(ise.alrt_frej_msubject,ise.alrt_frej_mbtxt_dir)

modelbuild_tofsplot(filestats_df)

def ictrejctions_analysis():
    
    report_dir = ana.rejectb_analysing()
    
    if len(os.listdir(report_dir)) != 0:
        sma.send_actiontoerr_mailalert(ise.alrt_rejclr_mbtxt_dir)
        ise.mailer(ise.alrt_rejclr_msubject,ise.alrt_rejclr_mbtxt_dir,'',report_dir)
        
ictrejctions_analysis()

