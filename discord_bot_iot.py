import discord
from discord.ext import tasks, commands
import requests
import json
import logging

logging.basicConfig(filename="/logs/app.log", level=logging.INFO, format='[%(asctime)s] - Discord BOT - %(levelname)s - %(message)s')

with open("config.json", 'r') as conf_file:
    config = json.load(conf_file)
    logging.info("Config Loaded")


# Bot configuration
intents = discord.Intents.default()
intents.message_content = True

URL = f"http://{config['API']['URL']}:{config['API']['PORT']}"
bot = commands.Bot(command_prefix='$', intents=intents)

# Bot definition
bot = commands.Bot(command_prefix=config['DISCORD_BOT']['PREFIX'], intents=intents)

# Bot definition
bot = commands.Bot(command_prefix=config['DISCORD_BOT']['PREFIX'], intents=intents)


# Bot starting event
@bot.event
async def on_ready():
    logging.info(f'We have logged in as {bot.user}')
    # Initialised planed task
    mytask.start()


# Looped task every 500 second
@tasks.loop(seconds=500)
async def mytask():
    # The task change the value the channel in the category meteo to display the last Luminosity and temperature
    for guild in bot.guilds:
        cat = discord.utils.get(guild.categories, name="meteo")
        x = requests.get(f'{URL}/data/last/')
        data = x.json()
        for i in data:
            if i['type'] == 'lumi':
                await cat.channels[0].edit(name=f"Lumi : {i['value']}")
            if i['type'] == 'temp':
                await cat.channels[1].edit(name=f"Temp : {i['value']}")
    logging.info("Channel name actualised")

# Command section


@bot.command()
async def temp(ctx):
    # Command that return the last temperature in the channel requesting the meteo
    x = requests.get(f'{URL}/temp/last')
    data = x.json()
    await ctx.channel.send(f'Il fait : {data["value"]} °C')
    logging.info("Temperature sent to channel")


@bot.command()
async def lumi(ctx):
    # Command that return the last luminosity in the channel requesting the meteo
    x = requests.get(f'{URL}/lumi/last')
    data = x.json()
    await ctx.channel.send(f'La luminosité est de : {data["value"]} lux')
    logging.info("Luminosity sent to channel")


@bot.command()
async def last_data(ctx):
    # Command that return the last luminosity and last temperature in the channel that request the meteo
    x = requests.get(f'{URL}/data/last/')
    data = x.json()
    lumin, temps = 0, 0
    for i in data:
        if i['type'] == 'lumi':
            lumin = i['value']
        if i['type'] == 'temp':
            temps = i['value']
    await ctx.channel.send(f'Luminosité : {lumin} lux \nTempérature : {temps} °C')
    logging.info("Data sent to channel")


@bot.command()
async def setupapp(ctx):
    # Command that register the first user used by the gateway to register data
    x = requests.get(f'{URL}/user/app/')
    await ctx.channel.send(x.content.decode())


# Bot startup
bot.run(config['DISCORD_BOT']['BOT_TOKEN'])
