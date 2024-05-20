import requests 
import json
from authenticate import get_auth_bearer, get_access_token
from database import *

auth_bearer = get_auth_bearer()
kart_access_token = get_access_token(auth_bearer)

kart_access_token = kart_access_token

apis = {
    "kids": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242396&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "normal": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=242392&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=1000&accessToken={kart_access_token}",
    "adults": f"https://modules-api6.sms-timing.com/api/besttimes/records/easykart?locale=ENG&rscId=242388&scgId=&startDate=1920-5-1+06%3A00%3A00&endDate=&maxResult=5000&accessToken={kart_access_token}"
}

# response format example:
# {
# "records": [
# {
# "position": 1,
# "date": "2024-05-08T17:28:48.158",
# "participant": "*Set777*",
# "score": "28.620"
# },
# {
# "position": 2,
# "date": "2024-05-05T22:35:29.068",
# "participant": "Heyday",
# "score": "28.970"
# },
# {
# "position": 3,
# "date": "2024-05-08T18:59:57.59",
# "participant": "*Ai Ai*",
# "score": "28.971"
# },
# {
# "position": 4,
# "date": "2024-05-08T20:40:42.446",
# "participant": "*Mighty*",
# "score": "29.032"
# },


for category, api_url in apis.items():
    records = fetch_data(api_url)
    add_participants(records)
    insert_records(records, category)
