from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from io import BytesIO
import logging
import os
import discord

selenium = os.environ["HUB"]

logger = logging.getLogger('cubebot.cubetutor')
logger.info('cog loaded')

async def CubeTutorPackChrome(cubeId, ctx, botmsg, bot):
    try:
        cubeId = int(cubeId)
    except Exception as e:
        logger.info("Failed to grab a cubeId\n"+str(e))
        await botmsg.edit(content="Please use an actual number at least")
        return False

    endpoint = "http://www.cubetutor.com/samplepack/"+str(cubeId)
    driver = webdriver.Remote(
        command_executor = selenium + "wd/hub",
        desired_capabilities = {"browserName": "chrome", "javascriptEnabled": True}
        )

    try:
        driver.get(endpoint)
    except Exception as e:
        logger.info("Failed to get cubetutor\n"+str(e))
        await tearDownClass(driver, ctx=ctx, botmsg=botmsg)
        
    try:
        gtfo = webdriver.common.action_chains.ActionChains(driver)
        gtfo.move_by_offset(100,100).perform()
        element = driver.find_element_by_id('main')
        elementPng = BytesIO(element.screenshot_as_png)
        await tearDownClass(driver, png=elementPng, ctx=ctx, botmsg=botmsg, bot=bot, cubeId=cubeId)
    except Exception as e:
        logger.info("Failed to grab a clean screenshot for "+str(cubeId)+str(e))
        await tearDownClass(driver, botmsg=botmsg)

async def tearDownClass(driver, png=None, ctx=None, botmsg=None, bot=None, cubeId=None): 
    driver.quit()
    if png:
        packImage = discord.File(png, "crack.png")
        await botmsg.delete()
        pack = await ctx.channel.send(str(ctx.author.name)+", react with \U0001F62C to regenerate the p1p1! http://cubetutor.com/viewcube/{0}".format(str(cubeId)), file=packImage)
        await pack.add_reaction('\U0001F62C')
        generate = await genPack(ctx, bot)
        if generate:
            await CubeTutorPackChrome(str(cubeId), ctx, pack, bot)
        if not generate:
            await pack.edit(content="Enjoy your picks! http://cubetutor.com/viewcube/{0}".format(str(cubeId)))
            await pack.clear_reactions()
    if not png:
        await botmsg.edit(content="Sorry, your pack couldn't be found. Please try again later.")

async def genPack(ctx, bot):
    def checkReaction(reaction, user):
        if ctx.message.author == user and str(reaction.emoji) == '\U0001F62C':
            return True
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=checkReaction)
    except Exception as e:
        logger.info("No response, leaving as is.\n"+str(e))
        return False
    else:
        return True
 
