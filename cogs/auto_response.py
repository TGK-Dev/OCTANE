from discord.ext import commands, tasks
from discord import app_commands
from discord import Interaction
from utils.converter import TimeConverter
from copy import deepcopy
import discord
import datetime

class Ar(commands.Cog, name="Auto Responce", description="Easy way to add Auto Responce"):
    def __init__(self, bot):
        self.bot = bot
        self.heist_ar = {}
        self.ar_check = self.heist_ar_check.start()
    
    def cog_unload(self):
        self.ar_check.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @tasks.loop(seconds=60)
    async def heist_ar_check(self):
        if self.heist_ar == {}:
            return
        current_ar = deepcopy(self.heist_ar)
        for guild in current_ar.keys():
            data = self.heist_ar[guild]
            if data['time'] <= datetime.datetime.now():
                #remove data from heist_ar
                del self.heist_ar[guild]

    @heist_ar_check.before_loop
    async def before_heist_ar_check(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        
        if message.channel.category_id in [932948559412748298, 785841152553123861,821807876812701706]: return
        
        if "heist" in message.content.lower() and self.heist_ar.keys() != []:
            print(f"{message.author.name} said heist")
            ar_data = self.heist_ar[message.guild.id]
            embed = discord.Embed(description=f"> **{ar_data['ammount']} Heist** **begins** <t:{round(ar_data['time'].timestamp())}:R>")
            if ar_data['role'] != None:
                embed.description += "\n> **Required Role:** <@&{}>".format(ar_data['role'])
            if ar_data['bypass_role'] != None:
                embed.description += "\n> **Bypass Role:** <@&{}>".format(ar_data['bypass_role'])
            embed.color = discord.Color.random()
            await message.reply(f"Heist will take place in <#{ar_data['channel']}>!!",embed=embed, delete_after=10)
        # elif "heist" in message.content.lower() and self.heist_ar == {}:
        #     await message.reply("There is currently no heist in progress take Heist ping from <#944670050252648468>", delete_after=10, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @app_commands.command(name="set-heist-ar", description="Set Auto Responce for Heist")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433, 811037093715116072)
    @app_commands.rename(remove_old="overwrite")
    async def set_heist_ar(self, interaction: Interaction, time: str, channel: discord.TextChannel, amount: str, role: discord.Role=None, remove_old: bool=False, bypass_role:discord.Role=None):
        times = await TimeConverter().convert(interaction, time)
        if time == 0:
            await interaction.response.send_message("Time is 0, no auto responce will be set", ephemeral=True)
            return
        
        if remove_old == False and interaction.guild.id in self.heist_ar.keys():
            await interaction.response.send_message("There is already an auto responce set", ephemeral=True)
            return
        
        time = datetime.datetime.now() + datetime.timedelta(seconds=times)
        self.heist_ar[interaction.guild.id] = {'_id': interaction.guild.id, 'time': time, 'channel': channel.id, 'ammount': amount, 'role': role.id if role else None, "expir": times, "bypass_role": bypass_role.id if bypass_role else None}
        await interaction.response.send_message("Auto Responce has been set", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ar(bot))