import discord
from discord.ext import commands , tasks
from discord import app_commands, Interaction
from utils.db import Document
from ui.confirm import Confirm
import datetime
from typing import Literal
from enum import Enum

commands_cooldown = {
    "work shift": {'time': 3600, 'mention': "</work shift:1011560371267579942>"},
    "adventure": {'time': 300, 'mention': "</adventure:1011560371041095695>"},
    "stream": {'time': 600, 'mention': "</stream:1011560371267579938>"},
    "crime": {'time': 45, 'mention': "</crime:1011560371078832202>"},
    "beg": {'time': 45, 'mention': "</beg:1011560371041095699>"},
}

class command_list(Enum):
    work_shift = "work shift"
    adventure = "adventure"
    stream = "stream"
    crime = "crime"
    beg = "beg"


class dankremiders(commands.GroupCog, name="dankremiders"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dank_reminders = Document(self.bot.db, "dank_reminders")
        self.bot.dank_reminders_cache = {}
        self.dank_reminder_task = self.dank_reminder.start()
    
    def cog_unload(self):
        self.dank_reminder_task.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        current_data = await self.bot.dank_reminders.get_all()
        for data in current_data:
            if data['enabled'] == False:
                continue
            else:
                self.bot.dank_reminders_cache[data["_id"]] = data        
        print(self.bot.dank_reminders_cache)
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @tasks.loop(seconds=30)
    async def dank_reminder(self):
        current_time = datetime.datetime.now()
        for data in self.bot.dank_reminders_cache.values():
            if data['enabled'] == False:
                del self.bot.dank_reminders_cache[data["_id"]]
                continue
            
            for _type, reminder in data['reminders'].items():
                if reminder['enabled'] == False:
                    continue         
                if reminder['next_remider'] == None:
                    continue
                if reminder['reminded'] == True:
                    continue
                if current_time >= reminder['next_remider']:
                    self.bot.dispatch("dank_reminder", data, _type)


    
    @dank_reminder.before_loop
    async def before_dank_reminder(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_dank_reminder(self, data: dict, _type: str):
        print(f"dank_reminder event fired {_type}")
        reminder = data['reminders'][_type]
        guild = self.bot.get_guild(reminder['guild_id'])
        channel = guild.get_channel(reminder['last_channel'])
        user = guild.get_member(data['_id'])
        if user == None:
            del self.bot.dank_reminders_cache[data["_id"]]
            return

        if channel == None:
            data['reminders'][_type]['enabled'] = False
            data['reminders'][_type]['last_channel'] = None
            await self.bot.dank_reminders.update(data)
            del self.bot.dank_reminders_cache[data["_id"]]
        
        data['reminders'][_type]['reminded'] = True
        await channel.send(f"Hey {user.mention}! You can now use the command {commands_cooldown[_type]['mention']} again!")
        await self.bot.dank_reminders.update(data)
        self.bot.dank_reminders_cache[data["_id"]] = data

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild == None or message.interaction == None or not message.author.bot or message.guild.id != 785839283847954433 or message.author.id != 270904126974590976 or message.channel.category.id != 821807876812701706:
            return
        user = message.interaction.user
        data = await self.bot.dank_reminders.find(user.id)
        command = message.interaction.name

        if command not in commands_cooldown.keys():
            return
        
        if not data:
            view = Confirm(user, 60)
            msg = await message.reply(f"Hey {user.mention}! do you want to enable dankremiders for {commands_cooldown[command]['mention']} and other commands? (this will remind you when you can use the command again)", view=view)
            view.message = msg
            await view.wait()

            if view.value == True:
                data = {"_id": user.id,"enabled": True,"reminders": {}}
                await self.bot.dank_reminders.insert(data)
            elif view.value == False:
                await msg.edit(content="Ok, you can enable it later with `/dankremiders enable`")
                await view.interaction.response.send_message("Cancelled", ephemeral=True)
                return

            if command not in data['reminders'].keys():
                data['reminders'][command] = {
                    "enabled": True,
                    "reminded": False,
                    "guild_id": message.guild.id,
                    "last_channel": message.channel.id,
                    "next_remider": datetime.datetime.now() + datetime.timedelta(seconds=commands_cooldown[command]['time']),
                    "last_used": round(datetime.datetime.now().timestamp())
                }

            data['reminders'][command]['reminded'] = True
            data['reminders'][command]['guild_id'] = message.guild.id
            data['reminders'][command]['last_channel'] = message.channel.id
            data['reminders'][command]['next_remider'] = datetime.datetime.now() + datetime.timedelta(seconds=commands_cooldown[command]['time'])
            data['reminders'][command]['last_used'] = round(datetime.datetime.now().timestamp())

            await self.bot.dank_reminders.update(data)
            self.bot.dank_reminders_cache[data['_id']] = data
            await message.add_reaction("<:octane_yes:1019957051721535618>")
            await view.interaction.response.send_message("Reminder has been enabled!", ephemeral=True)
            await msg.edit(view=None, content="Reminders are now enabled, you can enable or disable other commands reminders by using the `dankreminders` command")
        else:
            if command not in data['reminders'].keys():
                data['reminders'][command] = {
                    "enabled": True,
                    "reminded": False,
                    "guild_id": message.guild.id,
                    "last_channel": message.channel.id,
                    "next_remider": datetime.datetime.now() + datetime.timedelta(seconds=commands_cooldown[command]['time']),
                    "last_used": round(datetime.datetime.now().timestamp())
                }
            else:
                data['reminders'][command]['reminded'] = False
                data['reminders'][command]['guild_id'] = message.guild.id
                data['reminders'][command]['last_channel'] = message.channel.id
                data['reminders'][command]['next_remider'] = datetime.datetime.now() + datetime.timedelta(seconds=commands_cooldown[command]['time'])
            await self.bot.dank_reminders.update(data)
            self.bot.dank_reminders_cache[data['_id']] = data
            await message.add_reaction("<:octane_yes:1019957051721535618>")

    @app_commands.command(name="manage", description="Manage your dank reminders")
    @app_commands.describe(reminder="The reminder you want to manage", toggle="Enable or disable the reminder")
    async def dankreminders_manage(self, interaction: Interaction, reminder: command_list, toggle: bool):
        data = await self.bot.dank_reminders.find(interaction.user.id)
        if not data:
            return await interaction.response.send_message("You don't have any dank reminders enabled!", ephemeral=True)
        if reminder.value not in data['reminders'].keys():
            data['reminders'][reminder.value] = {
                "enabled": toggle,
                "reminded": False,
                "guild_id": None,
                "last_channel": interaction.channel.id,
                "next_remider": None,
                "last_used": None
            }

        data['reminders'][reminder.value]['enabled'] = toggle
        await self.bot.dank_reminders.update(data)
        self.bot.dank_reminders_cache[data['_id']] = data
        await interaction.response.send_message(f"Successfully {'enabled' if toggle else 'disabled'} the reminder for {commands_cooldown[reminder.value]['mention']}", ephemeral=True)
    
    @app_commands.command(name="info", description="View your dank reminders")
    async def dankreminders_info(self, interaction: Interaction):
        embed = discord.Embed(color=0x2f3136, description="", title="Dank Reminders")
        data = await self.bot.dank_reminders.find(interaction.user.id)
        if not data:await interaction.response.send_message("You don't have any dank reminders set up", ephemeral=True)

        embed.description += f"**Global Status:** {'<:octane_yes:1019957051721535618>' if data['enabled'] == True else '<:octane_no:1019957208466862120>'}\n"
        for _type, reminder in commands_cooldown.items():
            if _type in data['reminders'].keys():
                value = f"Enabled: {'<:octane_yes:1019957051721535618>' if data['reminders'][_type]['enabled'] == True else '<:octane_no:1019957208466862120>'}\n"
                value += f"Reminded: {'<:octane_yes:1019957051721535618>' if data['reminders'][_type]['reminded'] == True else '<:octane_no:1019957208466862120>'}\n"
                value += f"Next reminder: <t:{round(data['reminders'][_type]['next_remider'].timestamp())}:R>\n" if data['reminders'][_type]['next_remider'] else "Next reminder: N/A\n"
                # value += f"Last used: <t:{data['reminders'][_type]['last_used']}:R>\n" if data['reminders'][_type]['last_used'] else "Last used: N/A\n"
                embed.add_field(name=_type.capitalize(), value=value)
            else:
                data['reminders'][_type] = {"enabled": False,"reminded": False,"guild_id": None,"last_channel": None,"next_remider": None,"last_used": None}
                value = f"Enabled: {'<:octane_yes:1019957051721535618>' if data['reminders'][_type]['enabled'] == True else '<:octane_no:1019957208466862120>'}\n"
                value += "Next reminder: N/A"
                embed.add_field(name=_type.capitalize(), value=value)
        await self.bot.dank_reminders.update(data)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(dankremiders(bot), guilds=[discord.Object(785839283847954433)])