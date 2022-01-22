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

from traceback import format_exception

from discord.ext import commands
from pathlib import Path
from better_help import Help

# Local code
import utils.json_loader

from utils.mongo import Document
from utils.util import Pag
from utils.util import clean_code

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


intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
bot = commands.Bot(
    description="commands List of Me",
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_ids=[391913988461559809, 488614633670967307, 301657045248114690],
    help_command=Help(ending_note=f"Made By Jay and Utki", show_cooldown=False,
                      show_brief=True, timeout=60, timeout_delete=True),
    intents=intents,
)
# change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = os.getenv('TOKEN')
bot.connection_url = str(os.getenv('MONGO'))
bot.joke_api_key = os.getenv('DAD')

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.blacklist_users = []
bot.guild_id = [797920317871357972]
bot.cwd = cwd
bot.perm = {}
bot.afk_user = {}
bot.mod_role = [797923152617275433, 848585998769455104]
bot.version = "1.7"
bot.uptime = datetime.datetime.utcnow()
bot.automod = True
bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(status=discord.Status.dnd)

    os.system("pip uninstall -y discord.py==1.7.3")

    current_blacklist_user = await bot.config.find(785839283847954433)
    for blacklisted_user in current_blacklist_user['blacklist']:
        bot.blacklist_users.append(blacklisted_user)
        
    current_afk_user = await bot.afk.get_all()
    for afk in current_afk_user:
        bot.afk_user[afk["_id"]] = afk

    datas = await bot.ticket_setup.get_all()
    for data in datas:
        setup = json.dumps(data)
        bot.ticket_setups = json.loads(setup)

    try:
        permissions = await bot.perms.get_all()
        permission = json.dumps(permissions)
        bot.perm = json.loads(permission)
    except:
        pass

    print("\n-----")
    print(f"Current blacklist:{len(bot.blacklist_users)}")
    print("\n-----")
    print("Database Connected\n-----")


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


if __name__ == "__main__":
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["tgk_database"]
    bot.config = Document(bot.db, "config")
    bot.afk = Document(bot.db, "afk")
    bot.ticket = Document(bot.db, "ticket")
    bot.ticket_setup = Document(bot.db, "ticket_setup")
    bot.blacklist = Document(bot.db, "blacklist")
    bot.invites = Document(bot.db, "invites")
    bot.starboard = Document(bot.db, "starboard")
    bot.active_cmd = Document(bot.db, "Active_commands")
    bot.inactive_cmd = Document(bot.db, "inactive_commands")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_") and not file.startswith("test"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)