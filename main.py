from discord.ext import commands
from dotenv import load_dotenv
from utils.db import Document
from utils.help import EmbedHelpCommand
import discord
import os
import motor.motor_asyncio
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(
    command_prefix='gk.', 
    description='GK Bot', 
    case_insensitive=True, 
    help_command=EmbedHelpCommand(), 
    owner_id=488614633670967307, 
    intents=discord.Intents.all())

#bot envs 
load_dotenv()
bot.token = os.environ['TOKEN']
bot.mongo_connection = os.environ['MONGO']

#global bot atributes
bot.blacklist_users = []
bot.current_votes = {}
bot.current_bans = {}
bot.snipe = {'delete': {}, 'edit': {}}
bot.current_afk = {}
bot.current_mutes = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} | {bot.user.id}")
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Server Security"))

    current_vote = await bot.votes.get_all()
    for votes in current_vote:
        bot.current_votes[votes['_id']] = votes
    
    current_ban = await bot.bans.get_all()
    for bans in current_ban:
        bot.current_bans[bans['_id']] = bans
    
    current_afk = await bot.afk.get_all()
    for afk in current_afk:
        bot.current_afk[afk['_id']] = afk
    
    current_mute = await bot.mutes.get_all()
    for mute in current_mute:
        bot.current_mutes[mute['_id']] = mute
    
    await bot.tree.sync(guild=discord.Object(964377652813234206))
    print('Bot is ready')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.author.id in bot.blacklist_users:
        return
    
    await bot.process_commands(message)

async def run_bot():

    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(bot.mongo_connection)
    bot.db = bot.mongo['db']
    bot.config = Document(bot.db, 'config')
    bot.blacklist = Document(bot.db, 'blacklist')
    bot.suggestions = Document(bot.db, 'suggestions')
    bot.votes = Document(bot.db, 'votes')
    bot.bans = Document(bot.db, 'bans')
    bot.afk = Document(bot.db, 'afk')
    bot.mutes = Document(bot.db, 'mutes')

    for file in os.listdir('./cogs'):
        if file.endswith('.py') and not file.startswith("_"):
            await bot.load_extension(f'cogs.{file[:-3]}')
    
    await bot.start(bot.token)

loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(run_bot())
except KeyboardInterrupt:
    print("\nClosing bot...")
    loop.close()
    print("Closed.")