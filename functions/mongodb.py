import motor.motor_asyncio as mdb
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('cubebot.mongodb')
logger.info('MongoDB loaded')

client = mdb.AsyncIOMotorClient('localhost', 27017)

sotdb = client.sourceoftruth
sotdata = sotdb.sordata

csdb = client.cardstore
csdata = csdb.csdata

#Check for Source of Truth (EchoMTG list) is stale
async def validateSourceOfTruth(threshold): 
    logger.info("Validating SOT")

    dateThreshold = datetime.utcnow()-timedelta(days=threshold)

    latestEdit = await sotdata.find_one({"createdDate": {"$exists": "true", "$ne": "null"}})
    if latestEdit["createdDate"] > dateThreshold:
        print(latestEdit["createdDate"])
        print(await sotdata.count_documents({}))
        return True
    if latestEdit["createdDate"] < dateThreshold:
        print("Expired SOT!")
        return False
    if not latestEdit:
        print("Empty DB!")
        return False

#Store Source of Truth (EchoMTG list)
async def storeSourceOfTruth(cards):
    logger.info("Storing Source of Truth")    

    date = await sotdata.insert_one({"createdDate": datetime.utcnow()})
    
    store = await sotdata.insert_many(
        [value for key,value in cards["cards"].items()]
    )

    logger.info(len(store.inserted_ids))
    

#Purge Source of Truth
async def purgeSourceOfTruth():
    logger.info("Purging Source of Truth!")

    return await sotdata.drop()

#Query Source of Truth
async def querySourceOfTruth(query):
    logger.info("Querying Source of Truth")
    allCards = 50000

    results = sotdata.find({"name": {"$regex": query}})
    finale = []
    for result in await results.to_list(length=allCards):
        finale.append(result)
    print(finale)
    return finale 
 

#query card object for card store
async def queryCardCache(query):
    logger.info("Querying Card Store")

    results = csdata.find({"name": {"$regex": query}})
    finale = []
    for result in await results.to_list(length=100):
        finale.append(result)
    print(finale)
    return finale

#Clear expired Card Store caches
async def expireCardCache():
    logger.info("The Card Store Purge has begun!")

    result = await csdata.delete_many({
                 "expiration": { "$lt": datetime.utcnow()}
             })
    print(result)

#Create card object for Cache db
async def createCardCache(card, price=None, expiration=datetime.utcnow()+timedelta(hours=1), misc=[]):
    logger.info("Adding card to csdb")

    result = await csdata.update_one(
    { "echo_id": card["echo_id"]  },
    { "$set":
        {
            "name": card["name"],
            "echo_id": card["echo_id"],
            "expansion": card["expansion"],
            "multiverse_id": card["multiverse_id"],
            "set_code": card["set_code"],
            "expiration": expiration,
            "price": price,
            "misc": misc
        }
    }, upsert=True)

    print(result)

#Delete card object from Cache db
async def deleteCardCache(query):
    logger.info("Deleting: "+query)

    result = await csdata.delete_many({"name": {"$regex": query}})

    print(result)


if __name__ == "__main__":
    #Include executable testing
    sampleCards = {
        "cards": {
            "423758": {
                "multiverse_id": "423758",
                "echo_id": "101787",
                "name": "Pia's Revolution",
                "expansion": "Prerelease Cards",
                "set_code": "pPRE"
            },
            "100000012": {
                "multiverse_id": "100000012",
                "echo_id": "94746",
                "name": "Argothian Enchantress",
                "expansion": "Judge Promos",
                "set_code": "pJGP"
            },
            "100000013": {
                "multiverse_id": "100000013",
                "echo_id": "94747",
                "name": "Armageddon",
                "expansion": "Judge Promos",
                "set_code": "pJGP"
            }
        }}
 
    sampleCard = {
        'expansion': 'Judge Promos', 
        'set_code': 'pJGP', 
        'echo_id': '94747', 
        'multiverse_id': '100000013', 
        'name': 'Armageddon' 
    }

    loop = asyncio.get_event_loop()
    loop.run_until_complete(purgeSourceOfTruth()) 
    loop.run_until_complete(storeSourceOfTruth(sampleCards))
    loop.run_until_complete(validateSourceOfTruth(.01))
    loop.run_until_complete(querySourceOfTruth("rmag"))
    loop.run_until_complete(createCardCache(sampleCard))
    loop.run_until_complete(queryCardCache("rmag"))
    loop.run_until_complete(expireCardCache())
    loop.run_until_complete(deleteCardCache("rmag"))
    loop.run_until_complete(queryCardCache("rmag"))
