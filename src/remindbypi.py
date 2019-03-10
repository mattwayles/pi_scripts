import json
import time
import http.client
import scrollingtext

print("Retrieving custom message:")
#Create HTTPS Connection to Firebase database
conn = http.client.HTTPSConnection("remindbypi.firebaseio.com")
    
#Create GET request to message endpoint
conn.request("GET", "/message.json", "{}")
    
##Send request and read response
res = conn.getresponse()
data = res.read()
    
#Convert string response to JSON object
dataObj = json.loads(data.decode("utf-8"))
if (dataObj == None):
    print("No new messages")
else:
    print(dataObj["message"])
    scrollingtext.display("New RemindByPi Message: " + dataObj["message"])