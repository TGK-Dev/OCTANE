from discord.ext import commands, tasks
from discord import app_commands
from discord import Interaction
from ui.models import Embed_Modal
from utils.converter import TimeConverter
import discord
import datetime

class Ar(commands.Cog, name="Auto Responce", description="Easy way to add Auto Responce"):
    def __init__(self, bot):
        self.bot = bot
        self.heist_ar = {}
        self.heist_ar_active = False
        self.ar_check = self.heist_ar_check.start()
    
    def cog_unload(self):
        self.ar_check.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @tasks.loop(seconds=10)
    async def heist_ar_check(self):
        if self.heist_ar_active == False:
            return
        if (self.heist_ar['time'] + datetime.timedelta(seconds=600)) < datetime.datetime.now():
            self.heist_ar = {}
            self.heist_ar_active = False
            return

    @heist_ar_check.before_loop
    async def before_heist_ar_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or self.heist_ar_active == False or message.guild.id != 785839283847954433:
            return
        
        if message.channel.id not in [785847439579676672, 799364834927968336,799378297855279125]: return
        # if message.author.guild_permissions.manage_messages:
        #     return
        
        if "heist" in message.content.lower():
            embed = discord.Embed(description=f"> **{self.heist_ar['ammount']} Heist** **begins** <t:{round(self.heist_ar['time'].timestamp())}:R>")
            if self.heist_ar['role'] != None:
                embed.description += "\n> **Required Role:** <@&{}>".format(self.heist_ar['role'])
            if self.heist_ar['bypass_role'] != None:
                embed.description += "\n> **Bypass Role:** <@&{}>".format(self.heist_ar['bypass_role'])
            embed.color = discord.Color.random()
            await message.reply(f"Heist will take place in <#{self.heist_ar['channel']}>!!",embed=embed, delete_after=10)

    @app_commands.command(name="set-heist-ar", description="Set Auto Responce for Heist")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433)
    @app_commands.rename(remove_old="overwrite")
    async def set_heist_ar(self, interaction: Interaction, time: str, channel: discord.TextChannel, amount: str, role: discord.Role=None, remove_old: bool=False, bypass_role:discord.Role=None):
        times = await TimeConverter().convert(interaction, time)
        if time == 0:
            await interaction.response.send_message("Time is 0, no auto responce will be set", ephemeral=True)
            return
        
        if remove_old == False and self.heist_ar != {}:
            await interaction.response.send_message("Auto Responce is already set\nSet overwrite to True", ephemeral=True)
            return
        
        time = datetime.datetime.now() + datetime.timedelta(seconds=times)
        self.heist_ar = {'_id': interaction.user.id, 'time': time, 'channel': channel.id, 'ammount': amount, 'role': role.id if role else None, "expir": times, "bypass_role": bypass_role.id if bypass_role else None}
        await interaction.response.send_message("Auto Responce has been set", ephemeral=True)
        self.heist_ar_active = True
        print(self.heist_ar)

async def setup(bot):
    await bot.add_cog(Ar(bot))