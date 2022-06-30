import discord
from discord.ext import commands
from utils.unbelievaboat.unbelievaboat import client
from discord import app_commands
import typing



class Eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eco_api = client(self.bot.eco_api)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog is ready!")

async def setup(bot):
    await bot.add_cog(Eco(bot))