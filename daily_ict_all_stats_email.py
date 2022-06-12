#!/usr/bin/env python
# coding: utf-8

# In[1]:


import win32com.client
import datetime
import os
import pandas as pd
import re
import string
import random
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

    ## ******* set variables accordingly to pass in to the mailer fuction to send seperate mails ******** ##
        ## the `r` prefix means raw string
bu_msubject = 'ICT Business Stream wise Stats | '
bu_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Business_Streams_Stats\Mail_Body.html'
bu_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\Business_Streams_Stats'

nd_msubject = 'ICT Node wise Stats | '
nd_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Node_wise_Stats\Mail_Body.html'
nd_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\Node_wise_Stats'

tot_msubject = 'ICT Total CDR & Input File Stats | '
tot_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\InFile_TotCDR_Stats\Mail_Body.html'
tot_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Plot_figures\InFile_TotCDR_Stats'

    ## ************************************ For Alerts ************************************************ ##

alrt_bu_msubject = ' - ALERT : ICT Business Stream Anomly Detected | '
alrt_bu_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Business_Streams_Stats\Anomly_Mail\Anomly_Mail_Body.html'
alrt_bu_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Anomly_Plots\Business_Streams_Stats'

alrt_nd_msubject = ' - ALERT : ICT Node CDR Anomly Detected | '
alrt_nd_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Node_wise_Stats\Anomly_Mail\Anomly_Mail_Body.html'
alrt_nd_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Anomly_Plots\Node_wise_Stats'

alrt_tot_msubject = ' - ALERT : ICT Total CDR & Input File Anomly Detected | '
alrt_tot_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\InFile_TotCDR_Stats\Anomly_Mail\Anomly_Mail_Body.html'
alrt_tot_plot_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\Anomly_Plots\InFile_TotCDR_Stats'

analys_bu_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Business_Streams_Stats\Post_Analysis\Po_Ana_Mail_Body.html'
analys_nd_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Node_wise_Stats\Post_Analysis\Po_Ana_Mail_Body.html'
analys_sec_nd_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Node_wise_Stats\Sec_Post_Analysis\Po_Ana_Mail_Body.html'
analys_tot_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\InFile_TotCDR_Stats\Post_Analysis\Po_Ana_Mail_Body.html'

alrt_frej_msubject = ' - ALERT : CDR File Rejection Detected | '
alrt_frej_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\InFile_TotCDR_Stats\File_Rej_Mail\File_Rej_Mail_Body.html'

alrt_rejclr_msubject = ' - ALERT : Reference Data to be Updated in ICT | '
alrt_rejclr_mbtxt_dir = r'C:\Users\Vindhya_VIN071\Python\ICT_All_Stats\Test\To_Email\Reject_Clearence\Rej_Clr_Mail_Body.html'

ref_number = None
    ## ************************  mailer fucntion to genearte & send mails ****************************** ##

