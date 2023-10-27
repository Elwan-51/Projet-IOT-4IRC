import discord
from discord.ext import tasks
import requests
import json

with open("config.json", 'r') as conf_file:
    config = json.load(conf_file)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
URL = f"http://{config['API']['URL']}:{config['API']['PORT']}"


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    mytask.start()


@tasks.loop(seconds=430)
async def mytask():
    for guild in client.guilds:
        cat = discord.utils.get(guild.categories, name="meteo")
        x = requests.get(f'{URL}/data/last/')
        data = x.json()
        for i in data:
            if i['type'] == 'lumi':
                await cat.channels[0].edit(name=f"Lumi : {i['value']}")
            if i['type'] == 'temp':
                await cat.channels[1].edit(name=f"Temp : {i['value']}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$temperature'):
        x = requests.get(f'{URL}/temp/last')
        data = x.json()
        await message.channel.send(f'Il fait : {data["value"]} °C')

    if message.content.startswith('$luminosite'):
        x = requests.get(f'{URL}/lumi/last')
        data = x.json()
        await message.channel.send(f'La luminosité est de : {data["value"]} lux')

    if message.content.startswith('$lastdata'):
        x = requests.get(f'{URL}/data/last/')
        data = x.json()
        lumi, temp = 0, 0
        for i in data:
            if i['type'] == 'lumi':
                lumi = i['value']
            if i['type'] == 'temp':
                temp = i['value']
        await message.channel.send(f'Luminosité : {lumi} lumen \nTempérature : {temp} °C')

client.run(config['DISCORD_BOT']['BOT_TOKEN'])