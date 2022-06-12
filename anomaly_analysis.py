#!/usr/bin/env python
# coding: utf-8

# In[2]:


import cx_Oracle
import datetime
import pandas as pd
import os
import datetime
import paramiko

dsn_tns = cx_Oracle.makedsn('pdcex-scan.dc.dialog.lk', '1521', service_name='ICT') 
conn2 = cx_Oracle.connect(user='ictprdi', password='ictprdi', dsn=dsn_tns) 

con2 = conn2.cursor()

def report_dumps(sql_toread,idx_col,save_to,name_as):
        ## Set the sql output to the Pands DataFrame.
    reportdata_df = pd.read_sql(sql_toread, conn2, index_col = idx_col) 
    
    reprun_date = datetime.date.today().strftime('%d-%b-%Y')

    file_name = name_as+reprun_date+'.xlsx'
    group_length = 1000000

    if not reportdata_df.empty:
        
        for i in range(0, len(reportdata_df), group_length):
            reportdata_df.iloc[i:i+group_length].to_excel(save_to+file_name, sheet_name='Row {}'.format(i))
            #reportdata_df.to_excel(save_to+file_name)


def nodedrop_file_analysing(node_name):
       
    lastfile_date = con2.callfunc('GET_LAST_FILE_DATE',datetime.datetime,[node_name])
    
    return lastfile_date

def nodedrop_error_analysing(node_name):
    
    report_dir = None
    error_count = con2.callfunc('GET_NODE_ERROR_COUNT',int,[node_name])
    
    if error_count is not None:
        con2.callproc('SP_GET_NODE_ERR_REPORT',[node_name])
        
        ds_nodeerr_repsql = """                            SELECT EVENT_START_DATE_TIME,ERROR_CODE,EVENT_DIRECTION,ANUM,BNUM,OUTGOING_PRODUCT,OUTGOING_NODE,OUTGOING_PATH,INCOMING_PRODUCT,INCOMING_NODE,INCOMING_PATH,EVE_DURATION_IN_MIN 
                            FROM TMP_ANALYSIS_NODE_ERROR
                            ORDER BY ERROR_CODE,EVENT_START_DATE_TIME
                        """
        col_name = 'EVENT_START_DATE_TIME'
        
        report_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Reports\Post_Analysis_Reports\Node_wise_Stats'
        
        ## Clear the folder if any previous dumps exist ##    
        if len(os.listdir(report_dir)) != 0:
                    for f in os.listdir(report_dir):
                        os.remove(os.path.join(report_dir, f))
        
        report_name = '\ICT_'+node_name+'_REJECTIONS_'
        
        report_dumps(ds_nodeerr_repsql,col_name,report_dir,report_name)
        
    error_count = str(error_count)
    
    return error_count,report_dir

def ict_pricing_check():
       
    try:
        host = "172.26.86.149"
        port = 22
        username = "ictprd"
        password = "M@y2022DAP"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)

        if ssh.get_transport() is not None:
            active=ssh.get_transport().is_active()

            if active:
                stdin, stdout, stderr = ssh.exec_command('./check_ict_pricing.sh')
                lines = stdout.readlines()
                
                if lines == ['Yes\n']:
                    lines = 'Yes'
                else :
                    lines = 'No'
        
    except Exception as e:
        print ("Exception throughs : %s" %e)
    lines = str(lines)
    ssh.close()
    return lines

def hike_anomly_analysing(obj_name):
    
    ds_ternop_repdf = None
    
    con2.callproc('SP_GET_TOP_NOPS',[obj_name])
    
    if obj_name != 'BULK SMS':
    
        ds_ternop_repsql = """                            SELECT * 
                            FROM TMP_ANOMLY_ANALYSIS_TNOP
                            WHERE COMPONENT_DIRECTION = 'I'
                        """

        ds_ternop_repdf = pd.read_sql(ds_ternop_repsql, conn2)

        ## **** Transpose the DataFrame **** ##
        if not ds_ternop_repdf.empty:
            ds_ternop_repdf = pd.pivot_table(ds_ternop_repdf,values=['CDR_COUNT'],index=['FRANCHISE','BILLING_OPERATOR','COMPONENT_DIRECTION'],columns=['EVENT_DATE'] )

    ds_orgnop_repsql = """                        SELECT * 
                        FROM TMP_ANOMLY_ANALYSIS_TNOP
                        WHERE COMPONENT_DIRECTION = 'O'
                    """

    ds_orgnop_repdf = pd.read_sql(ds_orgnop_repsql, conn2)
    
    if not ds_orgnop_repdf.empty:
        ds_orgnop_repdf = pd.pivot_table(ds_orgnop_repdf,values=['CDR_COUNT'],index=['FRANCHISE','BILLING_OPERATOR','COMPONENT_DIRECTION'],columns=['EVENT_DATE'] )
    
    if obj_name in {'Local SMS A2P-P2P','INT SMS A2P-P2P','Local Voice','IDD & Transit Voice','BULK SMS'}:
        report_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Reports\Post_Analysis_Reports\Business_Streams_Stats'
    else:
        report_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Reports\Post_Analysis_Reports\Node_wise_Stats'
    
    if len(os.listdir(report_dir)) != 0:
                    for f in os.listdir(report_dir):
                        os.remove(os.path.join(report_dir, f))

    reprun_date = datetime.date.today().strftime('%d-%b-%Y')

    ## Write the DF to xlsx file in the   folder
    terfile_name = '\ICT_'+obj_name+'_TERMI_TOP10_NOP_Summary_'+reprun_date+'.xlsx'
    orgfile_name = '\ICT_'+obj_name+'_ORGI_TOP10_NOP_Summary_'+reprun_date+'.xlsx'
    
    terrep_fullpath = report_dir+terfile_name
    orgrep_fullpath = report_dir+orgfile_name
    
    if not ds_ternop_repdf.empty:
        ds_ternop_repdf.to_excel(terrep_fullpath)
    
    if not ds_orgnop_repdf.empty:
        ds_orgnop_repdf.to_excel(orgrep_fullpath)
    
    return report_dir

