import http.client
import json
from urllib.parse import urlparse
import os

url = os.environ.get("GOV_WEATHER_API")
email = os.environ.get("EMAIL") #this is sent to the weather API call as well as used for the email call, see https://www.weather.gov/documentation/services-web-api
userAgent = "window-weather"

def get_weather_data(url):

    parsed_url = urlparse(url)
    
    host = parsed_url.netloc
    path = parsed_url.path

    conn = http.client.HTTPSConnection(host)

    headers = {
        "User-Agent": f"({userAgent}, {email})"
    }

    conn.request("GET", path, headers=headers)

    response = conn.getresponse()

    if response.status == 200:
        data = json.loads(response.read().decode())
        print("Request successful!")
        print(json.dumps(data, indent=2))
    else:
        print(f"Request failed with status code: {response.status}")
        print(response.read().decode())

    conn.close()

get_weather_data(url)