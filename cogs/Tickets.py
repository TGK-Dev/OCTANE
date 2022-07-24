from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from discord import Interaction
from typing import Union, List, Literal
from utils.checks import Commands_Checks
from utils.functions import make_db_temp
from utils.paginator import Paginator
from ui.models import Ticket_Panel_edit, Ticket_Panel_edit_Other, Ticket_Panel_Roles
from ui.Ticket_system import Ticket_Control
import discord
import os
import logging
from traceback import format_exception
from ui.Ticket_system import Ticket_Control_Panel

class Ticket_slash(app_commands.Group, name="ticket", description="ticket system commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='ticket')     

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
                await interaction.edit_original_message(embed=embed)
                return
            else:
                data['add_roles'].append(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {target.mention} to the Ticket"
                embed.color = discord.Color.green()
                await interaction.edit_original_message(embed=embed)
        if isinstance(target, discord.Member):
            if target.id in data['add_members']:
                embed.description = "<:dynoError:1000351802702692442> | This member is already in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_message(embed=embed)
                return
            else:
                data['add_members'].append(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {target.mention} to the Ticket"
                embed.color = discord.Color.green()
                await interaction.edit_original_message(embed=embed)
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
                await interaction.edit_original_message(embed=embed)
                return
            else:
                data['add_roles'].remove(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {target.mention} from the Ticket"
                embed.color = discord.Color.green()
                await interaction.edit_original_message(embed=embed)
        if isinstance(target, discord.Member):
            if target.id not in data['add_members']:
                embed.description = "<:dynoError:1000351802702692442> | This member is not in the Ticket"
                embed.color = discord.Color.red()
                await interaction.edit_original_message(embed=embed)
                return
            else:
                data['add_members'].remove(target.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {target.mention} from the Ticket"
                embed.color = discord.Color.green()
                await interaction.edit_original_message(embed=embed)

        await interaction.client.tickets.update(data)
        ticket_config = await self.bot.ticket_system.find(interaction.guild.id)
        if not ticket_config:
            return
        log_channel = interaction.client.get_channel(ticket_config['logging'])
        logging_embed = discord.Embed(title="Ticket System Log", description=f"{interaction.user.mention} removed {target.mention} from the {interaction.channel.mention}", color=discord.Color.blurple())
        await log_channel.send(embed=logging_embed)    


class Panel(app_commands.Group):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='panel')
    
    async def panel_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_panel = await self.bot.ticket_system.find(interaction.guild.id)
        if not current_panel:
            return []
        
        choice = [
            app_commands.Choice(name=name, value=name)
            for name in current_panel['panels'].keys() if current.lower() in name.lower()
        ]
        return choice

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
            embed = discord.Embed(title="Ticket System Panel", color=discord.Color.random())
            for key, value in data['panels'].items():
                embed.add_field(name=key, value=value['description'], inline=False)
        
            view = Ticket_Control(data['panels'])
            channel = interaction.guild.get_channel(data['channel'])
            msg = await channel.send(embed=embed, view=view)
            data['last_plane_messaeg'] = msg.id
            await self.bot.ticket_system.update(data)
            await interaction.edit_original_message(content="Successfully sent all panels to support channel")

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
                await interaction.edit_original_message(content="Successfully Edited all panels to support channel")
    
    @app_commands.command(name="create", description="create a ticket panel")
    @app_commands.default_permissions(administrator=True)
    async def panel_create(self, interaction: discord.Interaction, name: str):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            data = {"_id": interaction.guild.id, "panels": {}, 'channel': None, 'catogory': None, 'logging': None, 'transcripts': None, 'last_plane_messaeg': None}
        panel_data = {"key": name, "support_role": [], "ping_role": None, 'creator': interaction.user.id, 'description': None, 'emoji': None, 'color': None}
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
    @app_commands.describe(name="panel name", option="option to edit")
    async def panel_edit(self, interaction: discord.Interaction, name:str ,option: Literal['Panel Roles', 'Description', 'Other']):
        data = await self.bot.ticket_system.find(interaction.guild.id)
        if not data:
            await interaction.response.send_message("No ticket system found")
            return
        if option == 'Panel Roles':
            modal = Ticket_Panel_Roles(interaction, name, data)
            modal.add_item(discord.ui.TextInput(label="Support Roles", default=",".join(data['panels'][name]['support_role']), placeholder="Ids of roles spearated by comma", style=discord.TextStyle.paragraph))
            modal.add_item(discord.ui.TextInput(label="Ping Role", default=data['panels'][name]['ping_role'], placeholder="Id of role", max_length=18))
            await interaction.response.send_modal(modal)
        
        if option == 'Description':
            modal = Ticket_Panel_edit(interaction, name, data)
            modal.add_item(discord.ui.TextInput(label="Description", default=data['panels'][name]['description'] if data['panels'][name]['description'] else None, custom_id="description", style=discord.TextStyle.paragraph, max_length=200))
            return await interaction.response.send_modal(modal)

        if option == 'Other':
            modal = Ticket_Panel_edit_Other(interaction, name, data)
            modal.add_item(discord.ui.TextInput(label="Emoji", default=data['panels'][name]['emoji'] if data['panels'][name]['emoji'] else None, custom_id="emoji", style=discord.TextStyle.short, max_length=50, required=False))
            modal.add_item(discord.ui.TextInput(label="Color", default=data['panels'][name]['color'] if data['panels'][name]['color'] else None, custom_id="color", style=discord.TextStyle.short, required=False))
            return await interaction.response.send_modal(modal)

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


class Ticket(commands.Cog, name="Ticket System", description="Create Ticket Without Any Worry"):
    def __init__(self, bot,):
        self.bot = bot
    
    async def cog_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_cogs = []
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                current_cogs.append(file[:-3])
        new_options = [app_commands.Choice(name="reload all cogs", value="*")]
        for cog in current_cogs:
            new_options.append(app_commands.Choice(name=cog, value=cog))
        return new_options[:24]

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_Control_Panel(self.bot))
        self.bot.tree.add_command(Ticket_slash(self.bot), guild=discord.Object(785839283847954433)) #main server
        self.bot.tree.add_command(Panel(self.bot), guild=discord.Object(785839283847954433)) #main server
        self.bot.tree.add_command(Ticket_slash(self.bot), guild=discord.Object(988761284956799038)) #appeal server
        self.bot.tree.add_command(Panel(self.bot), guild=discord.Object(988761284956799038)) #appeal server
        #await self.bot.tree.sync(guild=discord.Object(999551299286732871))

        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        self.bot.dispatch("load_panels")
    
    @commands.Cog.listener()
    async def on_load_panels(self):
        data = await self.bot.ticket_system.get_all()
        for i in data:
            view = Ticket_Control(i['panels'])
            self.bot.add_view(view)

    @commands.command()
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        #await ctx.send(embed=embed, view=Ticket_main(self.bot))

    @commands.command()
    async def reload(self, ctx, name:str):
        try:
            await self.bot.reload_extension(f"cogs.{name}")
            await ctx.send(f"{name} has been reloaded")
        except Exception as e:
            await ctx.send(f"{name} has failed to reload\n`{e}`")

async def setup(bot):
    await bot.add_cog(Ticket(bot))