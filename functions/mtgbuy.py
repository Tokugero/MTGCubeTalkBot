from . import mtgecho, mongodb, findall
import logging
import discord
import sys
import asyncio
import random
import requests
from discord.ext import commands

#shahrazad token ed98810941cf53fa9806f9aa9299c2 - This is only available internally and only executes the shahrazad test pipeline
logger = logging.getLogger('cubebot.mtgbuy')

logger.info("mtgbuy cog loaded")

def checkBotOwner(ctx):
    return 271543890828460032 == ctx.author.id

class Application(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checkBotOwner)
    async def resetSOT(self, ctx):
        await mongodb.purgeSourceOfTruth()
        await mtgecho.storeSourceOfTruth() 
        await ctx.send("Purge and Store completed.")

    @commands.group()
    async def buy(self, ctx):
        """Find a deal"""
        return 
    
    @buy.command()
    async def ebay(self, ctx, query=""):
        """Search ebay for cards cheaper than the average TCG Player Price."""
        if not query:
            await ctx.send("Provide a query, example: `$buy ebay Wrath of God|20`")
        return 

    @buy.command()
    async def tokus(self, ctx):
        """Buy some cards for Toku!"""
        watchList = await findall.findEbayWatchlist()
        for card in watchList:
            if not card["ebay"]:
                embed.add_field(name="Sorry, no cards found", value="...")
                await ctx.send(embed=embed)
            if card["ebay"]["results"]:
                for result in card["ebay"]["results"]:
                    result = sorted(result, key=lambda k: k['price'])
                    for listing in result:
                        embed = discord.Embed(title=card["card"]["name"], description=card["card"]["set_code"] + " | tcgplayer low: " + str(card["card"]["tcg_low"]) + " | tcgplayer foil: " + str(card["card"]["foil_price"]))
                        embed.set_thumbnail(url=listing["galleryUrl"])
                        embed.add_field(name=listing["currency"] + " " + listing["price"], value="["+listing["name"]+"]("+listing["url"]+")")
                        await ctx.send(embed=embed)
        return

    @buy.command()
    async def tcgplayer(self, ctx, *, query=""):
        """Get price ranges from tcgplayer"""
        logger.info(query)
        if not query:
            await ctx.send("Provide a query, example: `$buy tcgplayer Wrath of God`")
        if query:
            results = await mongodb.querySourceOfTruth(query)
            await ctx.send(str(results))
        return

def setup(bot):
    bot.add_cog(Application(bot))
