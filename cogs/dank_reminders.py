import discord
import datetime
from asyncio import TimeoutError
from discord.ext import commands, tasks
from discord import app_commands
from typing import Literal
from utils.db import Document
from ui.confirm import Confirm

class DankReminder(commands.GroupCog, name="dankreminder", description="Manage your dank reminders"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dank_reminders_cache = {}
        self.bot.dank_reminders = Document(self.bot.db, "dank_reminders")
        self.dank_reminder_task = self.dank_reminder.start()
        self.command_info = {"work_shift": "</work shift:1011560371267579942>", "crime":"</crime:1011560371078832202>", "adventure": "</adventure:1011560371041095695>"}
        self.message_in_progress = []
        self.reminder_task_on = False
    
    def cog_unload(self):
        self.dank_reminder_task.cancel()
    
    @tasks.loop(seconds=10)
    async def dank_reminder(self):
        if self.reminder_task_on == True:
            return
        self.reminder_task_on = True
        for key, value in self.bot.dank_reminders_cache.items():
            if value['enabled'] == False: continue
            for command, rm in value['reminders'].items():
                if rm['enabled'] == False: continue
                if rm['next_reminder'] <= datetime.datetime.now():
                    if rm['reminded'] == False:
                        self.bot.dispatch("dank_reminder", value, command)
        self.reminder_task_on = False
    
    @dank_reminder.before_loop
    async def before_dank_reminder(self):
        await self.bot.wait_until_ready()
    
    @staticmethod
    async def get_userdata(self, user: discord.Member):
        data = await self.bot.dank_reminders.find(user.id)
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
        data = await self.bot.dank_reminders.get_all()
        for user in data:
            self.bot.dank_reminders_cache[user["_id"]] = user

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

    @staticmethod
    async def delete_data(self, user_id: int):
        await self.bot.dank_reminders.delete(user_id)
        del self.bot.dank_reminders_cache[user_id]

    @commands.Cog.listener()
    async def on_ready(self):
        await self.make_cache(self)
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_dank_reminder(self, data: dict, _type: str):
        guild = self.bot.get_guild(data['reminders'][_type]['last_guild'])
        if guild is None: return
        channel = guild.get_channel(data['reminders'][_type]['channel'])
        user = guild.get_member(data['_id'])
        if user is None:
            try:
                user = await guild.fetch_member(data['reminders'][_type]['last_user'])
            except discord.NotFound:
                await self.delete_data(self, data['_id'])
        
        await channel.send(f"Hey {user.mention}, you can now use the command {self.command_info[_type]}")
        data['reminders'][_type]['reminded'] = True
        data['reminders'][_type]['last_reminder'] = datetime.datetime.now()
        await self.update_data(self, user, data)
        
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not message.author.id == 270904126974590976: return
        if message.guild is None: return
        interaction= message.interaction

        if interaction is None: return

        if interaction.name == "adventure":
            if isinstance(message.components[0].children[0], discord.components.SelectMenu):
                return
            else:
                self.bot.dispatch("adventure_done", message)
                        
                    

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.id != 270904126974590976: return
        if after.id in self.message_in_progress: return
        if not after.author.bot: return
        if after.guild is None: return

        if after.interaction is None: return

        if after.interaction.name == "work shift":
            embed = after.embeds[0]
            if embed.title == "Terrible work!" or "Great work!":
                self.bot.dispatch("dank_workShift_done", after, after.interaction)
        
        if after.interaction.name == "crime":
            if after.components[0].children[0].disabled == True and after.components[0].children[-1].disabled == True:
                self.bot.dispatch("dank_crime_done", after, after.interaction)

    @commands.Cog.listener()
    async def on_adventure_done(self, message: discord.Message):
        self.message_in_progress.append(message.id)
        user = message.interaction.user
        data = await self.get_cache(self, user)
        if "adventure" not in data['reminders'].keys():
            view = Confirm(user, 60)
            msg = await message.channel.send(f"Hey {user.mention}, would you like to enable reminders for {self.command_info['adventure']}?", view=view)
            view.message = msg
            await view.wait()
            if view.value:
                data['reminders']['adventure'] = {
                    "enabled": True,
                    "last_reminder": datetime.datetime.now(),
                    "next_reminder": datetime.datetime.now() + datetime.timedelta(minutes=3),
                    "reminded": False,
                    "channel": message.channel.id,
                    "last_user": user.id,
                    "last_guild": message.guild.id
                }
                await self.update_data(self, user, data)
                await msg.edit(content=f"Hey {user.mention}, I will remind you to use {self.command_info['adventure']} in 3 minutes!", view=None)
                await message.add_reaction("<:octane_yes:1019957051721535618>")
            else:
                await msg.edit(content=f"Hey {user.mention}, I won't remind you to use {self.command_info['adventure']}!", view=None)
                data['reminders']['adventure'] = {
                    "enabled": False,
                    "last_reminder": datetime.datetime.now(),
                    "next_reminder": datetime.datetime.now() + datetime.timedelta(minutes=3),
                    "reminded": False,
                    "channel": message.channel.id,
                    "last_user": user.id,
                    "last_guild": message.guild.id
                }
                await self.update_data(self, user, data)
        else:
            if data['reminders']['adventure']['enabled'] == True:
                data['reminders']['adventure']['last_reminder'] = datetime.datetime.now()
                data['reminders']['adventure']['next_reminder'] = datetime.datetime.now() + datetime.timedelta(minutes=3)
                data['reminders']['adventure']['reminded'] = False
                data['reminders']['adventure']['channel'] = message.channel.id
                await self.update_data(self, user, data)
                await message.add_reaction("<:octane_yes:1019957051721535618>")
        
        self.message_in_progress.remove(message.id)

    @commands.Cog.listener()
    async def on_dank_crime_done(self, message, interaction):
        self.message_in_progress.append(message.id)
        user = interaction.user
        data = await self.get_cache(self, user)
        if "crime" not in data['reminders'].keys():
            view = Confirm(user, 60)
            msg = await message.channel.send(f"Hey {user.mention}, would you like to enable reminders for {self.command_info['crime']}?", view=view)
            view.message = msg
            await view.wait()
            if view.value:
                data['reminders']['crime'] = {
                    "channel": message.channel.id,
                    "last_used": datetime.datetime.now(),
                    "last_guild": message.guild.id,
                    "enabled": True,
                    "reminded": False,
                    "next_reminder": datetime.datetime.now() + datetime.timedelta(seconds=44),
                    "last_reminder": None
                }
                await self.update_data(self, user, data)
                await view.interaction.response.edit_message(content=f"{user.mention}, you have set up a reminder for `/crime`!", view=None)
                await view.message.add_reaction("<:octane_yes:1019957051721535618>")
            else:
                await msg.edit(content=f"Ok {user.mention}, I will not set up a reminder for `/crime`.", view=None)
                data['reminders']['crime'] = {
                    "channel": message.channel.id,
                    "last_used": datetime.datetime.now(),
                    "last_guild": message.guild.id,
                    "enabled": False,
                    "reminded": False,
                    "next_reminder": None,
                    "last_reminder": None
                }
                await self.update_data(self, user, data)
                await view.message.add_reaction("<:octane_no:1019957208466862120>")
        else:
            if data['reminders']['crime']['enabled']:
                data['reminders']['crime']['last_reminder'] = datetime.datetime.now()
                data['reminders']['crime']['channel'] = message.channel.id
                data['reminders']['crime']['next_reminder'] = datetime.datetime.now() + datetime.timedelta(seconds=45)
                data['reminders']['crime']['reminded'] = False
                await self.update_data(self, user, data)
                await message.add_reaction("<:octane_yes:1019957051721535618>")

        self.message_in_progress.remove(message.id)
    
    @commands.Cog.listener()
    async def on_dank_workShift_done(self, message, interaction):
        self.message_in_progress.append(message.id)
        user = interaction.user
        data = await self.get_cache(self, user)
        if not data["enabled"]: return
        if "work_shift" not in data["reminders"].keys():
            print("work shift not in data adding")
            view = Confirm(user, 60)
            msg = await message.channel.send(f"Hey {user.mention}, would you like to enable reminders for {self.command_info['work_shift']}?", view=view)
            view.message = msg
            await view.wait()
            if view.value:
                data['reminders']['work_shift'] = {
                    "channel": message.channel.id,
                    "last_used": datetime.datetime.now(),
                    "last_guild": message.guild.id,
                    "enabled": True,
                    "reminded": False,
                    "next_reminder": datetime.datetime.now() + datetime.timedelta(hours=1),
                    "last_reminder": None
                }
                await self.update_data(self, user, data)
                await view.interaction.response.edit_message(content=f"Alright, I'll remind you when you can use `/work shift` again!", view=None)
                await message.add_reaction("<:octane_yes:1019957051721535618>")

            else:
                await msg.edit(content="Alright, I won't set a reminder for you")
                data['reminders']['work_shift'] = {
                    "channel": message.channel.id,
                    "last_used": datetime.datetime.now(),
                    "last_guild": message.guild.id,
                    "enabled": False,
                    "reminded": False,
                    "next_reminder": None,
                    "last_reminder": None
                }
                await self.update_data(self, user, data)
                await message.add_reaction("<:octane_no:1019957208466862120>")
                await view.message.edit(view=None)

                self.message_in_progress.remove(message.id)
                return
        else:
            if data['reminders']['work_shift']['enabled'] == False: return
            data['reminders']['work_shift']['last_used'] = datetime.datetime.now()
            data['reminders']['work_shift']['channel'] = message.channel.id
            data['reminders']['work_shift']['next_reminder'] = datetime.datetime.now() + datetime.timedelta(hours=1)
            data['reminders']['work_shift']['reminded'] = False
            await self.update_data(self, user, data)
            await message.add_reaction("<:octane_yes:1019957051721535618>")
        
        self.message_in_progress.remove(message.id)

    @app_commands.command(name="toggle", description="Toggle a reminder")
    @app_commands.describe(command="Command to toggle a reminder", enabled="Enable or disable a reminder")
    @app_commands.choices(command=[app_commands.Choice(name="All command", value="global"), app_commands.Choice(name="work shift", value="work_shift"), app_commands.Choice(name="crime", value="crime"), app_commands.Choice(name="adventure", value="adventure")])
    async def toggle(self, interaction: discord.Interaction, command: app_commands.Choice[str], enabled: bool):
        data = await self.get_cache(self, interaction.user)
        if command == "global":
            data["enabled"] = enabled
            await self.update_data(self, interaction.user, data)
            embed = discord.Embed(description=f"Alright, I have turned all reminders **{'<:Toggle_on:1029771260114243584>' if enabled else '<:Toggle_off:1029770614430498926>'}**", color=discord.Color.red() if not enabled else discord.Color.green())
            await interaction.response.send_message(embed=embed)
            return
        
        if command.value not in data["reminders"].keys():
            await interaction.response.send_message(f"You don't have a reminder set for `{command.value.replace('_', ' ')}`, use that command to set one up!", ephemeral=True)
        else:
            data["reminders"][command.value]["enabled"] = enabled
            await self.update_data(self, interaction.user, data)
            embed = discord.Embed(description=f"Alright, I have turned the `{command.value.replace('_', ' ')}` reminder **{'<:Toggle_on:1029771260114243584>' if enabled else '<:Toggle_off:1029770614430498926>'}**", color=discord.Color.red() if not enabled else discord.Color.green())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="view", description="View your reminders")
    async def view(self, interaction: discord.Interaction):
        data = await self.get_userdata(self, interaction.user)
        embed = discord.Embed(title="Dank Reminders", color=0x2F3136)
        for reminder in data['reminders'].keys():
            value = f"<:nat_reply:1011501024625827911> **Enabled:** {'<:Toggle_on:1029771260114243584>' if data['reminders'][reminder]['enabled'] else '<:Toggle_off:1029770614430498926>'}\n"
            value += f"<:nat_reply:1011501024625827911> **Reminded:** {'<:octane_yes:1019957051721535618>' if data['reminders'][reminder]['reminded'] else '<:octane_no:1019957208466862120>'}\n"
            if data['reminders'][reminder]['next_reminder'] is not None:
                value += f"<:nat_reply:1011501024625827911> **Next reminder:** <t:{round(data['reminders'][reminder]['next_reminder'].timestamp())}:R>\n"
            else:
                value += "<:nat_reply:1011501024625827911> <:nat_reply:1011501024625827911> **Next reminder:** None\n"
            if data['reminders'][reminder]['last_reminder'] is not None:
                value += f"<:nat_reply_cont:1011501118163013634> **Last reminder:** <t:{round(data['reminders'][reminder]['last_reminder'].timestamp())}:R>\n"
            else:
                value += "<:nat_reply_cont:1011501118163013634> **Last reminder:** None\n"
            
            name = reminder.replace('_', ' ')
            embed.add_field(name=name.capitalize(), value=value, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(DankReminder(bot))