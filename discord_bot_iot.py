import discord
from discord.ext import tasks, commands
import requests
import json

with open("config.json", 'r') as conf_file:
    config = json.load(conf_file)


intents = discord.Intents.default()
intents.message_content = True

URL = f"http://{config['API']['URL']}:{config['API']['PORT']}"
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    mytask.start()


@tasks.loop(seconds=430)
async def mytask():
    for guild in bot.guilds:
        cat = discord.utils.get(guild.categories, name="meteo")
        x = requests.get(f'{URL}/data/last/')
        data = x.json()
        for i in data:
            if i['type'] == 'lumi':
                await cat.channels[0].edit(name=f"Lumi : {i['value']}")
            if i['type'] == 'temp':
                await cat.channels[1].edit(name=f"Temp : {i['value']}")


@bot.command()
async def temp(ctx):
    x = requests.get(f'{URL}/temp/last')
    data = x.json()
    await ctx.channel.send(f'Il fait : {data["value"]} °C')


@bot.command()
async def lumi(ctx):
    x = requests.get(f'{URL}/lumi/last')
    data = x.json()
    await ctx.channel.send(f'La luminosité est de : {data["value"]} lux')
#


@bot.command()
async def lastdata(ctx):
    x = requests.get(f'{URL}/data/last/')
    data = x.json()
    lumi, temp = 0, 0
    for i in data:
        if i['type'] == 'lumi':
            lumi = i['value']
        if i['type'] == 'temp':
            temp = i['value']
    await ctx.channel.send(f'Luminosité : {lumi} lux \nTempérature : {temp} °C')


@bot.command()
async def setupapp(ctx):
    x = requests.get(f'{URL}/user/app/')
    await ctx.channel.send(x.content.decode())
bot.run(config['DISCORD_BOT']['BOT_TOKEN'])
