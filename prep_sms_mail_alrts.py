#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import cx_Oracle
import datetime 

con = conn1.cursor()


def send_sms_mailalert(obj_name,event_date,actual_value,lowerlim_value,upperlim_value,html_file_path,lastfile_date=None,
                       html_ana_file_path=None,error_count=None,diff_hours=None,html_sc_ana_file_path=None,
                       pricing_isactive=None):
    
    act_val = f"{actual_value:,.2f}"
    low_val = f"{lowerlim_value:,.2f}"
    up_val = f"{upperlim_value:,.2f}"
    
    msg_txt = 'Abnormal Behaviour in '+obj_name+' \nDate: '+event_date+' \nReceived Count: '+act_val+'\nPredicted Range: '+low_val+' - '+up_val
    msg_date = datetime.datetime.now().date()
    
    msg_values = [('VAS SMS','123456789', msg_txt,'N',msg_date),
                 ('VAS SMS','234567891', msg_txt,'N',msg_date),
                 ('VAS SMS','345678912', msg_txt,'N',msg_date)]
    
    insert_stmt = """INSERT INTO API.KEY_SMS_MESSAGE_LIST_HP (MODULE_ID,PHONE_NO,MESSAGE,READ,ACTION_DATE) VALUES (:1, :2, :3, :4, :5)"""
    con.executemany(insert_stmt, msg_values)
    conn1.commit()
    
    ## ************* writing the alert to a html file to send in a mail *************** ##

    
    html_str = """
                    <style>
                        p.big {
                                line-height: 2.0;
                            }

                    </style>

                    <p class="big">
                       <span style="color:red">System Alert,</span><br>
                        Abnormal behaviour in: """+obj_name+""" <br> 
                        Date: """+event_date+""" <br>
                        Recieved Count: """ +act_val+""" <br>
                        Predicted Range: """+low_val+""" - """+up_val+""" <br>
                        ************ This is an auto-generated email ************
                    </p>
                    """
    html_file= open(html_file_path,"w")
        
    html_file.write(html_str)
    html_file.close()
    
    ## ************* writing first level,second level and third level analysing details to html files to send in mails *************** ##  
    
    ## **** This is for CDR Drops capturing from Node CDRs where checking for ICT Pricing, ICT Rejctions,CDR File Delay 
    ##      to ICT from Up stream **** ##
    if lastfile_date:
        if pricing_isactive == 'Yes':
            if error_count == 'None':
                diff_hours = str(diff_hours)
                html_ana_str = """
                                    <style>
                                        p.big {
                                                line-height: 2.0;
                                            }

                                    </style>

                                    <p class="big">
                                       <span style="color:red">System Alert,</span><br>
                                        CDR Analysis on """+obj_name+""" <br> 
                                        Date: """+event_date+""" <br>
                                        Rating Service is active: """+pricing_isactive+""" <br>
                                        Rating Rejections: """+error_count+""" <br>
                                        Last File Received Time: """+lastfile_date+""" <br>                                       
                                        File Delay for the Day: """+diff_hours+""" Hours <br>
                                        ************ Escalating to the Up Stream **************** <br>
                                        ************ This is an auto-generated email ************ <br>
                                    </p>
                                    """
                html_file= open(html_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()

                html_ana_str = """
                                    <style>
                                        p.big {
                                                line-height: 2.0;
                                            }

                                    </style>

                                    <p class="big">
                                       <span style="color:red">System Alert,</span><br>
                                        CDR Analysis on """+obj_name+""" <br> 
                                        Date: """+event_date+""" <br>
                                        Recieved Count: """ +act_val+""" <br>
                                        Predicted Range: """+low_val+""" - """+up_val+""" <br>
                                        Rating Service is active: """+pricing_isactive+""" <br>
                                        Rating Rejections: """+error_count+""" <br>
                                        Last File Received Time: """+lastfile_date+""" <br>                                        
                                        File Delay for the Day: """+diff_hours+""" Hours <br>
                                        ****** Please investigate the reported incident ******<br>
                                        *********** This is an auto-generated email ***********<br>
                                    </p>
                                    """
                html_file= open(html_sc_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()

            else:
                html_ana_str = """
                                    <style>
                                        p.big {
                                                line-height: 2.0;
                                            }

                                    </style>

                                    <p class="big">
                                       <span style="color:red">System Alert,</span><br>
                                        CDR Analysis on """+obj_name+""" <br> 
                                        Date: """+event_date+""" <br>
                                        Rating Service is active: """+pricing_isactive+""" <br>
                                        Rating Rejections: """+error_count+""" <br>
                                        Last File Received Time: """+lastfile_date+""" <br>
                                        Please find the attached rejections through the Node <br>
                                        ************ This is an auto-generated email ************ <br>
                                    </p>
                                    """
                html_file= open(html_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()
        else:
            if error_count == 'None':
                html_ana_str = """
                                    <style>
                                        p.big {
                                                line-height: 2.0;
                                            }

                                    </style>

                                    <p class="big">
                                       <span style="color:red">System Alert,</span><br>
                                        CDR Analysis on """+obj_name+""" <br> 
                                        Date: """+event_date+""" <br>
                                        Rating Service is active: """+pricing_isactive+""" <br>
                                        Rating Rejections: """+error_count+""" <br>
                                        Last File Received Time: """+lastfile_date+""" <br>
                                        ****** Rating Service is inactive please check  ****** <br>
                                        *********** This is an auto-generated email *********** <br>
                                    </p>
                                    """
                html_file= open(html_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()
            else :
                html_ana_str = """
                                    <style>
                                        p.big {
                                                line-height: 2.0;
                                            }

                                    </style>

                                    <p class="big">
                                        <p style="color:red"><p style="color:red"> System Alert,</p></p><br>
                                        CDR Analysis on """+obj_name+""" <br> 
                                        Date: """+event_date+""" <br>
                                        Rating Service is active: """+pricing_isactive+""" <br>
                                        Rating Rejections: """+error_count+""" <br>
                                        Last File Received Time: """+lastfile_date+""" <br>
                                        Please find the attached rejections reported through the Node <br>
                                        **** Rating Service is inactive please check **** <br>
                                        ******** This is an auto-generated email ******** <br>
                                    </p>
                                    """
                html_file= open(html_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()
            
    ## ************* This is for CDR Hikes/Drops capturing from rest catagories & Hikes of Node CDRs ************* ##
            
    else :
        if obj_name not in {'ERROR_COUNT','FILE_COUNT','EVENT_COUNT','Total CDR Count','PRICED_COUNT'}:
            ## **** This For CDR Hikes in Node CDRs and Business Streams **** ##
            if actual_value > upperlim_value :
                
                html_ana_str = """
                                        <style>
                                            p.big {
                                                    line-height: 2.0;
                                                }

                                        </style>

                                        <p class="big">
                                           <span style="color:red">System Alert,</span><br>
                                            CDR Analysis on: """+obj_name+""" <br> 
                                            Date: """+event_date+""" <br>
                                            Highest anomaly detected 10 Operator's monthly CDR report attached <br>
                                            ************** Please investigate ************** <br>
                                            ******* This is an auto-generated email ******** <br>
                                        </p>
                                        """
                html_file= open(html_ana_file_path,"w")

                html_file.write(html_ana_str)
                html_file.close()
                
            ## ************* This is for CDR Drops in Business Streams ************* ##
                
            else :
                
                if obj_name in {'Local SMS A2P-P2P','INT SMS A2P-P2P','IDD & Transit Voice','Local Voice','BULK SMS'}:
                    if pricing_isactive == 'Yes':
                        html_ana_str = """
                                            <style>
                                                p.big {
                                                        line-height: 2.0;
                                                    }

                                            </style>

                                            <p class="big">
                                               <span style="color:red">System Alert,</span><br>
                                                CDR Analysis on: """+obj_name+""" <br> 
                                                Date: """+event_date+""" <br>
                                                Rating Service is active: """+pricing_isactive+""" <br>
                                                **** Manual Intervension Required **** <br>
                                                ****** This is an auto-generated email ****** <br>
                                            </p>
                                            """
                        html_file= open(html_ana_file_path,"w")

                        html_file.write(html_ana_str)
                        html_file.close()
                        
                    else :
                        html_ana_str = """
                                            <style>
                                                p.big {
                                                        line-height: 2.0;
                                                    }

                                            </style>

                                            <p class="big">
                                               <span style="color:red">System Alert,</span><br>
                                                CDR Analysis on: """+obj_name+""" <br> 
                                                Date: """+event_date+""" <br>
                                                Rating Service is active: """+pricing_isactive+""" <br>
                                                **** Rating Service is inactive please check **** <br>
                                                ******** This is an auto-generated email ********* <br>
                                            </p>
                                            """
                        html_file= open(html_ana_file_path,"w")

                        html_file.write(html_ana_str)
                        html_file.close() 
                        
        ##  *******  This is for CDR Drops capturing from Input Files & Total CDR Statistics ******* ##
        else :
            if pricing_isactive == 'Yes':
                    if obj_name == 'ERROR_COUNT':
                        if upperlim_value < actual_value or actual_value < lowerlim_value :
                            html_ana_str = """
                                            <style>
                                                p.big {
                                                        line-height: 2.0;
                                                    }

                                            </style>

                                            <p class="big">
                                               <span style="color:red">System Alert,</span><br>
                                                CDR Analysis on: """+obj_name+""" <br> 
                                                Date: """+event_date+""" <br>
                                                Rating Service is active: """+pricing_isactive+""" <br>
                                                Please refer the attached for summary of Error Bucket <br>
                                                ********** This is an auto-generated email *********** <br>
                                            </p>
                                            """
                            html_file= open(html_ana_file_path,"w")

                            html_file.write(html_ana_str)
                            html_file.close()
                    else:
                        if actual_value < lowerlim_value :
                            html_ana_str = """
                                        <style>
                                            p.big {
                                                    line-height: 2.0;
                                                }

                                        </style>

                                        <p class="big">
                                           <span style="color:red">System Alert,</span><br>
                                            CDR Analysis on: """+obj_name+""" <br> 
                                            Date: """+event_date+""" <br>
                                            Rating Service is active: """+pricing_isactive+""" <br>
                                            **** Manual Intervension Required **** <br>
                                            **** This is an auto-generated email **** <br>
                                        </p>
                                        """
                            html_file= open(html_ana_file_path,"w")

                            html_file.write(html_ana_str)
                            html_file.close()
                        
            else:
                if obj_name == 'ERROR_COUNT':
                    if upperlim_value < actual_value or actual_value < lowerlim_value :
                        html_ana_str = """
                                        <style>
                                            p.big {
                                                    line-height: 2.0;
                                                }

                                        </style>

                                        <p class="big">
                                           <span style="color:red">System Alert,</span><br>
                                            CDR Analysis on: """+obj_name+""" <br> 
                                            Date: """+event_date+""" <br>
                                            Rating Service is active : """+pricing_isactive+""" <br>
                                            Please refer the attached for summary of Error Bucket <br>
                                            **** Rating Service is inactive please check **** <br>
                                            ********** This is an auto-generated email ************ <br>
                                        </p>
                                        """
                        html_file= open(html_ana_file_path,"w")

                        html_file.write(html_ana_str)
                        html_file.close()
                        
                else :
                    if actual_value < lowerlim_value :                    
                        html_ana_str = """
                                        <style>
                                            p.big {
                                                    line-height: 2.0;
                                                }

                                        </style>

                                        <p class="big">
                                           <span style="color:red">System Alert,</span><br>
                                            CDR Analysis on: """+obj_name+""" <br> 
                                            Date: """+event_date+""" <br>
                                            Rating Service is active: """+pricing_isactive+""" <br>
                                            **** Rating Service is inactive please check **** <br>
                                            ********** This is an auto-generated email ************ <br>
                                        </p>
                                        """
                        html_file= open(html_ana_file_path,"w")

                        html_file.write(html_ana_str)
                        html_file.close()  
                        
def file_rejmbody(orgrej_flist,duprej_flist,html_file_path):
    if orgrej_flist:
    
        orgrej_flist=str(orgrej_flist)
        html_str = """
                    <style>
                            p.big {
                                    line-height: 2.0;
                                }

                    </style>

                    <p class="big">
                       <span style="color:red">System Alert,</span><br>
                        File Processing Error<br>
                        File Names: """+orgrej_flist+"""<br>
                        **** Please investigate this file rejection at /ICTPRDAPP/bmd/rating/original_reject **** <br>
                                    ********** This is an auto-generated email ************ <br>
                    </p>
                    """
    elif duprej_flist:
    
        duprej_flist=str(duprej_flist)
        html_str = """
                    <style>
                            p.big {
                                    line-height: 2.0;
                                }

                    </style>

                    <p class="big">
                        <span style="color:red">System Alert,</span><br>
                        File Processing Error<br>
                        File Names: """+duprej_flist+"""<br>
                        **** Please investigate this file rejection at /ICTPRDAPP/bmd/rating/duplicate_reject **** <br>
                                        ********** This is an auto-generated email ************ <br>
                    </p>
                    """
    else:
        
        orgrej_flist=str(orgrej_flist)
        duprej_flist=str(duprej_flist)
        html_str = """
                    <style>
                            p.big {
                                    line-height: 2.0;
                                }

                    </style>

                    <p class="big">
                        <span style="color:red">System Alert,</span><br>
                        File Processing Error<br>
                        File Names: """+orgrej_flist + duprej_flist +"""<br>
                        **** Please investigate this file rejection at /ICTPRDAPP/bmd/rating/original_reject & /ICTPRDAPP/bmd/rating/duplicate_reject ****
                                                                ********** This is an auto-generated email ************ <br>
                    </p>
                    """
    html_file= open(html_file_path,"w")

    html_file.write(html_str)
    html_file.close()
    
def send_actiontoerr_mailalert(html_file_path):
    
    ## ************* writing the alert to a html file to send in a mail *************** ##

    
    html_str = """
                    <style>
                        p.big {
                                line-height: 2.0;
                            }

                    </style>

                    <p class="big">
                       <span style="color:red">System Alert,</span><br>
                        Please refer the attached details and add the reference data accordingly.
                        *********************** This is an auto-generated email ***********************
                    </p>
                    """
    html_file= open(html_file_path,"w")
        
    html_file.write(html_str)
    html_file.close()

#con.close()
#conn1.close()
    
    
