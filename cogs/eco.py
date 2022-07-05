import discord
from discord.ext import commands, tasks
from discord import app_commands
import typing
import datetime
from ui.booster_system import Booster_main
from utils.functions import make_inv
from discord.app_commands import Choice
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from humanfriendly import format_timespan
class Eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.booster_task = self.boost_task.start()
    
    def cog_unload(self):
        self.boost_task.cancel()

    @tasks.loop(seconds=5)
    async def boost_task(self):
        active_booster = deepcopy(self.bot.active_booster)
        now = datetime.datetime.utcnow()
        for key, value in active_booster.items():
            boost_end = value['started'] + relativedelta(seconds=value['duration'])
            if now > boost_end:
                self.bot.dispatch('booster_end', value)
                try:
                    self.bot.active_booster.pop(value['_id'])
                except KeyError:
                    pass
    
    @commands.Cog.listener()
    async def on_booster_end(self, data):
        guild = self.bot.get_guild(data['guildID'])
        user = guild.get_member(data['_id'])
        if data['type'] == "onex":
            role = guild.get_role(990128728250155019)
        elif data['type'] == "twox":
            role = guild.get_role(990128810101989376)
        await user.remove_roles(role)

        await self.bot.booster.delete(user.id)
        embed = discord.Embed(description=f"Your Exp Booster has Ended", color=discord.Color.green())
        embed.set_footer(text=f"{user.name}#{user.discriminator}", icon_url=user.avatar.url)
        try:
            await user.send(embed=embed)
        except:
            pass

    @boost_task.before_loop
    async def before_booster_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog is ready!")

    @app_commands.command(name="buy", description="Buy booster")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433)
    async def buy(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Select booster",color=discord.Color.random())
        view = Booster_main(self.bot, interaction)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_message()
    
    @app_commands.command(name="inventory", description="Check your inventory")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433)
    async def inventory(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Inventory",color=discord.Color.random())
        data = await self.bot.inv.find(interaction.user.id)
        if not data:
            embed.description = "user don't have any boosters"
            await interaction.response.send_message(embed=embed)
        else:
            onex, onex_booster = data['onex'], ""
            towx, towx_booster = data['twox'], ""

            for i in onex:
                onex_booster += f"**Duration: {i['name']}**\n> Quantity: {i['quantity']}\n"
            
            for i in towx:
                towx_booster += f"**Duration: {i['name']}**\n> Quantity: {i['quantity']}\n"
            
            embed.add_field(name="1x Booster", value=onex_booster, inline=True)
            embed.add_field(name="2x Booster", value=towx_booster, inline=True)

            await interaction.response.send_message(embed=embed)
                
    @app_commands.command(name="use", description="Use booster")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433)
    @app_commands.choices(booster=[Choice(name="1x Booster", value="onex"), Choice(name="2x Booster", value="twox")])
    @app_commands.choices(duration=[Choice(name="12 Hour", value=0), Choice(name="24 Hour", value=1), Choice(name="48 Hour", value=2), Choice(name="72 Hour", value=3)])
    async def use(self, interaction: discord.Interaction, booster: Choice[str], duration: Choice[int]):
        await interaction.response.defer(thinking=True)
        if interaction.user.id in self.bot.active_booster:
            await interaction.followup.send(f"You already have a booster active, wait for it to end")
            return
        data = await self.bot.inv.find(interaction.user.id)
        if not data:
            await interaction.followup.send("user don't have any boosters")
            await self.bot.inv.insert(make_inv(interaction.user.id))
            return
        if data[booster.value][duration.value]['quantity'] == 0:
            await interaction.followup.send("user don't have any boosters")
            return
        else:
            data[booster.value][duration.value]['quantity'] -= 1
            await self.bot.inv.update(data)
            if booster.value == "onex":
                role = discord.utils.get(interaction.guild.roles, id=990128728250155019)
            elif booster.value == "twox":
                role = discord.utils.get(interaction.guild.roles, id=990128810101989376)
            await interaction.user.add_roles(role)
            
            if duration.value == 0: duration = 7200
            elif duration.value == 1: duration = 86400
            elif duration.value == 2: duration = 172800
            elif duration.value == 3: duration = 259200

            booster_data = {'_id': interaction.user.id, 'duration': duration, 'started': datetime.datetime.utcnow(), 'type': booster.value, 'guildID': interaction.guild.id}
            await self.bot.inv.update(data)
            await self.bot.booster.insert(booster_data)
            self.bot.active_booster[interaction.user.id] = booster_data
        
            embed = discord.Embed(description=f"You have used a {booster.name} booster for {format_timespan(duration)}", color=discord.Color.green())
            embed.timestamp = datetime.datetime.utcnow()
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="gboost", description="Give booster to someone")
    @app_commands.guild_only()
    @app_commands.guilds(785839283847954433)
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(booster=[Choice(name="1x Booster", value="onex"), Choice(name="2x Booster", value="twox")])
    @app_commands.choices(duration=[Choice(name="12 Hour", value=0), Choice(name="24 Hour", value=1), Choice(name="48 Hour", value=2), Choice(name="72 Hour", value=3)])
    async def gboost(self, interaction: discord.Interaction, user: discord.Member, booster: Choice[str], duration: Choice[int], quantity: int = 1):
        await interaction.response.defer(thinking=True)
        data = await self.bot.inv.find(user.id)
        if not data:
            await interaction.followup.send("user don't have any boosters")
            await self.bot.inv.insert(make_inv(user.id))
            return
        data[booster.value][duration.value]['quantity'] += 1
        await self.bot.inv.update(data)

        embed = discord.Embed(description=f"you have given {quantity} {booster.name} booster to {user.name}", color=discord.Color.green())
        embed.timestamp = datetime.datetime.utcnow()
        await interaction.followup.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Eco(bot))