def mailer(mail_subject=None,mbody_txtf_path=None,plot_dir=None,rep_dir=None,strm_name=None):
    global ref_number
    incident_number = ''
    
        ## ********* creating the mail object ********** ##
    olMailItem = 0x0
    outlook = win32com.client.Dispatch('outlook.application')
    #mail = outlook.CreateItem(0)
    mail = outlook.CreateItem(olMailItem)
    
    today_date = datetime.date.today().strftime("%d-%b-%Y")
    
        ## ******* collecting all the objects to be attached into the mail from a given path ****** ##
    def get_filepaths(path_dir):
        #     """
        #     This function will generate the file names in a directory 
        #     tree by walking the tree either top-down or bottom-up. For each 
        #     directory in the tree rooted at directory top (including top itself), 
        #     it yields a 3-tuple (dirpath, dirnames, filenames).
        #     """
        file_names = []  # List which will store all of the filenames in the given directory.

        # Walk the tree.
        for root, directories, files in os.walk(path_dir):
            for filename in files:
                   ## Can have the full file path alone with the file name by using join (path and file name as two variables).
                filepath = os.path.join(root, filename)
                file_names.append(filepath)  # Add file names to the list.

        return file_names  

        ## Run the above function and assining the return list of file names into a list.
    if plot_dir:
        files_toAttach = get_filepaths(plot_dir)
        
    if rep_dir:
        file_toAttach = get_filepaths(rep_dir)

        ## ************************************ Email parameters ******************************************* ##
    if strm_name == 'IDD & Transit Voice':
        mail.To = 'InterconnectOperations@dialog.lk;janaka.madhawa@dialog.lk'
        
    elif strm_name == 'INT SMS A2P-P2P':
        mail.To = 'InterconnectOperations@dialog.lk;sampath.vithanage@dialog.lk'
        
    elif strm_name == 'BULK SMS':
        mail.To = 'InterconnectOperations@dialog.lk;ajith.gamage@dialog.lk;manori.desilva@dialog.lk'
        
    else:
        mail.To = 'InterconnectOperations@dialog.lk'
    
    regex=' - ALERT'
    
    if re.match(regex, mail_subject):
            ## Randomly generate the incident number ##
        def id_generator(size=6, chars=string.digits):
            in_number = ''.join(random.choice(chars) for _ in range(size))
            return 'IN'+in_number
        
        incident_number = id_generator()
        ref_number      = incident_number
        
        
    if not mail_subject :
        
        if mbody_txtf_path == analys_bu_mbtxt_dir:
            mail.Subject = ref_number + ' - First Level Analysis : ICT Business Stream Anomaly | ' + today_date
        if mbody_txtf_path == analys_nd_mbtxt_dir:
            mail.Subject = ref_number + ' - First Level Analysis : ICT Node CDR Anomaly | ' + today_date
        else:
            mail.Subject = ref_number + ' - First Level Analysis : ICT Total CDR & Input File Anomaly | ' + today_date
        
    else:
        mail.Subject = incident_number + mail_subject + today_date
        
    mail.CC = 'Vindhya.Dissanayake@dialog.lk'

    fig_ids = []
    def image_embedded():
        for x, attachment in enumerate(files_toAttach):
            fig_id = "FigID"+str(x)
                ## To be embedded the image in the mail body instead of get attach in the mail
            mail.Attachments.Add(attachment).PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", fig_id)
            fig_ids.append(fig_id)
        return fig_ids
    
    if plot_dir:
        image_embedded()
        
    if rep_dir:
        for attachment in file_toAttach:
            mail.Attachments.Add(attachment)
 
        ## Text Content to be wrote in the mail body    
    html_url= open(mbody_txtf_path,encoding='utf8')
    data=html_url.read() 

    if mail_subject == bu_msubject:
        if len(fig_ids) == 9:
            mail.HTMLBody = data+"<html><body> <img src=cid:FigID7> <img src=""cid:FigID8""> <img src=""cid:FigID3""> <img src=""cid:FigID4""> <img src=""cid:FigID5""> <img src=""cid:FigID6""> <img src=""cid:FigID1""> <img src=""cid:FigID2""> <img src=""cid:FigID0""> <br><br> ****************************************************************************************************************** </body></html>"
        else:
            mail.HTMLBody = data+"<html><body> <img src=cid:FigID8> <img src=""cid:FigID9""> <img src=""cid:FigID4""> <img src=""cid:FigID5""> <img src=""cid:FigID6""> <img src=""cid:FigID7""> <img src=""cid:FigID2""> <img src=""cid:FigID3""> <img src=""cid:FigID0""> <img src=""cid:FigID1""> <br><br> ****************************************************************************************************************** </body></html>"
                
        mail.To = 'InterconnectOperations@dialog.lk;janaka.madhawa@dialog.lk;sampath.vithanage@dialog.lk'
                
    elif mail_subject == nd_msubject:
        mail.HTMLBody = data+"<html><body> <img src=cid:FigID0> <img src=""cid:FigID1""> <br><br> ****************************************************************************************************************** </body></html>"
    elif mail_subject == tot_msubject:
        mail.HTMLBody = data+"<html><body> <img src=cid:FigID0> <img src=""cid:FigID1""> <img src=cid:FigID2> <img src=""cid:FigID3""> <br><br> ****************************************************************************************************************** </body></html>"
    elif re.match(regex, mail_subject):
        mail.HTMLBody = data+"<html><body> <img src=cid:FigID0> <br><br> ****************************************************************************************************************** </body></html>"
        mail.Categories='Red category'
        mail.Save()
    else:   
        mail.HTMLBody = data
  
    mail.Send()
    
