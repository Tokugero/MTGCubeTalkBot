from functions import cubetutor
import logging
import discord
import sys
import asyncio
import random
import requests
from discord.ext import commands

#shahrazad token ed98810941cf53fa9806f9aa9299c2 - This is only available internally and only executes the shahrazad test pipeline
logger = logging.getLogger('cubebot.cubebot')

logger.info("cubebot cog loaded")

class Application(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def p1p1(self, ctx, cubeId=None):
		"""Generate a P1P1 image given a cubetutor cube ID"""
		botmsg = await ctx.channel.send("Looking up pack...")
		if cubeId:
			try:
				cubeId = int(cubeId)
				logger.info(str(ctx.message.author) + " pulled a pack")
				packLoader = self.bot.loop.create_task(cubetutor.CubeTutorPackChrome(str(cubeId), ctx, botmsg, self.bot))
			except Exception as e:
				logger.info(e)
				await botmsg.edit(content="Please give me a real ID at least. ")
		if not cubeId:
			await botmsg.edit(content="I need an ID.")

def setup(bot):
	bot.add_cog(Application(bot))
