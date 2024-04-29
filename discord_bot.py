import discord
import requests
import os
from discord.ext import commands
from rasa_connection import curl_request
import uuid
from roboflow import Roboflow

# import torch

# model = torch.hub.load("ultralytics/yolov5", "yolov5s", force_reload=False, skip_validation=True)  # or yolov5n - yolov5x6, custom


rf = Roboflow(api_key="blBiVdkya98dliasu6w4")
project = rf.workspace().project("ingredients-adzor")
model = project.version(2).model



#Load Discord Bot Token
token = os.environ.get('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
	print(f'{client.user.name} has connected to Discord!')

def is_image(atch):
	for i in ['jpg', 'jpeg', 'png']:
		if i in atch.filename.lower():
			return i
	return None

def download_image(atch, filename):
	print(f'Downloading {atch} as {filename}')
	img_data = requests.get(atch).content
	with open('./assets/downloaded/' + filename, 'wb') as handler:
		handler.write(img_data)

def detect_ingrd(path):
	res = model.predict(path, confidence=40, overlap=30).json()
	predictions = res['predictions']
	classes = []
	for pred in predictions:
		print(pred)
		classes.append(pred['class'])
	return classes

#Wait for a new Message
@client.event
async def on_message(message):
	#Verify that the User is not the Bot itself
	if message.content == '!clear':
		return await message.channel.purge()
	if message.author != client.user and message.channel.name == 'cookbook-bot':
		content = message.content

		#Check if the Message contains an Image
		if len(message.attachments) > 0:
			ingredients = []
			for atch in message.attachments:
				format = is_image(atch)
				if format:
					unique_id = str(uuid.uuid4()) + '.' + format
					download_image(str(atch), unique_id)
					ingredients += detect_ingrd('./assets/downloaded/' + unique_id)
			ingredients = list(set(ingredients))
			content = 'I have: ' + ', '.join(ingredients)
					
		print(f'{message.author} said: {content}')
		#Use curl_request Function (located in rasa_connection.py)
		answers = curl_request(content, str(message.author))

		#Insert all Respons into one String so we can return it into the Discord Channel
		end_response = " \n ".join((answers))

		#Return the message in a Discord Channel
		return await message.channel.send(f'{message.author.mention} ' + end_response)

client.run(token)