import lirc
import time
import json
import random
import html
import http.client
import startphrases
import scrollingtext

##############################################################
## Function to wait with blocking LIRC command for Power On ##
##############################################################
def waitForPowerOn():
    print("Waiting for IR POWER Input...")
    
    codeIR = []
    while (len(codeIR) == 0):
        codeIR = lirc.nextcode()

    #Power button pressed, begin sequence
    if powerBtnPressed(codeIR):
        print("Received POWER input")
        
        #Stop blocking behavior and restore variable
        lirc.set_blocking(False, sockid)
        scrollingtext.display(startphrases.get(random.randint(0, startphrases.size() - 1)))
        
        #Display Movie Suggestion
        #suggestMovie()
        
        getNewOnNetflix()
        
        #Begin Pushup Timer
        pushupTimer()

################################################################
## Function to determine if the power button has been pressed ##
################################################################
def powerBtnPressed(arr):
    #To debug, use: (arr[0] == "clear" or arr[0] == "press")
    if (arr != None and len(arr) > 0 and (arr[0] == "press")):
        return True
    else: return False

##############################################
## Function to retrieve anew Netflix titles ##
##############################################
def getNewOnNetflix():
    #Create HTTPS Connection to TMDB API
    conn = http.client.HTTPSConnection("unogs-unogs-v1.p.mashape.com")
    
    conn.request("GET", "/aaapi.cgi?q=get:new1:US&p=1&t=ns&st=adv", "", {
        "X-Mashape-Key": "PigYMeUYVOmshTe513GYkDHvW9WUp14a5npjsnflC3oXOXKtRd",
        "Accept": "application/json"
      })
    
    ##Send request and read response
    res = conn.getresponse()
    data = res.read()
    
    #Convert string response to JSON object
    dataObj = json.loads(data.decode("utf-8"))
    
    #Display movie count
    scrollingtext.display("There are " + dataObj["COUNT"] + " new titles on Netflix today. Press CH+ to view them.")
    
    wait = time.time()
    codeIr = []
    while (time.time() - wait < 5):
        codeIR = lirc.nextcode()
        if (len(codeIR) > 0 and codeIR[0] == "movie"):
            scrollingtext.display("Press CH+ after each movie to read its description: ")
            for i in range(int(dataObj["COUNT"])):
                #Get Netflix item
                item = dataObj["ITEMS"][i]
                
                #Construct message string
                message = str(i+1) + ") " + item["title"] + " ("
                if (len(item["type"]) > 0):
                    message += item["type"].capitalize() + ", "
                if (len(item["released"]) > 0):
                    message += item["released"] + ", "
                if (len(item["runtime"]) > 0):
                    message += item["runtime"] + ", "
                if (len(item["rating"]) > 0):
                    message += item["rating"]
                message += ")"
                
                #Display Netflix item on matrix
                scrollingtext.display(html.unescape(message))
                
                #Wait for user input
                titlewait = time.time()
                while(time.time() - titlewait < 2):
                    codeIR = lirc.nextcode()
                    if (len(codeIR) > 0 and codeIR[0] == "movie"):
                        scrollingtext.display(html.unescape(dataObj["ITEMS"][i]["synopsis"]))
                        time.sleep(1)
    
    scrollingtext.display("ZZzzz...")
    

#####################################################
## Function to retrieve a movie from TMBD database ##
#####################################################
def getMovie():
    #Random page number between 1-100, movie index between 1-20
    randPage = str(random.randint(1,25))
    randIndex = random.randint(0,19)
    
    #Create HTTPS Connection to TMDB API
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    
    #Create GET request to discover popular movies
    conn.request("GET", "/3/discover/movie?page=" + randPage + "&include_adult=true&sort_by=popularity.desc&language=en-US&api_key=2a85ce2e15ee40a32646565c65e33cb8", "{}")
    
    ##Send request and read response
    res = conn.getresponse()
    data = res.read()
    
    #Convert string response to JSON object
    dataObj = json.loads(data.decode("utf-8"))
    
    #Randomly select and display movie
    return dataObj["results"][randIndex]
    

#################################################
## Function to recommend a movie from TMDB API ##
#################################################
def suggestMovie():
    #Retrieve a movie from TMBD
    movie = getMovie()
    
    #If the movie has a NULL or OLD release year, get a new one
    while (len(movie["release_date"]) <= 0 or int(movie["release_date"].split("-")[0]) < 2008):
        movie = getMovie()
    
    #Display movie reommendation on matrix
    scrollingtext.display("I recommend " + movie["title"] +
                          " (" + movie["release_date"].split("-")[0] + ", " +
                          str(movie["vote_average"]) + "/10). Press the CH+ button to read more.")
    
    #Wait for optional button press to display overview
    print("Waiting 5s for optional overview input...")
    wait = time.time()
    while (time.time() - wait < 5):
        codeIR = lirc.nextcode()
        if (len(codeIR) > 0 and codeIR[0] == "movie"):
            scrollingtext.display(movie["overview"] + " (Title: " + movie["title"] + ")")
    


##############################################################
## Function to start pushup timer and handle any intercepts ##
##############################################################
def pushupTimer():
    print("Starting Pushup Timer...")
    
    #Set Intercepted flag
    intercepted = False
    
    #Store current timer
    startTime = time.time()
    
    #Pause for 60 minutes
    while(time.time() < startTime + 3600):
        #OFF Intercept
        codeIR = lirc.nextcode()
        if (len(codeIR) > 0):
            if codeIR[0] == "movie":
                print("Starting movie suggestion...")
                suggestMovie()
                print("Movie suggestion complete. Back to Pushup Timer...")
            elif codeIR[0] == "press":
                print("POWER OFF received, stopping timer and returning to root")
                scrollingtext.display("Goodbye")
                intercepted = True
                break
            elif codeIR[0] == "clear":
                scrollingtext.clear()
    
    #Restore state
    if intercepted:
        waitForPowerOn()
    else:
        scrollingtext.display("TIME FOR PUSHUPS!     TIME FOR PUSHUPS!     TIME FOR PUSHUPS!")
        
        #Restart timer only when message is finished displaying
        pushupTimer()

########################################
##              Service               ##
########################################
        #Block execution while waiting for power button press
sockid = lirc.init("pushuptimer", blocking=True)
waitForPowerOn()