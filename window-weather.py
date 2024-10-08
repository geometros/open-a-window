import http.client
import json
from urllib.parse import urlparse, urlencode
import os
import base64
from datetime import datetime, date

LOWER_BOUND = 42
UPPER_BOUND = 71

url = os.environ.get("GOV_WEATHER_API")
email = os.environ.get("TARGET_EMAIL") #this is sent to the weather API call as well as used for the email call, see https://www.weather.gov/documentation/services-web-api
userAgent = "window-weather"

def extractData(data): 
    dataList = data["properties"]["periods"]
    return dataList[0]["temperature"]
    
def getWeatherData(url,userAgent):

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

FLAG_FILE = os.environ.get("WINDOW_WEATHER_FLAG")

def worker():
    weatherData = getWeatherData(url,userAgent)
    currentTemp = extractData(weatherData)
    
    APIKey = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN")
    sender =  os.environ.get("MAILGUN_SENDER")
    subject = f"Temp in your area is {currentTemp} F, good time to open a window"
    text = "."
    
    if LOWER_BOUND < currentTemp < UPPER_BOUND:
        status, reason, response = send_simple_message(APIKey, domain, email, sender, subject, text)
        print(status, reason, response)
        with open(FLAG_FILE,'w') as f:
            f.write(datetime.now().strftime('%d %H'))
    else:
        print(currentTemp, "is out of bounds, notification not sent")

def should_run():
    if not os.path.exists(FLAG_FILE):
        return True
    with open(FLAG_FILE, "r") as f:
        hourDayNow = datetime.now().strftime('%d %H')
        hourDayNow = hourDayNow.split(' ')
        lastRun = f.read().strip()
        hourDayLastRun = lastRun.split(' ')
        if hourDayNow[0] == hourDayLastRun[0] and int(hourDayLastRun[1]) < 12 and int(hourDayNow[1]) > 12:
            return True
        if hourDayNow[0] != hourDayLastRun[0]:
            return True
        return False

if should_run(): 
    print(datetime.now(),"Running worker")
    worker()
else: 
    print(datetime.now(),"Script already ran too recently, exiting")

