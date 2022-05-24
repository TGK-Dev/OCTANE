from discord.ext import commands
from dotenv import load_dotenv
from utils.db import Document
from utils.help import EmbedHelpCommand
from discord import app_commands
from amari import AmariClient
from utils.callbacks import Argument_CallBack, Normal_CallBack
import discord
import os
import motor.motor_asyncio
import asyncio
import logging
import datetime

logging.basicConfig(level=logging.INFO)

main_guilds = [785839283847954433, 811037093715116072]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', description='GK Bot', case_insensitive=True, help_command=EmbedHelpCommand(), owner_id=488614633670967307, intents=discord.Intents.all(), application_id=816699167824281621)
    
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
        bot.starboard = Document(bot.db, 'starboard')
        bot.ticket = Document(bot.db, 'ticket')
        bot.warns = Document(bot.db, 'warns')
        bot.perms = Document(bot.db, 'perms')
        bot.cross_chat = Document(bot.db, 'cross_chat')
        bot.ban_backup = Document(bot.db, 'ban_backup')
        bot.invites = Document(bot.db, 'invites')
        bot.crosschat_blacklist = Document(bot.db, 'crosschat_blacklist')
        bot.quarantine = Document(bot.db, 'quarantine')
        bot.tags = Document(bot.db, 'tags')
        bot.Amari_api = AmariClient(bot.Amari_token)
        for file in os.listdir('./cogs'):
            if file.endswith('.py') and not file.startswith("_") and not file.startswith("votes"):
                await bot.load_extension(f'cogs.{file[:-3]}')

        await self.tree.sync(guild=discord.Object(main_guilds[0]))
        await self.tree.sync(guild=discord.Object(main_guilds[1]))

bot = Bot()

load_dotenv()
bot.token = os.environ['TOKEN']
bot.mongo_connection = os.environ['MONGO']
bot.Amari_token = os.environ['AMRI']
bot.connection_money = os.environ['MONGOMONEY']
bot.nuke_webhook = os.environ['NUKE_WEBHOOK']

#global bot atributes
bot.blacklist_users = []
bot.current_votes = {}
bot.current_bans = {}
bot.snipe = {'delete': {}, 'edit': {}}
bot.current_afk = {}
bot.current_mutes = {}
bot.guess_number = {}
bot.bot_temp_star = {}
bot.auto_mod_cache = {}
bot.perm = {}
bot.config_cache = {}
bot.cross_chat_blacklist = []
bot.ban_event = {}
bot.active_tag = {}
bot.uptime = datetime.datetime.utcnow()
bot.cross_chat_toggle = True

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
    
    current_perm = await bot.perms.get_all()
    for perm in current_perm:
        bot.perm[perm['_id']] = perm
    
    current_config = await bot.config.get_all()
    for config in current_config:
        bot.config_cache[config['_id']] = config
    
    current_ban_backup = await bot.ban_backup.get_all()
    for ban_backup in current_ban_backup:
        bot.ban_event[ban_backup['_id']] = ban_backup
    
    current_crosschat_blacklist = await bot.crosschat_blacklist.get_all()
    for crosschat_blacklist in current_crosschat_blacklist:
        bot.cross_chat_blacklist.append(crosschat_blacklist['_id'])
    
    current_tags = await bot.tags.get_all()
    for tag in current_tags:
        if tag['type'] == 'normal':
            commands = app_commands.Command(name=tag['_id'],description=tag['description'],callback=Normal_CallBack,guild_ids=[tag['guildID']])
            bot.active_tag[tag['_id']] = tag
            bot.tree.add_command(commands)
        
        elif tag['type'] == 'argument':
            commands = app_commands.Command(name=tag['_id'],description=tag['description'],callback=Argument_CallBack,guild_ids=[tag['guildID']])
            bot.active_tag[tag['_id']] = tag
            bot.tree.add_command(commands)

        print(f"added {commands.name}")
    
    await bot.tree.sync(guild=discord.Object(id=785839283847954433))
    await bot.tree.sync(guild=discord.Object(id=811037093715116072))
    print('Bot is ready')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.author.id in bot.blacklist_users:
        return
    
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(bot.token)