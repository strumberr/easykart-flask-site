import requests 
import json
from authenticate import get_auth_bearer, get_access_token
from database import *
import time

auth_bearer = get_auth_bearer()
kart_access_token = get_access_token(auth_bearer)

kart_access_token = kart_access_token

apis = {
    "kids": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "normal": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "adults": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken={kart_access_token}"
}


while True:
    for category, api_url in apis.items():
        records = fetch_data(api_url)
        add_participants(records)
        insert_records(records, category)
        
        time.sleep(60)

# for category, api_url in apis.items():
#     records = fetch_data(api_url)
#     add_participants(records)
#     insert_records(records, category)