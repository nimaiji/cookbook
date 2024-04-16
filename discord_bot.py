import discord
import requests
import os
from discord.ext import commands
from rasa_connection import curl_request


#Load Discord Bot Token
token = os.environ.get('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
	print(f'{client.user.name} has connected to Discord!')

#Wait for a new Message
@client.event
async def on_message(message):
	#Verify that the User is not the Bot itself

	if message.author != client.user and message.channel.name == 'cookbook-bot':
		if message.content == '!clear':
			return await message.channel.purge()
		#Use curl_request Function (located in rasa_connection.py)
		answers = curl_request(message.content, str(message.author))

		#Insert all Respons into one String so we can return it into the Discord Channel
		end_response = " \n ".join((answers))

		#Return the message in a Discord Channel
		return await message.channel.send(f'{message.author.mention} ' + end_response)

client.run(token)