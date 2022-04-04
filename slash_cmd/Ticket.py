from discord import app_commands, Interaction
from typing import Union, Optional, List
from discord.app_commands import Choice
import discord

import asyncio
from utils.checks import checks
import chat_exporter
import io
from Views.Ticket_panel import Ticket_Control
class Ticket_Commands(app_commands.Group):
    def __init__(self, bot, name="ticket"):
        super().__init__(name=name)
        self.bot = bot

    async def on_error(self, interaction: Interaction, command: app_commands.Command, error: app_commands.AppCommandError) -> None:
        
        embed = discord.Embed(title="Error", description=f"Error: {error}", color=0xFF0000)
        try:
            await interaction.followup.send(embed=embed)
        except:
            await interaction.response.send_message(embed=embed)

    
    @app_commands.command(name="edit", description="Edit current ticket")
    @app_commands.describe(option="Select Edit Options")
    @app_commands.describe(target="Role/User")
    @app_commands.choices(option=[
        Choice(name="Add", value=1),
        Choice(name="Remove", value=2),
        Choice(name="Panel", value=3)
    ])
    
    async def edit(self, interaction: Interaction, option: Choice[int], target: Union[discord.Role, discord.Member]=None):
        if option.value == 1:
            await interaction.response.defer(thinking=True)

            can_run = await checks.slash_check(self.bot, interaction, "add")
            if can_run != True:
                return await interaction.followup.send("You do not have permission to run this command")

            data = await self.bot.ticket.find(interaction.channel.id)
            if data is None and interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
                return await interaction.followup.send("This is not a ticket channel", ephemeral=True)

            if type(target) == discord.Role:
                if target.id in data['added_roles']:
                    return await interaction.followup.send("This role is already added to the ticket")
                else:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.view_channel = True
                    overwrite.send_messages = True
                    overwrite.read_messages = True
                    overwrite.attach_files = True
                    await interaction.channel.set_permissions(target, overwrite=overwrite)
                    data['added_roles'].append(target.id)
                    await self.bot.ticket.upsert(data)

            elif type(target) == discord.Member:
                if target.id in data['added_users']:
                    return await interaction.response.send_message("This user is already added to the ticket")
                else:
                    overwrite = discord.PermissionOverwrite()
                    overwrite.view_channel = True
                    overwrite.send_messages = True
                    overwrite.read_messages = True
                    overwrite.attach_files = True
                    await interaction.channel.set_permissions(target, overwrite=overwrite)
                    data['added_users'].append(target.id)
                    await self.bot.ticket.upsert(data)

            await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | {target.mention} added to the ticket", color=0x2f3136))

            log_embed = discord.Embed(color=0x00FF00)
            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Added {target.mention} to the ticket")
            return await log_channel.send(embed=log_embed)
        
        if option.value == 2:
            await interaction.response.defer(thinking=True)

            can_run = await checks.slash_check(self.bot, interaction, "remove")
            if can_run != True:
                return await interaction.followup.send("You do not have permission to run this command")

            data = await self.bot.ticket.find(interaction.channel.id)
            if data is None and interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
                return await interaction.response.send_message("This is not a ticket channel", ephemeral=True)

            if isinstance(target, discord.Role):
                if target.id not in data['added_roles']:
                    await interaction.response.send_message("This role is not added to the ticket")
                else:
                    await interaction.channel.set_permissions(target, overwrite=None)
                    data['added_roles'].remove(target.id)
                    await self.bot.ticket.upsert(data)

            elif isinstance(target, discord.Member):
                if target.id not in data['added_users']:
                    await interaction.response.send_message("This user is not added to the ticket")
                else:
                    await interaction.channel.set_permissions(target, overwrite=None)
                    data['added_users'].remove(target.id)
                    await self.bot.ticket.upsert(data)

            await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | {target.mention} removed from the ticket", color=0x2f3136))

            log_embed = discord.Embed(color=0xFF0000)
            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Removed {target.mention} from ticket")
            await log_channel.send(embed=log_embed)
        
        if option.value == 3:
            Panel_embed = discord.Embed(title="Ticket Control Panel",color=0x008000)
            data = await self.bot.ticket.find(interaction.channel.id)
            Panel_embed.description = f"""**Open**: To Open current Ticket\n**Close**: To Close current Ticket\n**Secure**: Make Ticket Adminitrator Only\n**Save**: Save Ticket Transhcript\n**Delete**: Delete Ticket\n6.**Add Shero**: add Shero bot to Ticket only works in Partnership Ticket\n"""
            View = Ticket_Control(self.bot)
            if data['type'] == "Partnership":
                pass
            else:
                for button in View.children:
                    if button.label == "Add Shero":
                        item = button
                        break
                View.remove_item(item)
            await interaction.response.send_message(embed=Panel_embed, view=Ticket_Control(self.bot))

    # @app_commands.command(name="config", description="Configure the ticket system")
    # @app_commands.describe(category="category of ticket")
    # @app_commands.describe(support_role="support role of system")
    # @app_commands.describe(pm_role="partner manager role of system")
    # @app_commands.describe(transcript="transcript channel of system")
    # @app_commands.describe(ticket_log="ticket log channel of system")
    # async def config(self, interaction: Interaction, category: discord.CategoryChannel=None, support_role: discord.Role=None, pm_role: discord.Role=None, transcript: discord.TextChannel=None, ticket_log: discord.TextChannel=None):        
    #     can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
    #     if can_run != True:
    #         return await interaction.followup.send("You do not have permission to run this command")

    #     data = await self.bot.config.find(interaction.guild.id)
    #     if data is None:
    #         data = {'_id': interaction.guild.id, 'ticket_category': None, 'support_role': None}

    #     if category:
    #         data['ticket_category'] = category.id

    #     if support_role:
    #         data['support_role'] = support_role.id

    #     if pm_role:
    #         data['pm_role'] = pm_role.id

    #     if transcript:
    #         data['transcript_log_channel'] = transcript.id
    #     if ticket_log:
    #         data['ticket_log_channel'] = ticket_log.id

    #     if support_role or category or pm_role or transcript or ticket_log:
    #         await self.bot.config.upsert(data)
    #         await interaction.response.send_message("Configuration Updated")
    #     else:
    #         embed = discord.Embed(title="Ticket Config", color=0x2f3136)
    #         embed.add_field(name="Ticket Category", value=f"<#{data['ticket_category']}>")
    #         embed.add_field(name="Support Role", value=f"<@&{data['support_role']}>")
    #         embed.add_field(name="Partner Manager Role", value=f"<@&{data['pm_role']}>")
    #         embed.add_field(name="Transcript Log Channel", value=f"<#{data['transcript_log_channel']}>")
    #         embed.add_field(name="Ticket Log Channel", value=f"<#{data['ticket_log_channel']}>")
    #         embed.set_footer(text="Made by Jay and utki007")
    #         await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='save', description="save transcript of ticket")
    @app_commands.describe(topic="topic of ticket")
    @app_commands.describe(limit="range of transcript")
    async def save(self, interaction: Interaction, topic:str = 'No Topic Given', limit: app_commands.Range[int,0,1000]= 500):
        await interaction.response.defer(thinking=True)
        
        can_run = await checks.slash_check(self.bot, interaction, "transcript")
        if can_run != True:
            return await interaction.followup.send("You do not have permission to run this command")

        transcript = await chat_exporter.export(interaction.channel, limit=limit,tz_info="Asia/Kolkata")

        if transcript is None:
            await interaction.followup.send("An Error Occured, Try Again Later")
            return
        
        transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{interaction.channel.name}.html")

        transcript_log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["transcript_log_channel"])

        link_msg = await transcript_log_channel.send(content=f"{interaction.channel.name} | {topic}",file=transcript_file)

        link_button = discord.ui.View()
        url = f"https://codebeautify.org/htmlviewer?url={link_msg.attachments[0].url}"
        link_button.add_item(discord.ui.Button(label='View Transcript', url=url))

        await link_msg.edit(view=link_button)

        await interaction.followup.send(embed=discord.Embed(description=f"<:save:819194696874197004> | Transcript Saved", color=0x00FF00),view=link_button)

        log_embed = discord.Embed(color=0x00FF00)
        log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket", value=interaction.channel.name)
        log_embed.add_field(name="Action", value=f"Saved Transcript")
        await log_channel.send(embed=log_embed)
        ticket_info = await self.bot.ticket.find(interaction.channel.id)
        log_msg = await log_channel.fetch_message(ticket_info['log_message_id'])
        embed = log_msg.embeds[0]
        embed.add_field(name="Transcript", value=f"[Link](<{link_msg.attachments[0].url}>)")
        await log_msg.edit(embed=embed) 