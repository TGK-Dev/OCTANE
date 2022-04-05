import discord
from utils.checks import checks
from discord.ext import commands
from discord import app_commands
from typing import Union, List

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded-----')

async def setup(bot):
    await bot.add_cog(Help(bot))
