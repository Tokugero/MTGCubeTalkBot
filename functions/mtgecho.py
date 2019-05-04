import time
import logging
import asyncio
import requests
import json
import os
import mongodb
from prettytable import PrettyTable

logger = logging.getLogger('cubebot.echomtg')

logger.info("Functionality loaded")

#Make an auth call to get a token. It expires super fast, so it has to be made with each call.
async def authGen():
    username = os.environ["MTGUSER"]
    password = os.environ["MTGPASS"]
    authUrl = "https://www.echomtg.com/api/user/auth/"
    payload = {"email":username, "password":password}
    instantiate = requests.post(authUrl,payload)
    result = json.loads(instantiate.text)
    return result["token"]

#Get the watchlist, paginates 100 items per request if needed
async def callWatchlist():
    start = 0
    end = 100
    inc = 100
    contents = []
    cont = True
    while cont:
        #Generates new auth with each request
        token = await authGen()
        watchUrl = "https://www.echomtg.com/api/watchlist/view/start="+str(start)+"&limit="+str(end)+"&auth="+token
        instantiate = requests.get(watchUrl)
        result = json.loads(instantiate.text)
        for i in result["items"]:
            contents.append(i)
        if len(contents) == end:
            start = end+1
            end = end+inc
        else:
            cont = False
    return contents

#Store Source of Truth
async def storeSourceOfTruth():
    token = await authGen()
    soturl = "https://www.echomtg.com/api/data/card_reference/auth="+token
    instantiate = requests.get(soturl)
    result = json.loads(instantiate.text)
    return await mongodb.storeSourceOfTruth(result)
    
#Add card to Watchlist
async def addWatchList(card):
    token = await authGen()
    watchUrl = "https://www.echomtg.com/api/watchlist/add/auth="+token+"&mid="+card["multiverse_id"]
    instantiate = requests.post(watchUrl)
    result = json.loads(instantiate.text)
    print(result)
    return result

#Delete card from Watchlist
async def rmWatchList(card):
    token = await authGen()
    watchUrl = "https://www.echomtg.com/api/watchlist/remove/id="+card["multiverse_id"]+"&auth="+token
    instantiate = requests.post(watchUrl)
    result = json.loads(instantiate.text)
    print(result)
    return result

#This is just for sample output, not actually used elsewhere
async def prettyWatchlist():
    rawData = await callWatchlist()
    watchList = PrettyTable()
    watchList.field_names = ["name", "set", "tcg_low", "tcg_mid", "foil_price"]
    for i in rawData:
        watchList.add_row([i["name"], i["set"], i["tcg_low"], i["tcg_mid"], i["foil_price"]])
    watchList.align["name"] = "l"
    watchList.align["foil_price"] = "r"
    print(watchList.get_string(sortby="foil_price"))
        

#Sample output if you wanted to call this method on its lonesome, just a sample of how to call
if __name__ == "__main__":
    sampleCard = { "expansion" : "Modern Masters 2015 Edition", 
                   "set_code" : "MM2", 
                   "multiverse_id" : "397729", 
                   "name" : "Brute Force", 
                   "echo_id" : "96267" }


    loop = asyncio.get_event_loop()
    #loop.run_until_complete(prettyWatchlist())
    #loop.run_until_complete(storeSourceOfTruth())
    loop.run_until_complete(addWatchList(sampleCard))
    loop.run_until_complete(rmWatchList(sampleCard))