def raise_jirareq(jira_summary,jira_desc):
    soup = BeautifulSoup(jira_desc,"html.parser")
    ## ** Removing last two lines form the converted text file ** ##
    jira_desc = (soup.get_text()).rsplit("\n",3)[0]
    jira_desc = jira_desc.replace("\n","\\n").replace("\r","\\r")

    auth_user = "Interconnect_ops"
    auth_pass = "Dialog@123"     
    url       = "https://support.dialog.lk/rest/servicedeskapi/request"

    # Set issue fields in python dictionary
    data = """
        {
        "serviceDeskId":114,
        "requestTypeId":3104,
        "requestFieldValues":{
            "summary":\""""+jira_summary+"""\",
            "description":\""""+jira_desc+"""\"
       }
    }
    """
    print(data)
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url,
            auth=(auth_user, auth_pass),
            headers=headers,
            data=data)

        print("POST {}".format(url))

    except requests.exceptions.HTTPError as error:
        print(error)

    
def med_mailer(mail_subject=None,mbody_txtf_path=None):
    
        ## ********* creating the mail object ********** ##
    #olMailItem = 0x0
    outlook = win32com.client.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    #mail = outlook.CreateItem(olMailItem)
    
    today_date = datetime.date.today().strftime("%d-%b-%Y")

        ## ************************************ Email parameters ******************************************* ##
    mail.To = 'InterconnectOperations@dialog.lk'
    #mail.To = 'asela@dialog.lk;ganganath.amarawickrama@dialog.lk;gajan.sangarappillai@dialog.lk;nuwan.ushantha@dialog.lk;vindhya.dissanayake@dialog.lk'
    
    if not mail_subject :
        mail.Subject = ref_number + ' - Second Level Analysis : ICT Node CDR Anomaly | ' + today_date
        
    else :
        ## Randomly generate the incident number ##
        def id_generator(size=6, chars=string.digits):
            in_number = ''.join(random.choice(chars) for _ in range(size))
            return 'IN'+in_number
        
        incident_number = id_generator()

        mail.Subject = incident_number + mail_subject + today_date
    jira_summary = mail.Subject
        
    mail.CC = 'Vindhya.Dissanayake@dialog.lk'
 
        ## Text Content to be wrote in the mail body    
    html_url= open(mbody_txtf_path,encoding='utf8')
    data=html_url.read() 
  
    mail.HTMLBody = data
    jira_desc = mail.HTMLBody
    mail.Categories='Red category'
    mail.Save()
  
    mail.Send()
    
    if mail_subject == alrt_frej_msubject:
        raise_jirareq(jira_summary,jira_desc)
    
# def frge_mailer(mail_subject,mbody_txtf_path):
    
#     ## ********* creating the mail object ********** ##
#     #olMailItem = 0x0
#     outlook = win32com.client.Dispatch('outlook.application')
#     mail = outlook.CreateItem(0)
#     #mail = outlook.CreateItem(olMailItem)
    
#     today_date = datetime.date.today().strftime("%d-%b-%Y")
    
#     ## Randomly generate the incident number ##
#     def id_generator(size=6, chars=string.digits):
#         in_number = ''.join(random.choice(chars) for _ in range(size))
#         return 'IN'+in_number
        
#     incident_number = id_generator()

#         ## ************************************ Email parameters ******************************************* ##
        
#     mail.To = 'InterconnectOperations@dialog.lk'
#     #mail.To = 'asela@dialog.lk;ganganath.amarawickrama@dialog.lk;gajan.sangarappillai@dialog.lk;nuwan.ushantha@dialog.lk;vindhya.dissanayake@dialog.lk'

#     mail.Subject = incident_number + mail_subject + today_date
        
#     #mail.CC = 'InterconnectOperations@dialog.lk'
    
#     ## Text Content to be wrote in the mail body    
#     html_url= open(mbody_txtf_path,encoding='utf8')
#     data=html_url.read() 
  
#     mail.HTMLBody = data
#     mail.Categories='Red category'
#     mail.Save()
  
#     mail.Send()
    

