import discord
from discord.ext import commands
from discord import app_commands
from captcha.image import ImageCaptcha
from utils.functions import Make_Verify_Code
from ui.buttons import Req_veriy_code
import string
import random


class Quarantined(commands.Cog, name="Quarantined", description="Server Member Verifaction Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Req_veriy_code(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @app_commands.command(name="verify", description="Force a member to verify")
    @app_commands.describe(member="The member to verify")
    @app_commands.guilds(785839283847954433)
    async def verify(self, interaction: discord.Interaction, member: discord.Member):
        if member.id in self.bot.owner_ids:
            await interaction.response.send_message("You can't verify an owner", ephemeral=True)
        
        await interaction.response.send_message("Starting Verification Process", ephemeral=True)
        
        verify_code = Make_Verify_Code()
        image = ImageCaptcha().generate(verify_code)
        await interaction.channel.send(f"Please type the following code in the channel to verify {member.mention}", file=discord.File(image, f"{member.id} verify.png"))
        await interaction.edit_original_message(content="Started")
    
    @app_commands.command(name="quarantine", description="Quarantine a member",)
    @app_commands.describe(member="The member to quarantine", reason="The reason for the quarantine")
    @app_commands.guilds(785839283847954433)
    async def quarantine(self, interaction: discord.Interaction, member: discord.Member, reason:str):
        if member.id in self.bot.owner_ids:
            await interaction.response.send_message("You can't quarantine an owner", ephemeral=True)
        
        await interaction.response.send_message("Starting Quarantine Process", ephemeral=True)
        
        data = {'_id': member.id, 'removed_roles': [], 'reason': ""}
        for role in member.roles:
            try:
                await member.remove_roles(role)
                data['removed_roles'].append(role.id)
            except: pass
        
        quarant_role = discord.utis.get(member.guild.roles, name="Quarantined")
        await member.add_roles(quarant_role)
        await interaction.edit_original_message(embed=discord.Embed(description=f"<:allow:819194696874197004> | {member.mention} has been quarantined for {reason}", color=0x00ff00))
        await self.bot.quarantined.insert(data)
    
    @app_commands.command(name="unquarantine", description="Unquarantine a member")
    @app_commands.describe(member="The member to unquarantine")
    @app_commands.guilds(785839283847954433)
    async def unquarantine(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message("Starting Unquarantine Process", ephemeral=True)
        
        data = await self.bot.quarantined.find({'_id': member.id})
        if data is None:
            await interaction.response.send_message("Member is not quarantined", ephemeral=True)
        
        for role in data['removed_roles']:
            try:
                await member.add_roles(discord.utils.get(member.guild.roles, id=role))
            except: pass
        
        quarant_role = discord.utils.get(member.guild.roles, name="Quarantined")
        await member.remove_roles(quarant_role)
        await interaction.edit_original_message(embed=discord.Embed(description=f"<:allow:819194696874197004> | {member.mention} has been unquarantined", color=0x00ff00))
        await self.bot.quarantined.delete({'_id': member.id})


async def setup(bot):
    await bot.add_cog(Quarantined(bot))