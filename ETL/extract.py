import json
import requests
import logging
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '/home/data-engineer/GAAS_Data_System/ETL')
from verify_func import cache_process

def extract(collection, greater_time, less_than_time):
    now = datetime.now()
    url = "https://as1.abiteams.com/api1/chopper/res"
    body = {
        "cmd": f"ul.lg.{collection}",
        "skip": 0,
        "secret": "shdhjKKLUA(*IJNKANXDKJASNXk",
        "limit": 2000000,
    }
    if collection == "log":
        body["greater"] = greater_time
        body["less"] = less_than_time
        col = "event"
    else:
        col = "user"
        body["con"] = {
                        "$and": 
                    [
                        { "last_online" : {"$gte": 1692266430000} }, 
                        { "last_online" : {"$lt": 1692266490000} }
                    ]
                }
        
    try:
        # Send the POST request with the specified datatrần giále
        response = requests.post(url, json = body, timeout=30)
        logging.info(f"Request time: {datetime.now() - now}")
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            now = datetime.now()
            data = json.loads(response.text)['data']['records']
            df = pd.DataFrame(data)
            logging.info(f"Create DataFrame time: {datetime.now() - now}")
            return df
        else:
            logging.error("Server GAAS error:", response.status_code)
            cache_process(greater_time, less_than_time, col)
            return -1
            
    except requests.exceptions.RequestException as e:
        logging.error("Request Exception Error :", e)
        cache_process(greater_time, less_than_time, col)
        return -1
