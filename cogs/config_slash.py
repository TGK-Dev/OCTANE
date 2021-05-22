import asyncio
import datetime
import discord
import os
import platform
import random
import traceback
import utils.json_loader


from discord.ext import commands
from discord.ext.buttons import Paginator
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option

guild_ids = [797920317871357972,785839283847954433]
description= "Basic slash commands"

class config_slash(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @cog_ext.cog_slash(name="Ping", description="Gives Bot latency", guild_ids=guild_ids)
    async def ping(self, ctx):
        await ctx.send(f"Ping `{round(self.bot.latency * 1000)}`ms")


    @cog_ext.cog_slash(name="Status",
    	description="Change Bot Status to online & Dnd & idle",
    	guild_ids=guild_ids,
    	options=[
    	create_option(
    		name="arg",
    		description="Status options",
    		option_type=3,
    		required=True,
    		choices=[
    			create_choice(
    					name="dnd",
    					value="dnd",
    				),
    			create_choice(
    					name="online",
    					value="online",
    				),
    			create_choice(
    					name="idle",
    					value="idle",
    				)
    			]
    		)
    	]
    )				
    @commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636)
    async def status(self,ctx, arg):
        if arg.lower() == 'dnd':
            await self.bot.change_presence(status=discord.Status.dnd)
            await ctx.send('Bot status is Updated',hidden=True)
        elif arg.lower() == 'online':
            await self.bot.change_presence(status=discord.Status.online)
            await ctx.send('Bot status is Updated',hidden=True)
        elif arg.lower() == 'idle' :
            await self.bot.change_presence(status=discord.Status.idle)
            await ctx.send('Bot status is Updated',hidden=True)
        else: 
        	return 
        
def setup(bot):
    bot.add_cog(config_slash(bot))