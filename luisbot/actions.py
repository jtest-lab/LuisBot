# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 11:16:45 2020

@author: T_jubin.ben
"""
from botbuilder.core import TurnContext, ActivityHandler
import requests

def get_buhr(turn_context):
    API_username = "A0000262@C0016585093P"
    API_password = "Nec@0987"
    base_url = "https://api10.successfactors.com/odata/v2/"
    api_type = "User"
    emp_id = 51454975
    api_filter = "({empId})/hr?$format=json".format(empId = emp_id)
    api_response = requests.get(base_url + api_type + api_filter,
                            auth=(API_username, API_password))
    if api_response.status_code == 200 and len(api_response.json()["d"]) != 0:
        buhr_name = api_response.json()["d"]["defaultFullName"]
        buhr_email = api_response.json()["d"]["email"]
        print(buhr_name)
        turn_context.send_activity(f"Name: {buhr_name}, Email: {buhr_email}")
            
        return ""