import os
import random
import platform
import traceback
import utils.json_loader
import asyncio
import discord


from discord.ext import commands
from discord.ext.buttons import Paginator

description = "Some Basic commands"

class Config(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    async def ping(self, ctx):
        message = await ctx.send(f'Ping') 
        await message.edit(content=f"Ping `{round(self.bot.latency * 1000)}`ms")
        
    @commands.command(name="Status", description="Change Bot Status to online & Dnd & idle", usage="[dnd & idle & online]", hidden=True)
    @commands.has_permissions(administrator=True)
    async def status(self,ctx, arg):
        if arg.lower() == 'dnd':
            await self.client.change_presence(status=discord.Status.dnd)
            await ctx.send('Bot status is Updated')
        elif arg.lower() == 'online':
            await self.client.change_presence(status=discord.Status.online)
            await ctx.send('Bot status is Updated')
        elif arg.lower() == 'idle' :
            await self.client.change_presence(status=discord.Status.idle)
            await ctx.send('Bot status is Updated')
        else: 
            await ctx.send(f':warning: {ctx.author.mention} Please provide valid status you dimwit!! :warning:')

    @commands.command(
        name="stats", description="A useful command that displays bot statistics.", usage="stats"
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

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
        embed.add_field(name="Bot Developers:", value="<@488614633670967307>\n<@301657045248114690>")

        embed.set_footer(text=f"Developed by Jay & Utik007 | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Config(bot))
