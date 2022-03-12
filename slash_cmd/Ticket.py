from discord import app_commands, Interaction
from typing import Union, Optional, List
from discord.app_commands import Choice
import discord

import asyncio
from utils.checks import checks
import chat_exporter
import io

class Ticket_Commands(app_commands.Group):
    def __init__(self, bot, name="ticket"):
        super().__init__(name=name)
        self.bot = bot

    async def on_error(self, interaction: Interaction, command: app_commands.Command, error: app_commands.AppCommandError) -> None:
        
        error = f"Error happened while executing command: ```py\n{error}\n```"
        embed = discord.Embed(title="Error", description=f"Error Ac", color=0xFF0000)
        await interaction.followup.send(embed=embed)

    
    @app_commands.command(name="edit", description="Edit current ticket")
    @app_commands.describe(option="Select Edit Options")
    @app_commands.describe(target="Role/User")
    @app_commands.choices(option=[
        Choice(name="Add", value=1),
        Choice(name="Remove", value=2),
    ])
    
    async def edit(self, interaction: Interaction, option: Choice[int], target: Union[discord.Role, discord.Member]):
        print(option.value)
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
    
    @app_commands.command(name="status", description="close/open/delete")
    @app_commands.describe(option="Select Status Options")
    @app_commands.choices(option=[
        Choice(name="Close", value=1),
        Choice(name="Open", value=2),
        Choice(name="Secure", value=3),
    ])
    async def status(self, interaction: Interaction, option: Choice[int]):
        if option.value == 1:
            await interaction.response.defer(ephemeral=False, thinking=True)
            can_run = await checks.slash_check(self.bot, interaction, "close")

            if can_run != True:
                return await interaction.followup.send("You do not have permission to run this command")

            if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
                return await interaction.followup.send("This is not a ticket channel", ephemeral=True)
            
            data = await self.bot.ticket.find(interaction.channel.id)
            ticket_owner = self.bot.get_user(int(data['ticket_owner']))
            await interaction.channel.edit(sync_permissions=True)

            overrite = discord.PermissionOverwrite()
            overrite.view_channel = False

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

            log_embed = discord.Embed(color=0xFF0000)
            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Closed {interaction.channel.name}")
            await log_channel.send(embed=log_embed)
        
        if option.value == 2:
            await interaction.response.defer(thinking=True)
            can_run = await checks.slash_check(self.bot, interaction, "open")

            if can_run != True:
                return await interaction.followup.send("You do not have permission to run this command")

            if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
                await interaction.followup.send("This is not a ticket channel", ephemeral=True)
            
            data = await self.bot.ticket.find(interaction.channel.id)
            ticket_owner = interaction.guild.get_member(int(data['ticket_owner']))
            if ticket_owner == None:
                return await interaction.followup.send("Ticket owner is not in the server, you may delete the ticket", ephemeral=False)
                
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

            log_embed = discord.Embed(color=0x00FF00)
            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Opend {interaction.channel.name}")
            await log_channel.send(embed=log_embed)
        
        if option.value == 3:

            ticket_info = await self.bot.ticket.find(interaction.channel.id)
            await interaction.response.defer(thinking=True)

            if ticket_info is None:
                return await interaction.followup.send("Ticket Not Found")
            
            await interaction.channel.edit(sync_permissions=True)
            ticket_owner = interaction.guild.get_member(int(ticket_info['ticket_owner']))
            if not ticket_owner:
                return await interaction.followup.send("Ticket Owner Not Found")
            
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = False
            overwrite.read_messages = False
            overwrite.send_messages = False
            overwrite.attach_files = False

            for i in interaction.channel.overwrites:
                if type(i) == discord.Member and i.id == ticket_owner.id:
                    pass
                else:
                    await interaction.channel.set_permissions(i, overwrite=overwrite)
            

            await interaction.followup.send("Ticket is now Admin Only")



    @app_commands.command(name="delete", description="Delete a ticket")
    async def delete(self, interaction: Interaction):
        data = await self.bot.ticket.find(interaction.channel.id)
        
        can_run = await checks.slash_check(self.bot, interaction, "delete")
        if can_run != True:
            return await interaction.followup.send("You do not have permission to run this command")

        if interaction.channel.category.id != self.bot.config_data[interaction.guild.id]["ticket_category"]:
            return await interaction.response.send_message("This is not a ticket channel", ephemeral=True)

        msg = await interaction.response.send_message("Deleting this Ticekt in 10s `type fs` to cancel this command")
        try:
            stop_m = await self.bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() == "fs", timeout=10)
            await stop_m.add_reaction("✅")
            return await msg.edit(content="Ok cancelling the command")

        except asyncio.TimeoutError:
            
            user_in_channel = {}
            async for message in interaction.channel.history(limit=None):
                if message.author.id in user_in_channel.keys():
                    user_in_channel[message.author.id] += 1
                else:
                    user_in_channel[message.author.id] = 1

            print(user_in_channel)    
            print("\n-----------------")

            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_message = await log_channel.fetch_message(data['log_message_id'])
            embed = log_message.embeds[0]
            users, i = "", 1

            for key, value in user_in_channel.items():
                users += f"{i}. <@{key}> - {value}\n"
                i += 1

            embed.add_field(name="Users in Ticket", value=users)
            await log_message.edit(embed=embed)

            await self.bot.ticket.delete(interaction.channel.id)
            await interaction.channel.delete()

            log_embed = discord.Embed(color=0xFF0000)
            log_channel = self.bot.get_channel(self.bot.config_data[interaction.guild.id]["ticket_log_channel"])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Deleted {interaction.channel.name}")
            await log_channel.send(embed=log_embed)


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
        embed.color = 0x00FF00
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="config", description="Configure the ticket system")
    @app_commands.describe(category="category of ticket")
    @app_commands.describe(support_role="support role of system")
    @app_commands.describe(pm_role="partner manager role of system")
    @app_commands.describe(transcript="transcript channel of system")
    @app_commands.describe(ticket_log="ticket log channel of system")
    async def config(self, interaction: Interaction, category: discord.CategoryChannel=None, support_role: discord.Role=None, pm_role: discord.Role=None, transcript: discord.TextChannel=None, ticket_log: discord.TextChannel=None):        
        can_run = await checks.slash_check(self.bot, interaction, app_commands.command.__name__)
        if can_run != True:
            return await interaction.followup.send("You do not have permission to run this command")

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
        if ticket_log:
            data['ticket_log_channel'] = ticket_log.id

        if support_role or category or pm_role or transcript or ticket_log:
            await self.bot.config.upsert(data)
            await interaction.response.send_message("Configuration Updated")
        else:
            embed = discord.Embed(title="Ticket Config", color=0x2f3136)
            embed.add_field(name="Ticket Category", value=f"<#{data['ticket_category']}>")
            embed.add_field(name="Support Role", value=f"<@&{data['support_role']}>")
            embed.add_field(name="Partner Manager Role", value=f"<@&{data['pm_role']}>")
            embed.add_field(name="Transcript Log Channel", value=f"<#{data['transcript_log_channel']}>")
            embed.add_field(name="Ticket Log Channel", value=f"<#{data['ticket_log_channel']}>")
            embed.set_footer(text="Made by Jay and utki007")
            await interaction.response.send_message(embed=embed)
    
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