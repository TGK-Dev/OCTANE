from discord.ext import commands
from dotenv import load_dotenv
from utils.db import Document
from utils.help import EmbedHelpCommand
from amari import AmariClient
from utils.unbelievaboat import Client as eco_client
import discord
import os
import motor.motor_asyncio
import asyncio
import logging
import logging.handlers
import datetime

logger = logging.getLogger('discord')
handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

main_guilds = [785839283847954433]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', description='GK Bot', case_insensitive=True, help_command=EmbedHelpCommand(), owner_ids=[488614633670967307, 301657045248114690], intents=discord.Intents.all(), application_id=816699167824281621)
    
    async def setup_hook(self):
        bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(bot.mongo_connection)
        bot.moneyDB = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_money))
        bot.db_money = bot.moneyDB["TGK"]
        bot.money = Document(bot.db_money, 'donorBank')
        bot.db = bot.mongo['tgk_database']
        bot.config = Document(bot.db, 'config')
        bot.blacklist = Document(bot.db, 'blacklist')
        bot.suggestions = Document(bot.db, 'suggestions')
        bot.votes = Document(bot.db, 'Votes')
        bot.bans = Document(bot.db, 'bans')
        bot.afk = Document(bot.db, 'afk')
        bot.mutes = Document(bot.db, 'mutes')
        bot.tickets = Document(bot.db, 'tickets')
        bot.warns = Document(bot.db, 'warns')
        bot.perms = Document(bot.db, 'perms')
        bot.cross_chat = Document(bot.db, 'cross_chat')
        bot.ban_backup = Document(bot.db, 'ban_backup')
        bot.invites = Document(bot.db, 'invites')
        bot.crosschat_blacklist = Document(bot.db, 'crosschat_blacklist')
        bot.quarantine = Document(bot.db, 'quarantine')
        bot.inv = Document(bot.db, 'inv')
        bot.booster = Document(bot.db, 'booster')
        bot.ticket_system = Document(bot.db, 'ticket_system')
        bot.staff = Document(bot.db, 'staff')
        bot.crole = Document(bot.db, 'crole')
        bot.poll = Document(bot.db, 'poll')
        bot.hightlights = Document(bot.db, 'hightlights')
        bot.eco_api = eco_client(bot.eco_toekn)
        
        for file in os.listdir('./cogs'):
            if file.endswith('.py') and not file.startswith("_") and not file.startswith("crosschat"):
                await bot.load_extension(f'cogs.{file[:-3]}')

bot = Bot()

load_dotenv()
bot.token = os.environ['TOKEN']
bot.mongo_connection = os.environ['MONGO']
bot.Amari_token = os.environ['AMRI']
bot.connection_money = os.environ['MONGOMONEY']
bot.nuke_webhook = os.environ['NUKE_WEBHOOK']
bot.eco_toekn = os.environ['ECO_API']

#global bot atributes
bot.blacklist_users = []
bot.current_votes = {}
bot.current_bans = {}
bot.snipe = {'delete': {}, 'edit': {}}
bot.current_afk = {}
bot.current_mutes = {}
bot.guess_number = {}
bot.temp_star = []
bot.auto_mod_cache = {}
bot.perm = {}
bot.config_cache = {}
bot.cross_chat_blacklist = []
bot.ban_event = {}
bot.uptime = datetime.datetime.utcnow()
bot.cross_chat_toggle = True
bot.active_booster = {}
bot.polls = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} | {bot.user.id}")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name="Startup..."))

    current_vote = await bot.votes.get_all()
    for votes in current_vote:
        if votes['reminded'] == False:
            bot.current_votes[votes['_id']] = votes
    
    current_config = await bot.config.get_all()
    for config in current_config:
        bot.config_cache[config['_id']] = config
    
    current_ban_backup = await bot.ban_backup.get_all()
    for ban_backup in current_ban_backup:
        bot.ban_event[ban_backup['_id']] = ban_backup
    
    current_crosschat_blacklist = await bot.crosschat_blacklist.get_all()
    for crosschat_blacklist in current_crosschat_blacklist:
        bot.cross_chat_blacklist.append(crosschat_blacklist['_id'])
    
    current_active_booster = await bot.booster.get_all()
    for active_booster in current_active_booster:
        bot.active_booster[active_booster['_id']] = active_booster
    
    await bot.tree.sync(guild=discord.Object(main_guilds[0]))
    await bot.tree.sync(guild=discord.Object(988761284956799038))
    await bot.tree.sync()

    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Server Security"))

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.author.id in bot.blacklist_users:
        return
    
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(bot.token)