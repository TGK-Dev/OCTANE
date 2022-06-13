from discord.ext import commands
from discord import app_commands
from discord import Interaction
from ui.models import Embed_Modal
import discord

class Embed(commands.Cog, name="Embed", description="Easy way to create embed"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @app_commands.command(name="embed", description="Create an embed")
    @app_commands.guilds(785839283847954433)
    async def embed(self, interaction: Interaction):
        await interaction.response.send_modal(Embed_Modal(self.bot))

async def setup(bot):
    await bot.add_cog(Embed(bot))