import discord
from discord.ext import commands
from discord import app_commands
from captcha.image import ImageCaptcha
from utils.functions import Make_Verify_Code
import string
import random


class Quarantined(commands.Cog, name="Quarantined", description="Server Member Verifaction Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
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
        
        
async def setup(bot):
    await bot.add_cog(Quarantined(bot))