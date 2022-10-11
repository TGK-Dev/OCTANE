import discord
import datetime
from asyncio import TimeoutError
from discord.ext import commands, tasks
from discord import app_commands
from typing import Literal
from utils.db import Document
from ui.confirm import Confirm

class DankReminder(commands.GroupCog, name="dankreminder"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dank_reminders_cache = {}
        self.bot.dank_reminders = Document(self.bot.db, "dank_reminders")
    
    @staticmethod
    async def get_userdata(self, user: discord.Member):
        data = await self.bot.dank_reminders.get(user.id)
        if data is None:
            data = {
                "_id": user.id,
                "reminders": {},
                "enabled": True
            }
            await self.bot.dank_reminders.insert(data)
        return data

    @staticmethod
    async def make_cache(self):
        print("Caching dank reminders")
        data = await self.bot.dank_reminders.get_all()
        for user in data:
            self.bot.dank_reminders_cache[user["_id"]] = user
        print("Done caching dank reminders")

    @staticmethod
    async def get_cache(self, user: discord.Member):
        if user.id in self.bot.dank_reminders_cache.keys():
            return self.bot.dank_reminders_cache[user.id]
        else:
            return await self.get_userdata(self, user)
        
    @staticmethod
    async def update_data(self, user: discord.Member, data: dict):
        await self.bot.dank_reminders.update(data)
        self.bot.dank_reminders_cache[user.id] = data

    @commands.Cog.listener()
    async def on_ready(self):
        await self.make_cache(self)
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot: return
        if message.guild is None: return
        if message.guild.id != 785839283847954433: return
        if message.author.id != 270904126974590976: return
        if message.interaction is None: return

        if message.interaction.name == "work shift":
            self.bot.dispatch("dank_wrok_shift", message)
        if message.interaction.name == "crime":
            self.bot.dispatch("dank_crime", message)

    @commands.Cog.listener()
    async def on_dank_wrok_shift(self, message):
        user = message.interaction.user
        data = await self.get_cache(self, user)
        if data['enabled'] is False: return
        def check(m):
            embed = m.embeds[0]
            return embed.title == "Terrible work!" or "Great work!"

        try:
            await self.bot.wait_for('message_edit', check=check, timeout=60)
            
            if "work" not in data['reminders'].keys():
                view = Confirm(user, 60)
                msg = await message.reply(f"Hey! {user.mention} do you want me to remind you when you can use the work command again?", view=view)
                view.message = msg
                await view.wait()
                if view.value is True:
                    data['reminders']['work'] = {
                        "enabled": True,
                        "last_channel": message.channel.id,
                        "reminded": False,
                        "next_remider": datetime.datetime.now() + datetime.timedelta(minutes=60),
                        "last_used": datetime.datetime.now(),
                        "guild_id": message.guild.id
                    }
                    await self.update_data(self, user, data)
                    await view.interaction.response.edit_message(content="Alright! I will remind you when you can use the work command again!", view=None)
                    await message.add_reaction("<:octane_yes:1019957051721535618>")
                else:
                    await view.interaction.response.edit_message(content="Alright! I won't remind you when you can use the work command again!", view=None)
                    await message.add_reaction("<:octane_no:1019957051721535617>")
            else:
                if data['reminders']['work']['enabled'] is False: return
                data['reminders']['work']['reminded'] = False
                data['reminders']['work']['next_remider'] = datetime.datetime.now() + datetime.timedelta(minutes=60)
                await self.update_data(self, user, data)
                await message.add_reaction("<:octane_yes:1019957051721535618>")
        except TimeoutError:
            if message.embeds[0].title == "You just received a promotion!":
                pass

    @app_commands.command(name="toggle", description="Toggle a reminder")
    async def toggle(self, interaction: discord.Interaction, command: Literal['work'], enabled: bool):
        data = await self.get_userdata(self, interaction.user)
        if command not in data['reminders'].keys():
            data['reminders'][command] = {
                "enabled": True,
                "reminded": False,
                "next_remider": None,
                "last_channel": None,
                "guild_id": interaction.guild.id
            }
        
        if enabled is True:
            data['reminders'][command]['enabled'] = True
            await interaction.response.send_message("Reminder enabled!", ephemeral=True)
        else:
            data['reminders'][command]['enabled'] = False
            await interaction.response.send_message("Reminder disabled!", ephemeral=True)

        await self.bot.dank_reminders.update(data)
        self.bot.dank_reminders_cache[data["_id"]] = data

    @app_commands.command(name="view", description="View your reminders")
    async def view(self, interaction: discord.Interaction):
        data = await self.get_userdata(self, interaction.user)
        embed = discord.Embed(title="Dank Reminders", color=0x2F3136)
        for reminder in data['reminders'].keys():
            value = f"Enabled: {data['reminders'][reminder]['enabled']}"
            value += f"\nReminded: {data['reminders'][reminder]['reminded']}"
            value += f"\nNext Remider: {round(data['reminders'][reminder]['next_remider'].timestamp()) if data['reminders'][reminder]['next_remider'] is not None else 'None'}"
            value += f"Last Used: {round(data['reminders'][reminder]['last_used'].timestamp()) if data['reminders'][reminder]['last_used'] is not None else 'None'}"
            embed.add_field(name=reminder, value=value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(DankReminder(bot), guilds=[discord.Object(785839283847954433)])