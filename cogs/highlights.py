from discord import app_commands
from discord.ext import commands, tasks
from copy import deepcopy
import datetime
import discord
from typing import List, Optional
import asyncio

class Highlight(commands.GroupCog, name="highlight", description="utils commands for highlights"):
    def __init__(self, bot):
        self.bot = bot
    
    async def remove_hl(self, interacton: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_hl = interacton.client.highlights.find(interacton.guild.id)
        if current_hl['tigger'] is None or current_hl['tigger'] < 0:
            return []
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in current_hl['tigger'] if current.lower() in name.lower()
        ]
        return choices[:24]

    @app_commands.command(name="add", description="Add an Trigger to the Highlight List")
    @app_commands.describe(tigger="The Trigger to add to the Highlight List")
    @app_commands.rename(tigger="word")
    async def add(self, interaction: discord.Interaction, tigger: str):
        data = await interaction.client.hightlights.find(interaction.user.id)
        if data is None:
            data = {
                '_id': interaction.user.id,
                'tigger': [],
                'ignore_channel':[],
                'last_react': None
            }
            await interaction.client.hightlights.insert(data)
            interaction.client.hl_chache[data['_id']] = data
        if tigger in data['tigger']:
            await interaction.response.send_message("This Trigger is already in the Highlight List", ephemeral=True)
            return
        else:
            if len(data['tigger']) >= 5:
                embed = discord.Embed(description="<:dynoError:1000351802702692442> | You have reached the maximum amount of Triggers allowed. Please remove one before adding another.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
            else:
                data['tigger'].append(tigger)
                await interaction.client.hightlights.update(data)
                interaction.client.hl_chache[data['_id']] = data
                embed = discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Added {tigger} to the Highlight List", color=discord.Color.green())
                await interaction.response.send_message(embed=embed)                
                return
    
    @app_commands.command(name="remove", description="Remove an Trigger from the Highlight List")
    @app_commands.describe(tigger="The Trigger to remove from the Highlight List")
    @app_commands.autocomplete(tigger=remove_hl)
    async def remove(self, interaction: discord.Interaction, tigger: str):
        data = await interaction.client.hightlights.find(interaction.user.id)
        if data is None:
            await interaction.response.send_message("This User dosn't have a Highlight List")
            return
        if tigger not in data['tigger']:
            embed = discord.Embed(description="<:dynoError:1000351802702692442> | This Trigger is not in the Highlight List, Please Select from auto-complete", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        else:
            data['tigger'].remove(tigger)
            await interaction.client.hightlights.update(data)
            embed = discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Removed {tigger} from the Highlight List", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
            interaction.client.hl_chache[data['_id']] = data
            return

    @app_commands.command(name="info", description="List all Triggers in the Highlight List", extras={'example': "/highlight info"})
    async def list(self, interaction: discord.Interaction):
        data = await interaction.client.hightlights.find(interaction.user.id)
        embed = discord.Embed(title="Highlight Info", color=discord.Color.blue())

        if data is None:
            embed.description = "This User dosn't have a Highlight List"
            await interaction.response.send_message(embed=embed)
            return

        embed.add_field(name="Triggers", value=f"{'.'.join(data['tigger']) if len(data['tigger']) > 0 else 'None'}")
        channels = []

        for channel in data['ignore_channel']:
            channels.append(f"<#{channel}>")
        
        embed.add_field(name="Ignore Channels", value=f"{'.'.join(channels) if len(channels) > 0 else 'None'}")
        embed.set_footer(text=f"Made by JAY#0138 & utki007#0007")
        embed.timestamp = datetime.datetime.utcnow()
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ignore", description="Add a Channel to the Highlight List")
    @app_commands.describe(channel="The Channel to add to the Highlight List")
    async def ignore(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = await interaction.client.hightlights.find(interaction.user.id)
        if data is None:
            await interaction.response.send_message("This User dosn't have a Highlight List")
            return
        if channel.id in data['ignore_channel']:
            await interaction.response.send_message("This Channel is already in the Highlight List")
            return
        else:
            data['ignore_channel'].append(channel.id)
            await interaction.client.hightlights.update(data)
            await interaction.response.send_message(f"{channel.name} has been added to the Highlight List")
            interaction.client.hl_chache[data['_id']] = data
            return
    
    @app_commands.command(name="unignore", description="Remove a Channel from the Highlight List")
    @app_commands.describe(channel="The Channel to remove from the Highlight List")
    async def unignore(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = await interaction.client.hightlights.find(interaction.user.id)
        if data is None:
            await interaction.response.send_message("This User dosn't have a Highlight List")
            return
        if channel.id not in data['ignore_channel']:
            await interaction.response.send_message("This Channel is not in the Highlight List")
            return
        else:
            data['ignore_channel'].remove(channel.id)
            await interaction.client.hightlights.update(data)
            await interaction.response.send_message(f"{channel.name} has been removed from the Highlight List")
            interaction.client.hl_chache[data['_id']] = data
            return
        
class Highlight_backend(commands.Cog, name="Votes",description="Server Vote counter with Top.gg"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.hl_chache = {}
        self.bot.ar_cache = {}
    
    async def highlight(self, message: discord.Message):
        if message.guild.id != 785839283847954433:
            return
        
        message_content = message.content.lower().split(" ")
        for key in self.bot.hl_chache.keys():
            data = self.bot.hl_chache[key]
            for msg in message_content:
                if msg in data['tigger']:
                    if message.channel.id in data['ignore_channel']:
                        return
                    if message.author.id == data['_id']:
                        return

                    async for cmsg in message.channel.history(limit=20, before=message):
                        if cmsg.author.id == data['_id']:
                            if not (message.created_at - cmsg.created_at).total_seconds() > 300:
                                return

                    channel_member_ids = [member.id for member in message.channel.members]
                    if data['_id'] not in channel_member_ids:
                        return
                    self.bot.dispatch("hl_trigger", message, data, msg)
    
    async def autoreactions(self, message: discord.Message):
        if message.author.bot: return
        if len(message.mentions) == 0: return

        for user in message.mentions:
            if user.id not in self.bot.ar_cache.keys():
                continue
            else:
                print("found ar")
                ar_data = self.bot.ar_cache[user.id]
                if ar_data['last_react'] is None or (datetime.datetime.utcnow() - ar_data['last_react']).total_seconds() > 20:
                    emoji = self.bot.get_emoji(ar_data['emoji'])
                    if emoji is None:
                        await message.guild.fetch_emoji(ar_data['emoji'])
                        if emoji is None:
                            continue
                    try:
                        await message.add_reaction(emoji)
                    except Exception as e:
                        print(e)
                        continue
                    
                    ar_data['last_react'] = datetime.datetime.utcnow()
                    self.bot.ar_cache[user.id] = ar_data
                

    @commands.Cog.listener()
    async def on_ready(self):
        all_hl = await self.bot.hightlights.get_all()
        for hl in all_hl: self.bot.hl_chache[hl['_id']] = hl
        for ar in await self.bot.autoreact.get_all(): 
            print(f"added: {ar['_id']}\n\t{ar['emoji']}")
            self.bot.ar_cache[ar['_id']] = ar

        print(f"{self.__class__.__name__} Cog has been loaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None: return
        if message.guild.id != 785839283847954433: return
        await self.highlight(message)
        await self.autoreactions(message)

    
    @commands.Cog.listener()
    async def on_hl_trigger(self, trigger_message: discord.Message, data: dict, trigger_key: str):
        channel = trigger_message.channel
        user = trigger_message.guild.get_member(data['_id'])
        await asyncio.sleep(5)

        embed = discord.Embed(title="You were Highlight", description="", color=discord.Color.blue())
        value = ""
        before_message = [message async for message in trigger_message.channel.history(limit=4, before=trigger_message)]

        #reverse the list
        before_message.reverse()
        for message in before_message:
            value += f"> [<t:{round(message.created_at.timestamp())}:R>]**{message.author.display_name}:** {message.content}\n"

        value += f"> [<t:{round(trigger_message.created_at.timestamp())}:R>]**{trigger_message.author.display_name}:** {trigger_message.content}\n"
        embed.add_field(name="Recent Messages:", value=value, inline=False)
        embed.add_field(name="Source", value=f"[Jump to Message]({trigger_message.jump_url})", inline=False)
        
        user = trigger_message.guild.get_member(data['_id'])

        if user is None:
            return print("User not found")
        try:
            await user.send(content=f"In **{message.guild.name}** {trigger_message.channel.mention}, you where mentioned with highlight word {trigger_key}",embed=embed)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(Highlight_backend(bot), guild=discord.Object(785839283847954433))
    await bot.add_cog(Highlight(bot), guild=discord.Object(785839283847954433))