def erroranomly_analysing():
    
    error_repsql = """                        SELECT TO_CHAR(EVENT_START_DATE_TIME,'MM/DD/YYYY') EVENT_DATE,ERROR_CODE,SUM(CALL_COUNT) ERROR_CDR_COUNT 
                        FROM ERROR_CDR
                        WHERE TRUNC(EVENT_START_DATE_TIME) = TRUNC(SYSDATE-1) 
                        GROUP BY TO_CHAR(EVENT_START_DATE_TIME,'MM/DD/YYYY'),ERROR_CODE
                        ORDER BY 1
                    """

    col_name = 'EVENT_DATE'
    
    report_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Reports\Post_Analysis_Reports\InFile_TotCDR_Stats'
    
    report_name = '\ICT_Error_Summary_'

    report_dumps(error_repsql,col_name,report_dir,report_name)
    
    return report_dir

def file_rejection_checking():
    try:
        host = "172.26.86.149"
        port = 22
        username = "ictprd"
        password = "M@y2022DAP"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        
        orgrej_files = []
        duprej_files = []

        if ssh.get_transport() is not None:
            
            active=ssh.get_transport().is_active()
            
            if active:
                stdin, stdout, stderr = ssh.exec_command('cd /ICTPRDAPP/bmd/rating/original_reject;ls -Art | tail -n 1 | find -maxdepth 1 -type f ')
                orgrej_op = stdout.readlines()
                
                if orgrej_op:
                    for i in range(len(orgrej_op)):
                        orgrej_files.append(orgrej_op[i].rstrip('\n').split(','))
                orgrej_files = ( ", ".join( str(f) for f in orgrej_files ) )
                
                stdin, stdout, stderr = ssh.exec_command('cd /ICTPRDAPP/bmd/rating/duplicate_reject;ls -Art | tail -n 1 | find -maxdepth 1 -type f ')
                duprej_op = stdout.readlines()    
                
                if duprej_op:
                    for i in range(len(duprej_op)):
                         duprej_files.append(duprej_op[i].rstrip('\n').split(','))
                duprej_files = ( ", ".join( str(f) for f in duprej_files ) )
        
    except Exception as e:
        print ("Exception throughs : %s" %e)
    ssh.close()
    
    return orgrej_files,duprej_files

def rejectb_analysing():
    
    report_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Daily_Rejection_Analysis\Reports'
    
    ## Clear the folder if any previous dumps exist ##    
    if len(os.listdir(report_dir)) != 0:
                    for f in os.listdir(report_dir):
                        os.remove(os.path.join(report_dir, f))
                    
        ## Write the DF to xlsx file and save it in to the folder ##
    
    #### ********* BSMS Web existing paths but through new web nodes at rejections to be configured ********** ####

    with open(r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Daily_Rejection_Analysis\Sql_Scripts\BSMS_SMPP_NWMASKS_REJECTIONS.sql') as file:
        err_bsmssmpp_sql = file.readline()
        
    col_name = 'ERR_MONTH'
    
    report_name = '\BSMS_SMPP_NewMasks_Report_'
    
    report_dumps(err_bsmssmpp_sql,col_name,report_dir,report_name)
    
    #### ********* BSMS SMPP new paths but through existing SMPP nodes at rejections to be configured ********** ####
    
    with open(r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Daily_Rejection_Analysis\Sql_Scripts\BSMS_WEB_NWNODES_REJECTIONS.sql') as file:
        err_bsmsweb_sql = file.readline()
    
    report_name = '\BSMS_WEB_NewNodes_Report_'
    
    report_dumps(err_bsmsweb_sql,col_name,report_dir,report_name)
    
    #### ********* BSMS billing periods to be configured ********** ####
    
    with open(r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Daily_Rejection_Analysis\Sql_Scripts\BSMS_BILLING_PERIODS_REJECTIONS.sql') as file:
        err_bsmsbillprd_sql = file.readline()
    
    report_name = '\BSMS_BILLINGPERIOD_Report_'
    
    report_dumps(err_bsmsbillprd_sql,col_name,report_dir,report_name)
    
    #### ********* Traffic from existing paths but through new nodes at rejections to be configured ********* ####
    
    with open(r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Daily_Rejection_Analysis\Sql_Scripts\IC_OG_PATHNWNODES_REJECTIONS.sql') as file:
        err_icticocpath_sql = file.readline()
    
    report_name = '\Ref_Data_Adding_for_New_Paths_Report_'
    
    report_dumps(err_icticocpath_sql,col_name,report_dir,report_name)
    
    return report_dir

#con2.close()
#conn2.close()


# In[ ]:




