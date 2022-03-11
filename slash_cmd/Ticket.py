from discord import app_commands, Interaction
from typing import Union, Optional, List
import discord
import asyncio
from utils.checks import checks
import chat_exporter
import io

class Ticket_Commands(app_commands.Group):
    def __init__(self, bot, name="ticket"):
        super().__init__(name=name)
        self.bot = bot
    
    @app_commands.command(name="close", description="Close a ticket")
    async def close(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=False, thinking=True)

        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)

        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

        if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            return await interaction.followup.send("This is not a ticket channel", ephemeral=True)
        
        data = await self.bot.ticket.find(interaction.channel.id)
        ticket_owner = self.bot.get_user(int(data['ticket_owner']))
        await interaction.channel.edit(sync_permissions=True)

        overrite = discord.PermissionOverwrite()
        overrite.view_channel = False
        await interaction.channel.set_permissions(ticket_owner, overwrite=overrite)

        staff_overrite = discord.PermissionOverwrite()
        staff_overrite.view_channel = True
        staff_overrite.send_messages = True
        staff_overrite.read_messages = True
        staff_overrite.attach_files = True

        for i in data['added_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(i))
            await interaction.channel.set_permissions(role, overwrite=overrite)
        
        for i in data['added_users']:
            user = self.bot.get_user(int(i))
            await interaction.channel.set_permissions(user, overwrite=overrite)

        support_role = discord.utils.get(interaction.guild.roles, id=self.bot.config_data[interaction.guild.id]["support_role"])
        await interaction.channel.set_permissions(support_role, overwrite=staff_overrite)

        data['status'] = "closed"
        await self.bot.ticket.upsert(data)

        await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | Ticket closed by {interaction.user.mention}", color=0x2f3136))

    @app_commands.command(name="open", description="ReOpen a ticket")
    async def open(self, interaction: Interaction):

        await interaction.response.defer(thinking=True)
        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)

        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

        if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            await interaction.followup.send("This is not a ticket channel", ephemeral=True)
        
        data = await self.bot.ticket.find(interaction.channel.id)
        ticket_owner = self.bot.get_user(int(data['ticket_owner']))
        await interaction.channel.edit(sync_permissions=True)

        overrite = discord.PermissionOverwrite()
        overrite.view_channel = True
        overrite.send_messages = True
        overrite.read_messages = True
        overrite.attach_files = True

        await interaction.channel.set_permissions(ticket_owner, overwrite=overrite)

        for i in data['added_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(i))
            await interaction.channel.set_permissions(role, overwrite=overrite)
        
        for i in data['added_users']:
            user = self.bot.get_user(int(i))
            await interaction.channel.set_permissions(user, overwrite=overrite)

        data['status'] = "open"
        await self.bot.ticket.upsert(data)

        support_role = discord.utils.get(interaction.guild.roles, id=self.bot.config_data[interaction.guild.id]['support_role'])
        await interaction.channel.set_permissions(support_role, overwrite=overrite)
        await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | Ticket re-opened by {interaction.user.mention}", color=0x2f3136))
    
    @app_commands.command(name="delete", description="Delete a ticket")
    async def delete(self, interaction: Interaction):
        data = await self.bot.ticket.find_by_custom({'channel': interaction.channel.id, 'guild': interaction.guild.id})
        
        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

        if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            return await interaction.response.send_message("This is not a ticket channel", ephemeral=True)

        msg = await interaction.response.send_message("Deleting this Ticekt in 10s `type fs` to cancel this command")
        try:
            stop_m = await self.bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() == "fs", timeout=10)
            await stop_m.add_reaction("✅")
            return await msg.edit(content="Ok cancelling the command")
        except asyncio.TimeoutError:
            await self.bot.ticket.delete(interaction.channel.id)
            await interaction.channel.delete()
            

    @app_commands.command(name="add", description="Add a user or role to a ticket")
    @app_commands.describe(target='user/role')   
    async def add(self, interaction: Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.defer(thinking=True)

        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

        data = await self.bot.ticket.find(interaction.channel.id)
        if data is None and interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            return await interaction.followup.send("This is not a ticket channel", ephemeral=True)

        if type(target) == discord.Role:
            if target.id in data['added_roles']:
                await interaction.followup.send("This role is already added to the ticket")
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
                await interaction.response.send_message("This user is already added to the ticket")
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
    
    @app_commands.command(name="remove", description="Remove a user or role from a ticket")
    @app_commands.describe(target='user/role')
    async def remove(self, interaction: Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.defer(thinking=True)

        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

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

    @app_commands.command(name="stats", description="stats of tickets")
    async def stats(self, interaction: Interaction):
        data = await self.bot.ticket.find(interaction.channel.id)
        if data is None and interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            return await interaction.response.send_message("This is not a ticket channel", ephemeral=True)
        
        embed = discord.Embed(title="Ticket Stats", color=0x2f3136)
        embed.add_field(name="Ticket Owner", value=f"<@{data['ticket_owner']}>")
        embed.add_field(name="Ticket Status", value=f"{data['status']}")
        embed.add_field(name="Ticket Created", value=f"{data['created_at']}")
        embed.add_field(name="Ticket Type", value=f"{data['type']}")
        embed.add_field(name="Added Roles", value=f"{len(data['added_roles'])}")
        embed.add_field(name="Added Users", value=f"{len(data['added_users'])}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="config", description="Configure the ticket system")
    @app_commands.describe(category="category of ticket")
    @app_commands.describe(support_role="support role of system")
    @app_commands.describe(pm_role="partner manager role of system")
    @app_commands.describe(transcript="transcript channel of system")
    async def config(self, interaction: Interaction, category: discord.CategoryChannel=None, support_role: discord.Role=None, pm_role: discord.Role=None, transcript: discord.TextChannel=None):        
        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

        data = await self.bot.config.find(interaction.guild.id)
        if data is None:
            data = {'_id': interaction.guild.id, 'ticket_category': None, 'support_role': None}

        if category:
            data['ticket_category'] = category.id

        if support_role:
            data['support_role'] = support_role.id

        if pm_role:
            data['pm_role'] = pm_role.id

        if transcript:
            data['transcript_log_channel'] = transcript.id

        if support_role or category or pm_role or transcript:
            await self.bot.config.upsert(data)
            await interaction.response.send_message("Configuration Updated")
        else:
            embed = discord.Embed(title="Ticket Config", color=0x2f3136)
            embed.add_field(name="Ticket Category", value=f"<#{data['ticket_category']}>")
            embed.add_field(name="Support Role", value=f"<@&{data['support_role']}>")
            embed.add_field(name="Partner Manager Role", value=f"<@&{data['pm_role']}>")
            embed.add_field(name="Transcript Log Channel", value=f"<#{data['transcript_log_channel']}>")
            embed.set_footer(text="Made by Jay and utki007")
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='save', description="save transcript of ticket")
    @app_commands.describe(topic="topic of ticket")
    @app_commands.describe(limit="range of transcript")
    async def save(self, interaction: Interaction, topic:str = 'No Topic Given', limit: app_commands.Range[int,0,1000]= 500):
        await interaction.response.defer(thinking=True)
        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            await interaction.followup.send("You do not have permission to run this command")

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

        await interaction.followup.send(embed=discord.Embed(description=f"<:save:819194696874197004> | Transcript Saved", color=0x2f3136),view=link_button)