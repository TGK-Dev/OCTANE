import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import datetime

class BanAppeal(commands.Cog, name="Ban Appeal", description="Easy way to add Ban Appeal"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.command(name='check', description='check reason of ban from main server')
    @app_commands.checks.has_any_role(988764089713066005)
    @app_commands.guilds(988761284956799038)
    async def check(self, interaction: discord.Interaction, user: discord.Member):
        user = await interaction.client.fetch_user(user.id)
        main_guild = interaction.client.get_guild(785839283847954433)
        try:
            ban = await main_guild.fetch_ban(user)
            embed = discord.Embed(description=f"Reason: {ban.reason}", color=0x00ff00)
            await interaction.response.send_message(embed=embed)
        except:
            embed = discord.Embed(description="ban not found", color=0xff0000)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="approve", description="Approve a ban appeal")
    @app_commands.guild_only()
    @app_commands.guilds(988761284956799038)
    @app_commands.checks.has_any_role(988764089713066005)
    async def approve(self, interaction: Interaction, user: discord.Member):
        main_guild = await self.bot.fetch_guild(785839283847954433)
        try:
            ban = await main_guild.fetch_ban(user)
            if ban:
                await main_guild.unban(user, reason="Ban Appeal Approved by {}".format(interaction.user.name))
                await interaction.response.send_message("Ban Appeal Approved", ephemeral=True)
                await interaction.channel.send(f"{user.mention} Your ban has been lifted by {interaction.user.mention}, you can now rejoin the server at https://discord.gg/uJeHDqpCVw")
        except discord.NotFound:
            await interaction.response.send_message("User is not banned")
            return        

    @app_commands.command(name="deny", description="Deny a ban appeal")
    @app_commands.guild_only()
    @app_commands.guilds(988761284956799038)
    @app_commands.checks.has_any_role(988764089713066005)
    async def deny(self, interaction: Interaction, user: discord.Member, reason: str=None):
        main_guild = await self.bot.fetch_guild(785839283847954433)
        try:
            await user.send("Your ban appeal has been denied\n`Reason:` {}".format(reason))
        except discord.HTTPException:
            pass
        
        await interaction.response.send_message("User Appeal has been denied")

async def setup(bot):
    await bot.add_cog(BanAppeal(bot))
