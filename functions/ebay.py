import asyncio
import requests
import json
import os
from prettytable import PrettyTable
import isodate
import logging

logger = logging.getLogger('cubebot.ebay')
logger.info("Functionality called")

#Does the work of the query, returns a big gross beautiful json object from ebay, generally in format dict[0][key][0][key][0]etc
async def queryEbay(query, maxPrice):
    appid = os.environ["EBAYAPPID"]
    url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByKeywords"
    #URL is URL+app id+filter configs & sort functions+max price filter + actual query
    instantiate = requests.get(url+"&SERVICE-VERSION=1.0.0&SECURITY-APPNAME="+appid+"&affiliate.trackingId=5338531779&affiliate.networkId=9&affiliate.customId=1&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&sortOrder=EndTimeSoonest&itemFilter.name=MaxPrice&itemFilter.value="+str(maxPrice)+"&keywords="+query)
    response = json.loads(instantiate.text)
    return response

#Right now this is just an extra sample output to see how to parse the json object from ebay
async def cliReturn(query, maxPrice):
    results = await queryEbay(query, maxPrice)
    listings = PrettyTable()
    listings.field_names = ["Title", "Price", "Time Left", "URL"]
    for i in results["findItemsByKeywordsResponse"][0]["searchResult"][0]["item"]:
        listings.add_row([i["title"][0][:25], i["sellingStatus"][0]["currentPrice"][0]["__value__"], isodate.parse_duration(i["sellingStatus"][0]["timeLeft"][0]), i["viewItemURL"][0]])
    listings.align["URL"] = "l"
    listings.align["Title"] = "l"
    print(listings)


#{u'findItemsByKeywordsResponse': [{u'itemSearchURL': [u'http://www.ebay.com/sch/i.html?_nkw=Sol+Ring+Masterpiec&fscurrency=USD&_ddo=1&_ipg=100&_mPrRngCbx=1&_pgn=1&_sop=1&_udhi=5'], u'paginationOutput': [{u'totalPages': [u'0'], u'entriesPerPage': [u'100'], u'pageNumber': [u'0'], u'totalEntries': [u'0']}], u'ack': [u'Success'], u'timestamp': [u'2018-06-05T14:22:32.580Z'], u'searchResult': [{u'@count': u'0'}], u'version': [u'1.13.0']}]}
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cliReturn("Wrath of God foil", 1000))
