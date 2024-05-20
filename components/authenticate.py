import requests

def get_auth_bearer():
        
    url = 'https://easykart.net/bangkok-easykart-fastest-of-the-month/'
    response = requests.get(url)

    print(f"Status code: {response.status_code}")

    auth_bearer = ""

    if response.status_code == 200:

        lines = response.text.splitlines()
        
        for line in lines:
            if "https://modules.sms-timing.com/BestTimes/?key=" in line:

                # Result example = <div class="image-container"><iframe id="TrackRecord" src="https://modules.sms-timing.com/BestTimes/?key=ZWFzeWthcnQ6YjZlMTVhZWUtYmJkZS00NGQyLWJiNzktMGJhYTIxMmZkOTU1&amp;locale=ENG&amp;scgh=Default&amp;maxResult=100" width="882" height="320" frameborder="0" scrolling="yes" data-mce-fragment="1"></iframe></div>
                auth_bearer = line.split("key=")[1].split("&amp")[0]
    else:
        print(f"Failed to fetch the webpage: HTTP {response.status_code}")

    print(f"Authorization bearer: {auth_bearer}")
    
    if auth_bearer == "":
        print("Failed to get the authorization bearer")
        return False
    
    return f"Basic {auth_bearer}"


def get_access_token(auth_bearer):
    
    new_token_api = "https://backend.sms-timing.com/api/connectioninfo?type=modules"
    response = requests.get(new_token_api, headers={"Authorization": auth_bearer})
    kart_access_token = response.json()["AccessToken"]
        
    print(f"Kart access token: {kart_access_token}")
    
    if kart_access_token == "":
        print("Failed to get the access token")
        return False
    
    return kart_access_token