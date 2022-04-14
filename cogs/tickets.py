import asyncio
import chat_exporter
import discord
import io
from discord.ext import commands
from typing import Union
from utils.checks import checks
from Views.Ticket_panel import *
from Views.Ticket_panel import Ticket_Control
from Views.Ticket_panel import Support_model
description = "Ticket System For the Server Support"

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_panel(self.bot))
        self.bot.add_view(Ticket_Control(self.bot))
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')

    @commands.command()
    @commands.check_any(checks.is_me(), checks.can_use())
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=Ticket_panel(self.bot))

async def setup(bot):
    await bot.add_cog(Tickets(bot))
