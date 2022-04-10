# Standard libraries
import contextlib
import io
import logging
import os
from pydoc import Doc
from dotenv import load_dotenv

# Third party libraries
import textwrap
import datetime
import discord
import json
import motor.motor_asyncio
import asyncio
from traceback import format_exception

from discord.ext import commands
from pathlib import Path

# Local code
from utils.mongo import Document
from slash_cmd.permissions import Permissions
from slash_cmd.Ticket import Ticket_Commands

load_dotenv()
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

async def sync_slash_command(bot) -> None:
        """
        This function will sync every guild slash command.
        """
        # Waits until the client’s internal cache is all ready.
        await bot.wait_until_ready()
        for guild in bot.guilds:
            for slash_command in bot.slash_commands:
                try:
                    bot.tree.add_command(slash_command, guild=discord.Object(id=785839283847954433))
                except:
                    pass
            try:
                bot.tree.add_command(Ticket_Commands(bot), guild=discord.Object(id=785839283847954433))
                bot.tree.add_command(Permissions(bot), guild=discord.Object(id=785839283847954433))                
            except:
                pass
            await bot.tree.sync(guild=discord.Object(id=785839283847954433))
            

intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
bot = commands.Bot(
    description="commands List of Me",
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_ids=[488614633670967307, 301657045248114690],
    intents=intents,
    help_command=None
    #Help(ending_note=f"Made By Jay and Utki", show_cooldown=False,show_brief=True, timeout=60, timeout_delete=True),
)
# change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = os.getenv('TOKEN')
bot.connection_url = str(os.getenv('MONGO'))
bot.joke_api_key = os.getenv('DAD')
bot.logging_webhook = os.getenv('WEBHOOK')
bot.nuke_webhook = os.getenv('NUKE')
bot.Amri_token = os.getenv('AMRI')
bot.connection_money = os.getenv('MONGOMONEY')

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.blacklist_users = []
bot.slash_commands = []
bot.guild_id = [797920317871357972]
bot.cwd = cwd
bot.perm = {}
bot.afk_user = {}
bot.current_ban = {}
bot.version = "1.7"
bot.uptime = datetime.datetime.utcnow()
bot.automod = True
bot.current_vote = {}
bot.ban_event = {}
bot.total_suggestions = 0
bot.snipe = {}
bot.esnipe = {}
bot.config_data = {}
bot.guess_number = {}
bot.auto_mod_cache = {}

@bot.event
async def on_ready():
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Server Security"))

    current_blacklist_user = await bot.config.find(785839283847954433)
    for blacklisted_user in current_blacklist_user['blacklist']:
        bot.blacklist_users.append(blacklisted_user)

    current_banned_user = await bot.bans.get_all()
    for banned_user in current_banned_user:
        bot.current_ban[banned_user["_id"]] = banned_user
        
    current_afk_user = await bot.afk.get_all()
    for afk in current_afk_user:
        bot.afk_user[afk["_id"]] = afk

    votes = await bot.votes.get_all()
    for vote in votes:
        bot.current_vote[vote["_id"]] = vote

    battles = await bot.ban_backup.get_all()
    for bans in battles:
        bot.ban_event[bans["_id"]] = bans

    current_perm = await bot.active_cmd.get_all()
    for perm in current_perm:
        bot.perm[perm["_id"]] = perm
    
    current_config = await bot.config.get_all()
    for config in current_config:
        bot.config_data[config["_id"]] = config
    
    current_suggestions = await bot.suggest.get_all()
    bot.total_suggestions = len(current_suggestions)

    print("\n-----")
    print(f"Current blacklist:{len(bot.blacklist_users)}")
    print("\n-----")
    print(f"Current Bans:{len(bot.current_ban)}")
    print("\n-----")
    print("Database Connected\n-----")
    print("starting Slash Commands Sync\n-----")
    await sync_slash_command(bot)
    print("Slash Commands Sync Complete\n-----")
    # print("Starting Loading Extensions\n-----")
    print("Extensions Loaded\n-----")

@bot.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted list
    if message.author.id in bot.blacklist_users:
        return
    

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and len(message.content) == len(
        f"<@!{bot.user.id}>"
    ):
        data = await bot.config.find_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    await bot.process_commands(message)


async def Run_bot(bot: commands.Bot) -> None:

    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.moneyDB = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_money))
    bot.db = bot.mongo["tgk_database"]
    bot.db_money = bot.moneyDB["TGK"]
    bot.money = Document(bot.db_money, 'donorBank')
    bot.config = Document(bot.db, "config")
    bot.afk = Document(bot.db, "afk")
    bot.bans = Document(bot.db, "bans")
    bot.ticket = Document(bot.db, "ticket")
    bot.ticket_setup = Document(bot.db, "ticket_setup")
    bot.blacklist = Document(bot.db, "blacklist")
    bot.invites = Document(bot.db, "invites")
    bot.starboard = Document(bot.db, "starboard")
    bot.active_cmd = Document(bot.db, "Active_commands")
    bot.inactive_cmd = Document(bot.db, "inactive_commands")
    bot.embeds = Document(bot.db, "embeds")
    bot.votes = Document(bot.db, "Votes")
    bot.ban_backup = Document(bot.db, "ban_backup")
    bot.suggest = Document(bot.db, "suggestions")
    bot.april = Document(bot.db, "april")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            await bot.load_extension(f"cogs.{file[:-3]}")
    
    await bot.start(bot.config_token)

loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(Run_bot(bot))
except KeyboardInterrupt:
    print("\n-----\nShutting down...\n-----\n")
    loop.close()
    print("-----\nShutdown Complete\n-----\n")
