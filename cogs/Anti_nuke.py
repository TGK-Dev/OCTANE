import datetime
import discord
import aiohttp
import asyncio
from discord.ext import commands, tasks
from discord import Webhook, app_commands, Interaction
from utils.db import Document
from typing import Union
from utils.paginator import Paginator
from ui.confirm import Confirm
from ui import selects
from typing import Literal

class Anti_Nuke(commands.GroupCog, name="antinuke", description="Manage the antinuke system/config"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.antinuke = Document(self.bot.db, 'antinuke')
        self.system_enabled = None
    
    @staticmethod
    def make_config(guild_id):
        return {
                '_id': guild_id, 
                'log_channel': None,
                'owner_ids': [],
                'role': {
                    'create': {'users': [], 'roles': [], 'punishment': {'type': None}}, 
                    'delete': {'users': [], 'roles': [], 'punishment': {'type': None}},
                    'edit': {'users': [], 'roles': [], 'punishment': {'type': None}},
                    'lock': False
                },
                'channel': {
                    'create': {'users': [], 'roles': [], 'punishment': {'type': None}},
                    'delete': {'users': [], 'roles': [], 'punishment': {'type': None}},
                    'edit': {'users': [], 'roles': [], 'punishment': {'type': None}},
                },
                'lockdown': {'channels': [], 'active': False},
            }
    
    role_command = app_commands.Group(name="role", description="Manage the antinuke role settings")
    channel_command = app_commands.Group(name="channel", description="Manage the antinuke channel settings")
    lockdown_command = app_commands.Group(name="lockdown", description="Manage the antinuke lockdown settings")
    settings = app_commands.Group(name="settings", description="show the antinuke settings")

    async def is_me(interaction: discord.Interaction) -> bool:
        return interaction.user.id in [301657045248114690, 488614633670967307]


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Commands has been loaded')

    @lockdown_command.command(name="add", description="Add a channel to the lockdown list")
    @app_commands.check(is_me)
    async def lockdown_add(self, interaction: Interaction):
        config = await self.bot.antinuke.find(interaction.guild.id)
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        embed = discord.Embed(description="Select the channel you want to add to the lockdown list from the dropdown menu below", color=discord.Color.blurple())
        view = selects.Channel_Select(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        view.message = await interaction.original_response()
        await view.wait()
        if view.value is None:
            for child in view.children:
                child.disabled = True
            await view.message.edit(view=view)
            return
        if view.value:
            for channel in view.channels:
                if channel.id not in config['lockdown']['channels']:
                    config['lockdown']['channels'].append(channel.id)
            await self.bot.antinuke.update(config)
            embed = discord.Embed(description="Successfully added the selected channels to the lockdown list", color=discord.Color.blurple())
            embed.add_field(name="Added Channels", value="\n".join(channel.mention for channel in view.channels))
            for child in view.children:
                child.disabled = True
            await view.interaction.response.edit_message(embed=embed, view=view)

        self.bot.master_config = config
    
    @lockdown_command.command(name="remove", description="Remove a channel from the lockdown list")
    @app_commands.check(is_me)
    async def lockdown_remove(self, interaction: Interaction, channel: discord.TextChannel):
        config = await self.bot.antinuke.find(interaction.guild.id)
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        if channel.id in config['lockdown']['channels']:
            config['lockdown']['channels'].remove(channel.id)
            embed = discord.Embed(description=f"Successfully removed {channel.mention} from the lockdown list", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(description=f"{channel.mention} is not in the lockdown list", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.bot.master_config = config

    @lockdown_command.command(name="list", description="List all the channels in the lockdown list")
    @app_commands.check(is_me)
    async def lockdown_list(self, interaction: Interaction):
        config = await self.bot.antinuke.find(interaction.guild.id)
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        categories = {f'{categories.name}': [] for categories in interaction.guild.categories}
        categories['Uncategorized'] = []
        channels = [channel for channel in interaction.guild.channels if channel.id in config['lockdown']['channels']]
        for channel in channels:
            if channel.category:
                categories[f'{channel.category.name}'].append(channel)
            else:
                categories['Uncategorized'].append(channel)
        embeds = []
        for category, channels in categories.items():
            embed = discord.Embed(title=f"{category} Channels", color=discord.Color.blurple())
            if len(channels) == 0:
                embed.description = "No channels are added to this category for the lockdown list"
            else:
                embed.description = "\n".join(channel.mention for channel in channels)
            embeds.append(embed)

        await Paginator(interaction, pages=embeds).start(embeded=True, quick_navigation=False)
    
    @lockdown_command.command(name="start", description="Start the lockdown")
    @app_commands.check(is_me)
    async def lockdown_start(self, interaction: Interaction, reason: str = None):
        config = await self.bot.antinuke.find(interaction.guild.id)
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)

        if config['lockdown']['active'] == True:
            embed = discord.Embed(description="The lockdown is already active", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = Confirm(interaction.user, 30)
        embed = discord.Embed(description="Are you sure you want to start the lockdown? when you start the lockdown, all the channels in the lockdown list will be locked down", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        view.message = await interaction.original_response()
        await view.wait()

        if view.value:            
            start = datetime.datetime.now()
            await view.interaction.response.edit_message(embed=discord.Embed(description="<a:Do_not_disturb:1038074377306132531> | Starting the lockdown...", color=discord.Color.red()), view=None)

            overwrites = discord.PermissionOverwrite()
            overwrites.send_messages = False
            overwrites.add_reactions = False

            channels = [channel for channel in interaction.guild.channels if channel.id in config['lockdown']['channels']]
            embed = discord.Embed(title="Server Lockdown 🔒", description="This Channel has been locked down by the server staff\nMore Information can be found in announcements channels, Refrain from dm'ing staff, **__you are not muted.__**", color=discord.Color.red())

            for channel in channels:
                await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason=reason)
                await channel.send(embed=embed)
                await asyncio.sleep(0.5)

            config['lockdown']['active'] = True
            await self.bot.antinuke.update(config)
            await view.interaction.edit_original_response(embed=discord.Embed(description=f"<:octane_yes:1019957051721535618> | Successfully Initiated the lockdown in {round((datetime.datetime.now() - start).total_seconds())} Seconds", color=discord.Color.green()))
        else:
            for child in view.children:
                child.disabled = True
            await view.message.edit(view=view, content="Lockdown Cancelled")

        self.bot.master_config = config
        
    @lockdown_command.command(name="end", description="end the lockdown")
    @app_commands.check(is_me)
    async def lockdown_end(self, interaction: Interaction, reason: str = None):
        config = await self.bot.antinuke.find(interaction.guild.id)

        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)

        if config['lockdown']['active'] == False:
            return await interaction.response.send_message(embed=discord.Embed(description="The lockdown is not active", color=discord.Color.blurple()), ephemeral=True)

        view = Confirm(interaction.user, 30)
        embed = discord.Embed(description="Are you sure you want to end the lockdown? when you end the lockdown, all the channels in the lockdown list will be unlocked", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        view.message = await interaction.original_response()
        await view.wait()

        if view.value:
            start = datetime.datetime.now()
            await view.interaction.response.edit_message(embed=discord.Embed(description="<a:Do_not_disturb:1038074377306132531> | Ending the lockdown...", color=discord.Color.red()), view=None)

            overwrites = discord.PermissionOverwrite()
            overwrites.send_messages = None
            overwrites.add_reactions = None

            channels = [channel for channel in interaction.guild.channels if channel.id in config['lockdown']['channels']]

            for channel in channels:
                await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason=reason)
                await asyncio.sleep(0.5)

            config['lockdown']['active'] = False
            await self.bot.antinuke.update(config)

            await view.interaction.edit_original_response(embed=discord.Embed(description=f"<:octane_yes:1019957051721535618> | Successfully ended the Lockdown in {round((datetime.datetime.now() - start).total_seconds())} Seconds", color=discord.Color.green()))

        else:

            for child in view.children:
                child.disabled = True
            await view.message.edit(view=view, content="Lockdown Cancelled")
        
        self.bot.master_config = config

    @role_command.command(name="whitelist", description="Mange the antinuke role config")
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(is_me)
    @app_commands.choices(option=[app_commands.Choice(name="create", value="create"), app_commands.Choice(name="delete", value="delete"), app_commands.Choice(name="edit", value="edit")])
    async def role_create(self, interaction: Interaction, option: app_commands.Choice[str],traget: Union[discord.Member, discord.Role]):
        await interaction.response.pong()
        config = await self.bot.antinuke.find(interaction.guild.id)
        option = option.value
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        embed = discord.Embed(description="", color=discord.Color.green())
        if isinstance(traget, discord.Member):
            if traget.id in config['role'][option]['users']:
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the whitelist of role {option}"
            else:
                config['role'][option]['users'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the whitelist of role {option}"

        elif isinstance(traget, discord.Role):
            if traget.id in config['role'][option]['roles']:
                config['role'][option]['roles'].remove(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the whitelist of role {option}"
            else:
                config['role'][option]['roles'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the whitelist of role {option}"

        await interaction.response.send_message(embed=embed, ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config
    
    @role_command.command(name="punishment", description="Mange the panishment of the antinuke role config")
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(is_me)
    @app_commands.choices(
        option=[app_commands.Choice(name="create", value="create"), app_commands.Choice(name="delete", value="delete"), app_commands.Choice(name="edit", value="edit")],
        punishment=[app_commands.Choice(name="ban", value="ban"), app_commands.Choice(name="kick", value="kick"), app_commands.Choice(name="timeout", value="timeout"), app_commands.Choice(name="qurantine", value="qurantine")]
    )
    async def role_punishment(self, interaction: Interaction, option: app_commands.Choice[str],punishment: app_commands.Choice[str]):
        config = await self.bot.antinuke.find(interaction.guild.id)
        option = option.value
        punishment = punishment.value
        config['role'][option]['punishment']['type'] = punishment
        await interaction.response.send_message(embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Set the punishment of role {option} to {punishment}", color=discord.Color.green()), ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config
    
    @role_command.command(name="lock", description="Disable role updates on users profile")
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(is_me)
    async def role_lock(self, interaction: Interaction, togggle: bool):
        config = await self.bot.antinuke.find(interaction.guild.id)
        config['role']['lock'] = togggle
        await interaction.response.send_message(embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Set the role lock to {togggle}", color=discord.Color.green()), ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config

    @channel_command.command(name="whitelist", description="Mange the antinuke channel config")
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(is_me)
    @app_commands.choices(option=[app_commands.Choice(name="create", value="create"), app_commands.Choice(name="delete", value="delete"), app_commands.Choice(name="edit", value="edit")])
    async def channel_create(self, interaction: Interaction, option: app_commands.Choice[str],traget: Union[discord.Member, discord.Role]):
        config = await self.bot.antinuke.find(interaction.guild.id)
        option = option.value
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        embed = discord.Embed(description="", color=discord.Color.green())
        if isinstance(traget, discord.Member):
            if traget.id in config['channel'][option]['users']:
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the whitelist of channel {option}"
            else:
                config['channel'][option]['users'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the whitelist of channel {option}"

        elif isinstance(traget, discord.Role):
            if traget.id in config['channel'][option]['roles']:
                config['channel'][option]['roles'].remove(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the whitelist of channel {option}"
            else:
                config['channel'][option]['roles'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the whitelist of channel {option}"

        await interaction.response.send_message(embed=embed, ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config

    @channel_command.command(name="punishment", description="Mange the panishment of the antinuke channel config")
    @app_commands.check(is_me)
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(
        option=[app_commands.Choice(name="create", value="create"), app_commands.Choice(name="delete", value="delete"), app_commands.Choice(name="edit", value="edit")],
        punishment=[app_commands.Choice(name="ban", value="ban"), app_commands.Choice(name="kick", value="kick"), app_commands.Choice(name="timeout", value="timeout"), app_commands.Choice(name="qurantine", value="qurantine")]
    )
    async def channel_punishment(self, interaction: Interaction, option: app_commands.Choice[str],punishment: app_commands.Choice[str]):
        config = await self.bot.antinuke.find(interaction.guild.id)
        option = option.value
        punishment = punishment.value
        config['channel'][option]['punishment']['type'] = punishment
        await interaction.response.send_message(embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Set the punishment of channel {option} to {punishment}", color=discord.Color.green()), ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config
    
    @app_commands.command(name="owner", description="add/remove the owner from the antinuke config")
    @app_commands.check(is_me)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(traget="The user to add/remove from the owner list")
    async def anitnuke_owner(self, interaction: Interaction, traget: discord.Member):
        config = await self.bot.antinuke.find(interaction.guild.id)
        option = traget
        if config is None:
            config = self.make_config(interaction.guild.id)
            await self.bot.antinuke.insert(config)
        embed = discord.Embed(description="", color=discord.Color.green())
        if isinstance(traget, discord.Member):
            if traget.id in config['owner_ids']:
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the owner list"
            else:
                config['owner_ids'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the owner list"

        elif isinstance(traget, discord.Role):
            if traget.id in config['owner_ids']:
                config['owner_ids'].remove(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Removed {traget.mention} from the owner list"
            else:
                config['owner_ids'].append(traget.id)
                embed.description = f"<:dynosuccess:1000349098240647188> | Added {traget.mention} to the owner list"

        await interaction.response.send_message(embed=embed, ephemeral=False)
        await self.bot.antinuke.update(config)
        self.bot.master_config = config
    
    @settings.command(name="show", description="Show the antinuke config")
    @app_commands.check(is_me)
    @app_commands.default_permissions(administrator=True)
    async def show(self, interaction: Interaction, option: Literal['Roles', 'Channel', 'Lockdown', 'Owners']):
        guild_data = await self.bot.antinuke.find(interaction.guild.id)
        if guild_data is None:
            return await interaction.response.send_message(embed=discord.Embed(description="<:dynoerror:1000349098240647188> | No antinuke config found", color=discord.Color.red()), ephemeral=False)      
        if option == 'Roles':
            pages = []
            for key in guild_data['role']:
                embed = discord.Embed(title=f"Role {key.capitalize()} Settings", description="", color=discord.Color.green())
                #embed.add_field(name="Users", value="\n".join([f"<@{i}>" for i in guild_data['role'][key]['users']]) if len(guild_data['role'][key]['users']) > 0 else "None")
                embed.add_field(name="Roles", value="\n".join([f"<@&{i}>" for i in guild_data['role'][key]['roles']]) if len(guild_data['role'][key]['roles']) > 0 else "None")
                embed.add_field(name="Punishment", value=guild_data['role'][key]['punishment']['type'] if guild_data['role'][key]['punishment']['type'] != "None" else "None")
                pages.append(embed)

            await Paginator(pages=pages, interaction=interaction).start(quick_navigation=False,embeded=True)        
        elif option == 'Channel':
            pages = []
            for key in guild_data['channel']:
                embed = discord.Embed(title=f"Channel {key.capitalize()} Settings", description="", color=discord.Color.green())
                embed.add_field(name="Users", value="\n".join([f"<@{i}>" for i in guild_data['channel'][key]['users']]) if len(guild_data['channel'][key]['users']) > 0 else "None")
                embed.add_field(name="Roles", value="\n".join([f"<@&{i}>" for i in guild_data['channel'][key]['roles']]) if len(guild_data['channel'][key]['roles']) > 0 else "None")
                embed.add_field(name="Punishment", value=guild_data['channel'][key]['punishment']['type'] if guild_data['channel'][key]['punishment']['type'] != "None" else "None")
                pages.append(embed)
            
            await Paginator(pages=pages, interaction=interaction).start(quick_navigation=False,embeded=True)        
        elif option == 'Lockdown':
            embed = discord.Embed(title="Lockdown", description="", color=discord.Color.green())
            embed.description = f"Lockdown is {'enabled' if guild_data['lockdown']['enabled'] else 'disabled'}"
            embed.add_field(name="Channels", value="\n".join([f"<#{i}>" for i in guild_data['lockdown']['channels']]) if len(guild_data['lockdown']['channels']) > 0 else "None")

            await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(name="log-channel", description="Set the log channel for the antinuke")
    @app_commands.check(is_me)
    @app_commands.default_permissions(administrator=True)
    async def log_channel(self, interaction: Interaction, channel: discord.TextChannel):
        config = await self.bot.antinuke.find(interaction.guild.id)
        if config is None:
            return await interaction.response.send_message(embed=discord.Embed(description="<:dynoerror:1000349098240647188> | No antinuke config found", color=discord.Color.red()), ephemeral=False)      
        config['log_channel'] = channel.id
        await self.bot.antinuke.update(config)
        self.bot.master_config = config
        await interaction.response.send_message(embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Set the log channel to {channel.mention}", color=discord.Color.green()), ephemeral=False)
    
    @app_commands.command(name="set-quarantine", description="Set the quarantine role for the antinuke")
    @app_commands.check(is_me)
    @app_commands.default_permissions(administrator=True)
    async def set_quarantine(self, interaction: Interaction):
        start = datetime.datetime.now()
        await interaction.response.send_message(embed=discord.Embed(description="<a:Do_not_disturb:1038074377306132531> | Starting up the quarantine role setup", color=discord.Color.red()), ephemeral=False)
        qurentine_role = discord.utils.get(interaction.guild.roles, name="Quarantined")
        if qurentine_role: await qurentine_role.delete()
        qurentine_role = await interaction.guild.create_role(name="Quarantine", reason="Quarantine role for antinuke")
        await qurentine_role.edit(permissions=discord.Permissions.none())
        for channel in interaction.guild.channels:
            await channel.set_permissions(qurentine_role, send_messages=False, read_messages=False, read_message_history=False, view_channel=False)
            await asyncio.sleep(0.5)

        await interaction.edit_original_response(embed=discord.Embed(description=f"<:octane_yes:1019957051721535618> | Successfully created the quarantine role and completed configuration in {(datetime.datetime.now() - start).total_seconds()} Seconds", color=discord.Color.green()))

class Antinuke_Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.master_config = {}
        self.role_lock_system = None
        self.update_cache_event = self.update_cache.start()
    
    @tasks.loop(minutes=5)
    async def update_cache(self):
        self.bot.master_config = await self.bot.antinuke.find(785839283847954433)
    
    @update_cache.before_loop
    async def before_update_cache(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.bot.master_config = await self.bot.antinuke.find(785839283847954433)
        self.bot.qurantine = Document(self.bot.db, "qurantine")
        print(self.bot.master_config)
        #self.role_lock_system = self.bot.master_config['role']['lock']
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
    async def do_punishment(self, guild: discord.Guild, user: discord.Member, punishment: str, reason: str, log_channel: discord.TextChannel):
        now = datetime.datetime.now()
        if punishment == "ban":
            try:
                await user.send(f"You have been banned from {guild.name} for {reason}")
            except:
                pass
            await guild.ban(user, reason=reason)
            embed = discord.Embed(description=f"Offender: {user.mention} ({user.id})\nAction: Ban\nReason: {reason}, Moderator: Antinuke-System", color=discord.Color.red())
            await log_channel.send(embed=embed)
        elif punishment == "kick":
            try:
                await user.send(f"You have been kicked from {guild.name} for {reason}")
            except:
                pass
            await guild.kick(user, reason=reason)
            embed = discord.Embed(description=f"Offender: {user.mention} ({user.id})\nAction: Kick\nReason: {reason}, Moderator: Antinuke-System", color=discord.Color.red())
            await log_channel.send(embed=embed)
        elif punishment == "timeout":
            try:
                await user.send(f"You have been timed out from {guild.name} for {reason}")
            except:
                pass
            await user.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=5))
            embed = discord.Embed(description=f"Offender: {user.mention} ({user.id})\nAction: Timeout\nReason: {reason}, Moderator: Antinuke-System", color=discord.Color.red())
            await log_channel.send(embed=embed)
        elif punishment == "qurantine":
            try:
                await user.send(f"You have been quarantined from {guild.name} for {reason}")
            except:
                pass
            roles = [role for role in user.roles if role.managed]
            data = {"_id": user.id, "roles": [role.id for role in user.roles], "guild": guild.id, reason: reason}
            qurantine_role = discord.utils.get(guild.roles, name="Quarantined")
            if qurantine_role is None:
                qurantine_role = await guild.create_role(name="Quarantined", reason="Antinuke-System")
                await qurantine_role.edit(position=guild.me.top_role.position - 1, reason="Antinuke-System")
                for channel in guild.channels:
                    await channel.set_permissions(qurantine_role, send_messages=False, read_messages=False, view_channel=False)
                roles.append(qurantine_role)
                await user.edit(roles=roles, reason=reason)
            else:
                roles.append(qurantine_role)
                await user.edit(roles=roles, reason=reason)
            embed = discord.Embed(description=f"Offender: {user.mention} ({user.id})\nAction: Quarantine\nReason: {reason}\nModerator: Antinuke-System", color=discord.Color.red())
            await log_channel.send(embed=embed)
            await self.bot.qurantine.upsert(data)
        
        end = datetime.datetime.now()
        total_ms = (end - now).total_seconds() * 1000
        print(f"punishment for {user} with reason {reason} and punishment {punishment} took {total_ms}ms to complete")

    async def whitelist_check(self, guild: discord.Guild, user: discord.Member, action_type: str, option: str, data: dict):
        whitelist = False
        if user.id == self.bot.user.id or user.id == guild.owner.id or user.id in data[action_type][option]['users'] or user.id in data['owner_ids']:
            whitelist = True
        elif (set(role.id for role in user.roles) & set(data[action_type][option]['roles'])):
            whitelist = True
        return whitelist

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):

        if role.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(role.guild.id)
        guild: discord.Guild = role.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create) if log.target.id == role.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        whitelist = await self.whitelist_check(guild, user, "role", "create", config)        
        if whitelist == False:
            await self.do_punishment(guild, user, config['role']['create']['punishment']['type'], reason="Unauthorized role creation", log_channel=guild.get_channel(config['log_channel']))
            await role.delete(reason="Unauthorized role creation")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if role.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(role.guild.id)
        guild: discord.Guild = role.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete) if log.target.id == role.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        whitelist = await self.whitelist_check(guild, user, "role", "delete", config)

        if whitelist == False:
            await self.do_punishment(guild, user, config['role']['delete']['punishment']['type'], reason="Unauthorized role deletion", log_channel=guild.get_channel(config['log_channel']))
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if before.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(before.guild.id)
        guild: discord.Guild = before.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update) if log.target.id == before.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        whitelist = await self.whitelist_check(guild, user, "role", "edit", config)

        if whitelist == False:
            await self.do_punishment(guild, user, config['role']['edit']['punishment']['type'], reason="Unauthorized role update", log_channel=guild.get_channel(config['log_channel']))
            await after.edit(reason="Unauthorized role update", name=before.name, permissions=before.permissions, color=before.color, hoist=before.hoist, mentionable=before.mentionable, position=before.position)
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if channel.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(channel.guild.id)
        guild: discord.Guild = channel.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create) if log.target.id == channel.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        whitelist = await self.whitelist_check(guild, user, "channel", "create", config)

        if whitelist == False:
            await self.do_punishment(guild, user, config['channel']['create']['punishment']['type'], reason="Unauthorized channel creation", log_channel=guild.get_channel(config['log_channel']))
            await channel.delete(reason="Unauthorized channel creation")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if channel.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(channel.guild.id)
        guild: discord.Guild = channel.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete) if log.target.id == channel.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        whitelist = await self.whitelist_check(guild, user, "channel", "delete", config)

        if whitelist == False:
            await self.do_punishment(guild, user, config['channel']['delete']['punishment']['type'], reason="Unauthorized channel deletion", log_channel=guild.get_channel(config['log_channel']))
        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if before.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(before.guild.id)
        guild: discord.Guild = before.guild

        server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update) if log.target.id == before.id]
        if len(server_audit_log) == 0: return
        server_audit_log = server_audit_log[0]
        user: discord.Member = server_audit_log.user
        if user.id == self.bot.user.id: return
        whitelist = await self.whitelist_check(guild, user, "channel", "edit", config)

        if whitelist == False:
            await self.do_punishment(guild, user, config['channel']['edit']['punishment']['type'], reason="Unauthorized channel update", log_channel=guild.get_channel(config['log_channel']))
            await after.edit(reason="Unauthorized channel update", name=before.name, topic=before.topic, slowmode_delay=before.slowmode_delay, nsfw=before.nsfw, category=before.category, position=before.position)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.guild.id != self.bot.master_config['_id']: return
        config = await self.bot.antinuke.find(before.guild.id)
        guild: discord.Guild = before.guild

        if before.roles == after.roles: return
        new_roles = [role for role in after.roles if role not in before.roles]
        if len(new_roles) == 0: return
        for role in new_roles:
            #check if role has any moderation permissions
            if role.permissions.administrator == True or role.permissions.manage_guild == True or role.permissions.manage_roles == True or role.permissions.manage_channels == True or role.permissions.ban_members == True or role.permissions.kick_members == True or role.permissions.manage_messages == True or role.permissions.manage_nicknames == True or role.permissions.manage_emojis == True or role.permissions.manage_webhooks == True or role.permissions.manage_emojis == True or role.permissions.manage_webhooks == True or role.permissions.manage_emojis == True or role.permissions.manage_webhooks == True:
                server_audit_log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update) if log.target.id == before.id]
                if len(server_audit_log) == 0: return
                server_audit_log = server_audit_log[0]
                user: discord.Member = server_audit_log.user

                if user.id == self.bot.user.id or user.id in config['owner_ids'] or user.id == guild.owner_id: 
                    return print("whitelisted")
                else:
                    await self.do_punishment(guild, user, "qurantine", reason="Unauthorized role staff addition", log_channel=guild.get_channel(config['log_channel']))
                    await self.do_punishment(guild, before, "qurantine", reason="Unauthorized role staff addition", log_channel=guild.get_channel(config['log_channel']))

async def setup(bot):
    await bot.add_cog(Anti_Nuke(bot), guilds=[discord.Object(785839283847954433)])
    await bot.add_cog(Antinuke_Events(bot), guilds=[discord.Object(785839283847954433)])