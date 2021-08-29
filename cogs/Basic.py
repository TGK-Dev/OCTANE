import asyncio
import discord
import os
from discord.ext.commands import converter
import psutil
import time
import platform
import random
import traceback
import datetime
from humanfriendly import format_timespan
import utils.json_loader


from discord.ext import commands

description = "Some Basic commands"


class Basic(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        start = self.bot.uptime
        now = datetime.datetime.utcnow()
        newtime = (now - start)
        total_s = newtime.total_seconds()

        dstart = datetime.datetime.utcnow()
        await self.bot.config.find(ctx.guild.id)
        dend = datetime.datetime.utcnow()
        dping = (dend - dstart)
        dping = dping.total_seconds()

        embed = discord.Embed(title="Pingss", color=ctx.author.colour,
            description=f"**Response TIme** {round(self.bot.latency * 1000)}ms\n**API**: {round((end_time - start_time) * 1000)}ms\n**Database Ping**: {round(dping * 1000)}Ms\n**My Age**: {format_timespan(total_s)}")

        await message.edit(content=None, embed=embed)
        
  
    @commands.command(
        name="stats", description="A useful command that displays bot statistics.", usage="stats"
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))
        cpu = round(psutil.cpu_percent(),1)

        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version:", value=self.bot.version)
        embed.add_field(name="Python Version:", value=pythonVersion)
        embed.add_field(name="Discord.Py Version", value=dpyVersion)
        embed.add_field(name="Total Guilds:", value=serverCount)
        embed.add_field(name="Total Users:", value=memberCount)
        embed.add_field(name="CPU Useage:", value=f"{str(cpu)}%")
        embed.add_field(name="RAM Useage:", value=f"{round(psutil.virtual_memory().percent,1)}%")
        embed.add_field(name="Bot Developers:", value="<@488614633670967307>\n<@301657045248114690>")
        embed.add_field(name="Embed Format:" , value="<@413651113485533194>\n<@651711446081601545>")

        embed.set_footer(text=f"Developed by Jay & Utik007 | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Basic(bot))
