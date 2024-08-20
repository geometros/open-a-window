import http.client
import json
from urllib.parse import urlparse, urlencode
import os
import base64

url = os.environ.get("GOV_WEATHER_API")
email = os.environ.get("EMAIL") #this is sent to the weather API call as well as used for the email call, see https://www.weather.gov/documentation/services-web-api
userAgent = "window-weather"

def extractData(data): 
    dataList = data["properties"]["periods"]
    return "the current temperature in your area is: " + str(dataList[0]["temperature"])
    
def getWeatherData(url):

    parsedUrl = urlparse(url)
    host = parsedUrl.netloc
    path = parsedUrl.path

    conn = http.client.HTTPSConnection(host)

    headers = {
        "User-Agent": f"({userAgent}, {email})"
    }

    conn.request("GET", path, headers=headers)

    response = conn.getresponse()

    if response.status == 200:
        data = json.loads(response.read().decode())
        #print("Request successful!")
        conn.close()
        return data
    else:
        print(f"Request failed with status code: {response.status}")
        print(response.read().decode())
        conn.close()
        return None

def send_simple_message(api_key, domain, recipient, sender, subject, text):
    host = f"api.mailgun.net"
    path = f"/v3/{domain}/messages"

    auth = base64.b64encode(f"api:{api_key}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = urlencode({
        "from": sender,
        "to": recipient,
        "subject": subject,
        "text": text
    })

    conn = http.client.HTTPSConnection(host)

    try:
        conn.request("POST", path, body, headers)
        response = conn.getresponse()
        return response.status, response.reason, response.read().decode()
    finally:
        conn.close()

weatherData = getWeatherData(url)
temperatureString = extractData(weatherData)

recipient = os.environ.get("TARGET_EMAIL")
APIKey = os.environ.get("MAILGUN_API_KEY")
domain = os.environ.get("MAILGUN_DOMAIN")
sender =  os.environ.get("MAILGUN_SENDER")
subject = temperatureString
text = "."

status, reason, response = send_simple_message(APIKey, domain, recipient, sender, subject, text)
print(f"Status: {status}")
print(f"Reason: {reason}")
print(f"Response: {response}")
