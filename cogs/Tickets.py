from discord import app_commands
from discord.ext import commands
from discord import Interaction
from typing import Union, List
from utils.paginator import Paginator
from ui.Ticket_system import Ticket_Control, Panel_edit, MyModal
import discord
import os
from ui.Ticket_system import Ticket_Control_Panel

class Ticket_slash(commands.GroupCog, name="ticket", description="ticket system commands"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="configure ticket system")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(channel="channel to use for ticket system", catogory="category to use for ticket system", logging="logging channel for ticket system", transcripts="channel to use for transcripts logs")
    async def config(self, interaction: discord.Interaction, channel: discord.TextChannel=None, catogory: discord.CategoryChannel=None, logging: discord.TextChannel=None, transcripts: discord.TextChannel=None):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            data = {
                '_id': interaction.guild.id,
                'channel': channel.id,
                'catogory': catogory.id if catogory else None,
                'logging': logging.id if logging else None,
                'panels': {},
                'last_plane_messaeg': None
            }
            await self.bot.ticket_system.insert(data)
        embed = discord.Embed(title="Ticket System Config", description="", color=discord.Color.random())

        if channel:
            data['channel'] = channel.id
            embed.add_field(name="Channel", value=channel.mention, inline=False)
        if catogory:
            data['catogory'] = catogory.id
            embed.add_field(name="Category", value=catogory.mention if catogory else "None", inline=False)
        if logging:
            data['logging'] = logging.id
            embed.add_field(name="Logging Channel", value=logging.mention if logging else "None", inline=False)
        if transcripts:
            data['transcripts'] = transcripts.id
            embed.add_field(name="Transcripts Channel", value=transcripts.mention if transcripts else "None", inline=False)

        await self.bot.ticket_system.update(data)        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="add", description="add someone to Ticket")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(target="target to add to ticket")
    async def add(self, interaction: discord.Interaction, target: Union[discord.Role, discord.Member]):
        data = await self.bot.tickets.find(interaction.channel.id)
        if not data:
            await interaction.response.send_message("Ticket not found",ephemeral=True)
            return
        embed = discord.Embed(description=f"<a:loading:998834454292344842> | Adding {target.mention}", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)
        if isinstance(target, discord.Role):
            if target.id in data['add_roles']:
                embed.description = "<:dynoError:1000351802702692442> | This role is already in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed)
                return
            else:
                data['add_roles'].append(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {target.mention} to the Ticket"
                embed.color = discord.Color.green()
                await interaction.channel.set_permissions(target, read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
                await interaction.edit_original_response(embed=embed)

        if isinstance(target, discord.Member):
            if target.id in data['add_users']:
                embed.description = "<:dynoError:1000351802702692442> | This member is already in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed)
                return
            else:
                data['add_users'].append(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {target.mention} to the Ticket"
                embed.color = discord.Color.green()
                await interaction.channel.set_permissions(target, read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
                await interaction.edit_original_response(embed=embed)

        await interaction.client.tickets.update(data)
        ticket_config = await self.bot.ticket_system.find(interaction.guild.id)
        if not ticket_config:
            return
        log_channel = interaction.client.get_channel(ticket_config['logging'])
        logging_embed = discord.Embed(title="Ticket System Log", description=f"{interaction.user.mention} added {target.mention} to the {interaction.channel.mention}", color=discord.Color.blurple())
        await log_channel.send(embed=logging_embed)

    @app_commands.command(name="remove", description="remove someone from Ticket")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(target="target to remove from ticket")
    async def remove(self, interaction: discord.Interaction, target: Union[discord.Role, discord.Member]):
        data = await self.bot.tickets.find(interaction.channel.id)
        if not data:
            await interaction.response.send_message("Ticket not found",ephemeral=True)
            return
        embed = discord.Embed(description=f"<a:loading:998834454292344842> | Removing {target.mention}", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)
        if isinstance(target, discord.Role):
            if target.id not in data['add_roles']:
                embed.description = "<:dynoError:1000351802702692442> | This role is not in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed)
                return
            else:
                data['add_roles'].remove(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {target.mention} from the Ticket"
                embed.color = discord.Color.green()
                await interaction.channel.set_permissions(target, read_messages=False)
                await interaction.edit_original_response(embed=embed)
                
        if isinstance(target, discord.Member):
            if target.id not in data['add_users']:
                embed.description = "<:dynoError:1000351802702692442> | This member is not in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed)
                return
            else:
                data['add_users'].remove(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {target.mention} from the Ticket"
                embed.color = discord.Color.green()
                await interaction.channel.set_permissions(target, read_messages=False)
                await interaction.edit_original_response(embed=embed)

        await interaction.client.tickets.update(data)
        ticket_config = await self.bot.ticket_system.find(interaction.guild.id)
        if not ticket_config:
            return
        log_channel = interaction.client.get_channel(ticket_config['logging'])
        logging_embed = discord.Embed(title="Ticket System Log", description=f"{interaction.user.mention} removed {target.mention} from the {interaction.channel.mention}", color=discord.Color.blurple())
        await log_channel.send(embed=logging_embed)    


class Panel(commands.GroupCog, name="panel", description="Manage Ticket system palnel"):
    def __init__(self, bot):
        self.bot = bot
    
    async def panel_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_panel = await self.bot.ticket_system.find(interaction.guild.id)
        if not current_panel:
            return []
        
        choice = [
            app_commands.Choice(name=name, value=name)
            for name in current_panel['panels'].keys() if current.lower() in name.lower()
        ]
        return choice
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_Control_Panel(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        self.bot.dispatch("load_panels")
    
    @commands.Cog.listener()
    async def on_load_panels(self):
        data = await self.bot.ticket_system.get_all()
        for i in data:
            view = Ticket_Control(i['panels'])
            self.bot.add_view(view)

    @app_commands.command(name="send", description="send all panel to support channel")
    @app_commands.default_permissions(administrator=True)
    async def panel_send(self, interaction: discord.Interaction):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            await interaction.response.send_message("Ticket System is not configured")
            return
        if data['channel'] is None:
            await interaction.response.send_message("Ticket System is not configured use /ticket config")
            return
        if len(data['panels']) == 0:
            await interaction.response.send_message("Please add panels using /ticket panel-create and /ticket panel-edit")
            return

        if data['last_plane_messaeg'] is None:
            await interaction.response.send_message("Sending all panels to support channel")
            embed = discord.Embed(title="Ticket System Panel", color=0x9e3bff)
            for key, value in data['panels'].items():
                embed.add_field(name=key, value=value['description'], inline=False)
        
            view = Ticket_Control(data['panels'])
            channel = interaction.guild.get_channel(data['channel'])
            msg = await channel.send(embed=embed, view=view)
            data['last_plane_messaeg'] = msg.id
            await self.bot.ticket_system.update(data)
            await interaction.edit_original_response(content="Successfully sent all panels to support channel")

        elif data['last_plane_messaeg']:

            await interaction.response.send_message("Found Existing Panel Message starting editing")
            channel = interaction.guild.get_channel(data['channel'])
            message = await channel.fetch_message(data['last_plane_messaeg'])
            if message:
                embed = message.embeds[0]
                embed.clear_fields()
                for key, value in data['panels'].items():
                    embed.add_field(name=key, value=value['description'], inline=False)
                view = Ticket_Control(data['panels'])
                await message.edit(embed=embed, view=view)
                await interaction.edit_original_response(content="Successfully Edited all panels to support channel")
    
    @app_commands.command(name="create", description="create a ticket panel")
    @app_commands.default_permissions(administrator=True)
    async def panel_create(self, interaction: discord.Interaction, name: str):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            data = {"_id": interaction.guild.id, "panels": {}, 'channel': None, 'catogory': None, 'logging': None, 'transcripts': None, 'last_plane_messaeg': None}
        panel_data = {"key": name, "support_role": [], "ping_role": None, 'creator': interaction.user.id, 'description': None, 'emoji': None, 'color': None, 'modal': {'type': 'long', 'question': 'state your reason for opening the ticket'}}
        data['panels'][name] = panel_data

        await self.bot.ticket_system.upsert(data)
        await interaction.response.send_message(f"Panel `{name}` is successfully created")
    
    @app_commands.command(name="delete", description="delete a ticket panel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(name=panel_auto)
    async def panel_delete(self, interaction: discord.Interaction, name: str):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            await interaction.response.send_message("No ticket system found")
            return
        if name not in data['panels'].keys():
            await interaction.response.send_message("Panel not found")
            return
        del data['panels'][name]
        await self.bot.ticket_system.upsert(data)
        await interaction.response.send_message(f"Panel `{name}` is successfully deleted")
    
    @app_commands.command(name="edit", description="edit a ticket panel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(name=panel_auto)
    @app_commands.describe(name="panel name")
    async def panel_edit(self, interaction: discord.Interaction, name:str):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            await interaction.response.send_message("No ticket system found")
            return
        if name not in data['panels'].keys():
            await interaction.response.send_message("Panel not found")
            return
        try:
            panel = data['panels'][name]
        except KeyError:
            await interaction.response.send_message("Panel not found")
            return

        embed = discord.Embed(title=f"{name} Settings", color=discord.Color.blurple())
        Support_roles = ""
        if len(panel['support_role']) > 0:
            for role in panel['support_role']:
                role = interaction.guild.get_role(int(role))
                if role:
                    Support_roles += f"{role.name} | {role.id}\n"
        else:
            Support_roles = "None"

        Ping_role = ""
        if panel['ping_role']:
            role = interaction.guild.get_role(int(panel['ping_role']))
            if role:
                Ping_role = f"{role.name} | {role.id}"
        else:
            Ping_role = "None"
        embed.add_field(name="Role Settings", value=f"> **Support Roles:**\n```\n{Support_roles}\n```\n> **Ping Role:**\n```\n{Ping_role}\n```", inline=False)
        embed.add_field(name="Info Settings", value=f"> **Description**\n```\n{panel['description']}\n```", inline=False)
        Modal_Settings = ""
        if panel['modal']:
            Modal_Settings += f"Question: {panel['modal']['question']}\nAnswer Type: {panel['modal']['type']}"
        else:
            Modal_Settings = "None"
        embed.add_field(name="Modal Settings", value=f"```\n{Modal_Settings}\n```", inline=False)
        Other = ""
        if panel['emoji']:
            Other += f"Emoji: {panel['emoji']}\n"
        if panel['color']:
            Other += f"Color: {panel['color']}"
        if Other:
            embed.add_field(name="Other Settings", value=f"```\n{Other}\n```", inline=False)
        else:
            embed.add_field(name="Other Settings", value="```\nNone\n```", inline=False)
        
        view = Panel_edit(interaction, data, name)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_message()

    @app_commands.command(name="list", description="list all ticket panels")
    @app_commands.default_permissions(administrator=True)
    async def panel_list(self, interaction: discord.Interaction):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        pages = []
        for panel in data['panels'].keys():
            embed = discord.Embed(title=panel, color=0x00ff00)
            embed.add_field(name="Support Roles", value=", ".join([interaction.guild.get_role(int(role)).mention for role in data['panels'][panel]['support_role']]) if len(data['panels'][panel]['support_role']) > 0 else "None", inline=False)
            embed.add_field(name="Ping Role", value=interaction.guild.get_role(int(data['panels'][panel]['ping_role'])).mention if data['panels'][panel]['ping_role'] else "None", inline=False)
            embed.add_field(name="Description", value=data['panels'][panel]['description'] if data['panels'][panel]['description'] else "None", inline=False)
            embed.add_field(name="Emoji", value=data['panels'][panel]['emoji'] if data['panels'][panel]['emoji'] else "None", inline=False)
            embed.add_field(name="Button Color", value=data['panels'][panel]['color'] if data['panels'][panel]['color'] else "None", inline=False)
            embed.set_footer(text=f"Created by {interaction.guild.get_member(data['panels'][panel]['creator']).display_name}", icon_url=interaction.guild.get_member(data['panels'][panel]['creator']).avatar.url if interaction.guild.get_member(data['panels'][panel]['creator']).avatar else interaction.guild.get_member(data['panels'][panel]['creator']).default_avatar.url)
            pages.append(embed)

        await Paginator(interaction, pages).start(quick_navigation=False, embeded=True)

    async def on_error(self, interaction: Interaction, error):
        try:
            await interaction.response.send_message(f"Error: {error}")
        except discord.InteractionResponded:
            await interaction.followup.send(f"Error: {error}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ticket_slash(bot), guilds=[discord.Object(785839283847954433), discord.Object(988761284956799038)])
    await bot.add_cog(Panel(bot), guilds=[discord.Object(785839283847954433), discord.Object(988761284956799038)])