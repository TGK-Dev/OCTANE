import discord
import aiohttp

from discord.ext import commands
from discord import app_commands
from utils.db import Document
from ui.confirm import Confirm

class LinkedRole(commands.GroupCog, name="linkedrole"):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://discord.com/api/v10/"
        self.bot.auth = Document(self.bot.db, 'auth')
        self.bot.linked_config = Document(self.bot.db, 'linked_config')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded-----\n')
    
    @app_commands.command(name="verify", description="verify the connection for linked")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(link=[
        app_commands.Choice(name="Beast Donor", value="beast"),
    ])
    async def link_verfiy(self, interaction: discord.Interaction, user: discord.User, link: app_commands.Choice['str'], platform_name: str=None, platform_username: str=None, value: bool=None):
        auth_data = await self.bot.auth.find(user.id)
        if not auth_data:
            await interaction.response.send_message("User has not completed authentification", ephemeral=True)
            return
        
        value_value = 1 if value == True else 0
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {auth_data['access_token']}",
                "content-type": "application/json"
            }
            payload = {
                "platform_name": platform_name,
                "platform_username": platform_username,
                "metadata": {link.value: value_value}
                }

            async with session.put(f"{self.base_url}/users/@me/applications/{self.bot.user.id}/role-connection", headers=headers, json=payload) as r:
                await interaction.response.send_message(f"{await r.json()}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(LinkedRole(bot), guilds=[discord.Object(785839283847954433)])