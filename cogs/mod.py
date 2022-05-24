import datetime
import discord
import re
from discord import Webhook
import aiohttp
import asyncio
from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
from typing import Union
from utils.converter import TimeConverter
from utils.functions import make_db_temp
from utils.checks import Commands_Checks
import ui.models as models


class Mod(commands.Cog, name="Moderation",description = "Moderation commands"):
    def __init__(self, bot):
        self.bot = bot
        self.ban_task = self.check_current_bans.start()
        self.mute_task = self.check_current_mutes.start()
    
    def cog_unload(self):
        self.ban_task.cancel()
        self.mute_task.cancel()
    
    @tasks.loop(seconds=30)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.utcnow()
        Mutes = deepcopy(self.bot.current_mutes)
        for key, value in Mutes.items():
            #data = {'_id': member.id, 'guildId': interaction.guild.id, 'MutedBy': interaction.user.id, 'MutedBy': datetime.datetime.utcnow(), 'MutedDuration': time,'old_roles': []}
            if value['MutedDuration'] is None:
                continue

            unmuteTime = value['MutedAt'] + relativedelta(seconds=value['MutedDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])
                moderator = guild.get_member(value['MutedBy'])
                if not member:
                    value['MutedAt'] = datetime.datetime.utcnow()
                    await self.bot.mutes.update(value)
                    self.bot.current_mutes[key] = value
                    continue

                self.bot.dispatch('unmute', member, moderator, value)

                await self.bot.mutes.delete(value['_id'])
                try:
                    self.bot.current_mutes.pop(key)
                except KeyError:
                    pass
    
    @tasks.loop(seconds=60)
    async def check_current_bans(self):
        currentTime = datetime.datetime.utcnow()
        bans = deepcopy(self.bot.current_bans)
        for key, value in bans.items():
            if value['BanDuration'] is None:
                continue

            unbantime = value['BannedAt'] + relativedelta(seconds=value['BanDuration'])

            if currentTime >= unbantime:
                guild = self.bot.get_guild(int(value['guildId']))
                member = await self.bot.fetch_user(int(value['_id']))
                moderator = guild.get_member(value['BanedBy'])
                self.bot.dispatch('ban_expired', guild, member, moderator)

                try:
                    self.bot.current_bans.pop(member.id)
                except KeyError:
                    pass
    
    @check_current_bans.before_loop
    async def before_check_current_bans(self):
        await self.bot.wait_until_ready()
    
    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_ban_expired(self, guild: discord.Guild, user: discord.User, moderator: discord.Member):
        try:
            await guild.unban(user, reason="Automatic ban expired")
        except discord.NotFound:
            pass
        data = await self.bot.config.find(guild.id)
        embed = discord.Embed(title=f"🔨 UnBan | Case ID: {data['case']}",
                                    description=f" **Offender**: {user.name} | {user.mention} \n**Reason**: Automatic punishment expire\n **Moderator**: {moderator.name} {moderator.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {user.id}")
        data["case"] += 1
        await self.bot.config.upsert(data)

        log_channel = self.bot.get_channel(int(data['mod_log']))
        if log_channel:
            await log_channel.send(embed=embed)
        
        await self.bot.bans.delete(user.id)

    @commands.Cog.listener()
    async def on_unmute(self, member: discord.Member, moderator: discord.Member, data: dict):
        guild = self.bot.get_guild(data['guildId'])

        guild_data = await self.bot.config.find(guild.id)
        embed = discord.Embed(title=f"🔇 UnMute | Case ID: {guild_data['case']}",
                                    description=f" **Offender**: {member.name} | {member.mention} \n**Reason**:Automatic punishment expire\n **Moderator**: {moderator.name} {moderator.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        guild_data["case"] += 1
        await self.bot.config.increment(guild.id, 1, "case")

        log_channel = self.bot.get_channel(int(guild_data['mod_log']))
        if log_channel:
            await log_channel.send(embed=embed)    
        
        Muted_role = discord.utils.get(guild.roles, name="Muted")
        if Muted_role:
            await member.remove_roles(Muted_role)
        roles = []
        for i in data['old_roles']:
            role  = discord.utils.get(guild.roles, id=int(i))
            if role:
                roles.append(role)
        
        await member.add_roles(*roles)
    
        await self.bot.mutes.delete(member.id)
    

    @commands.hybrid_command(name="slowmode", aliases=["sm"], description="Set slowmode for a channel", usage="<time>")
    @app_commands.describe(time="Slowmod Time")
    @app_commands.guilds(785839283847954433)
    async def slowmode(self, ctx, time: TimeConverter=None):

        if time is None:
            await ctx.channel.edit(slowmode_delay=None)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed slowmode from {ctx.channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)
        elif time > 21600:
            await ctx.send("Slowmode can't be more than 6 hours",ephemeral=True)
        else:
            await ctx.channel.edit(slowmode_delay=time)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Set slowmode to {format_timespan(time)}s in {ctx.channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(member="User to ban")
    @app_commands.describe(reason="Reason for ban")
    @app_commands.describe(time="Duration of ban")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_me())
    async def ban(self, interaction: discord.Interaction, member: Union[discord.Member, discord.User], time: str=None, reason: str="No reason given"):
        await interaction.response.defer()
        time = await TimeConverter().convert(interaction, time)
        
        if member.id in [self.bot.owner_id, self.bot.user.id]:
            return await interaction.followup.sen("You can't ban me and my owner")
        
        if member.top_role >= interaction.user.top_role:
            return await interaction.followup.send("You can't ban someone with a higher/Equal role than you", ephemeral=True)
        
        if member.id == interaction.user.id:
            return await interaction.followup.send("You can't ban yourself", ephemeral=True)
        
        data = {'_id': member.id, 'guildId': interaction.guild.id, 'BanedBy': interaction.user.id, 'BannedAt': datetime.datetime.utcnow(), 'BanDuration': time, 'Reason': reason}
        guild_data = await self.bot.config.find(interaction.guild.id)
        if not guild_data:
            guild_data = make_db_temp(interaction.guild.id)
            
        embed = discord.Embed(title=f"🔨 Ban | Case ID: {guild_data['case']}",
                                    description=f" **Offender**: {member.name} | {member.mention}\n**Duration**: {format_timespan(time)} \n**Reason**: {reason}\n **Moderator**: {interaction.user.name} {interaction.user.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        guild_data["case"] += 1
        await self.bot.config.upsert(guild_data)

        try:
            await member.send(f"You have been banned from {interaction.guild.name} for {format_timespan(time)}s\nReason: {reason}")
        except discord.HTTPException:
            pass
        await interaction.guild.ban(member, reason=reason, delete_message_days=0)
        log_channel = interaction.guild.get_channel(guild_data['mod_log'])
        await log_channel.send(embed=embed)
        response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Banned {member.mention} has been banned for {format_timespan(time)}", color=0x32CD32)
        await interaction.followup.send(embed=response_embed)
        if time:
            await self.bot.bans.insert(data)
            self.bot.current_bans[member.id] = data
        else:
            pass
    
    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(member="User to unban")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_me())
    async def unban(self, interaction: discord.Interaction, member: discord.User, reason: str="No reason given"):
        await interaction.response.defer()

        try:
            await interaction.guild.unban(member, reason=reason)
        except discord.NotFound:
            return await interaction.followup.send("That user is not banned")

        data = await self.bot.config.find(interaction.guild.id)

        if not data:
            data = make_db_temp(interaction.guild.id)
        embed = discord.Embed(title=f"🔨 UnBan | Case ID: {data['case']}",
                                    description=f" **Offender**: {member.name} | {member.mention}\n**Reason**: {reason}\n **Moderator**: {interaction.user.name} {interaction.user.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        data["case"] += 1
        await self.bot.config.upsert(data)

        log_channel = interaction.guild.get_channel(data['mod_log'])
        await log_channel.send(embed=embed)
        response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Unbanned {member.mention} has been unbanned", color=0x32CD32)
        await interaction.followup.send(embed=response_embed)
        await self.bot.bans.delete(member.id)

        try:
            self.bot.current_bans.pop(member.id)
        except KeyError:
            pass
    
    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(member="User to kick")
    @app_commands.describe(reason="Reason for kick")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_me())
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason given"):
        await interaction.response.defer()
        if member.id in [self.bot.owner_id, self.bot.user.id]:
            return await interaction.followup.sen("You can't kick me and my owner")
        
        if member.top_role >= interaction.user.top_role:
            return await interaction.followup.send("You can't kick someone with a higher/Equal role than you", ephemeral=True)
        
        if member.id == interaction.user.id:
            return await interaction.followup.send("You can't kick yourself", ephemeral=True)
        
        guild_data = await self.bot.config.find(interaction.guild.id)
        if not guild_data:
            guild_data = make_db_temp(interaction.guild.id)

        await self.bot.config.increment(interaction.guild.id, 1, "case")

        try:
            await member.send(f"You have been kicked from {interaction.guild.name} for {reason}")
        except discord.HTTPException:
            pass
        await interaction.guild.kick(member, reason=reason)

        log_channel = interaction.guild.get_channel(guild_data['mod_log'])

        embed = discord.Embed(title=f"🔨 Kick | Case ID: {guild_data['case']}",
                            description=f" **Offender**: {member.name} | {member.mention}\n**Reason**: {reason}\n **Moderator**: {interaction.user.name} {interaction.user.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        await log_channel.send(embed=embed)
        response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Kicked {member.mention} has been kicked", color=0x32CD32)
        await interaction.followup.send(embed=response_embed)
    
    @app_commands.command(name="massban", description="Massban a users")
    @app_commands.guilds(785839283847954433)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(reason="Reason for ban")
    async def massban(self, interaction: discord.Interaction, reason: str="No reason given"):
        await interaction.response.send_modal(models.Mass_ban(self.bot, interaction, reason))

    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(member="User to mute")
    @app_commands.describe(time="Time to mute")
    @app_commands.describe(reason="Reason for mute")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_me())
    async def mute(self, interaction: discord.Interaction, member: discord.Member, time: str=None, reason: str="No reason given"):
        await interaction.response.defer(thinking=True)
        time = await TimeConverter().convert(interaction, time)
        if member.id in [self.bot.owner_id, self.bot.user.id]:
            return await interaction.followup.send("You can't mute me and my owner")
        
        if member.top_role >= interaction.user.top_role:
            return await interaction.followup.send("You can't mute someone with a higher/Equal role than you")
        
        if member.id == interaction.user.id:
            return await interaction.followup.send("You can't mute yourself")
        
        guild_data = await self.bot.config.find(interaction.guild.id)

        Muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if not Muted_role:
            Muted_role = await interaction.guild.create_role(name="Muted", reason="No Muted role Found in server")
            overrite = discord.PermissionOverwrite()
            overrite.send_messages = False
            overrite.add_reactions = False
            overrite.read_messages = False
            for channel in interaction.guild.channels:
                await channel.set_permissions(Muted_role, overwrite=overrite)
        
        if Muted_role in member.roles:
            return await interaction.followup.send("This user is already muted")
        
        data = {'_id': member.id, 'guildId': interaction.guild.id, 'MutedBy': interaction.user.id, 'MutedAt': datetime.datetime.utcnow(), 'MutedDuration': time,'old_roles': []}
        for role in member.roles:
            try:
                await member.remove_roles(role)
                data['old_roles'].append(role.id)
            except:
                continue
        
        await member.add_roles(Muted_role, reason="Muted")
        if time:
            await self.bot.mutes.insert(data)
            self.bot.current_mutes[member.id] = data
        
        log_channel = interaction.guild.get_channel(guild_data['mod_log'])
        
        embed = discord.Embed(title=f"🔇 Mute | Case ID: {guild_data['case']}",
            description=f" **Offender**: {member.name} | {member.mention}\n**Duration:** {format_timespan(time)}\n**Reason**: {reason}\n **Moderator**: {interaction.user.name} {interaction.user.mention}", color=0xE74C3C)

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {member.id}")
        await log_channel.send(embed=embed)
        response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Muted {member.mention} has been muted", color=0x32CD32)
        await interaction.followup.send(embed=response_embed)
        try:
            if time is not None:
                remove_time = round((discord.utils.utcnow() + datetime.timedelta(seconds=time)).timestamp())
            else:
                remove_time = "Infinite"
            await member.send(f"You have been muted from {interaction.guild.name} for {reason}\n Unmute in <t:{remove_time}:R>")
        except discord.HTTPException:
            pass
    
    @app_commands.command(name="role", description="add/remove a role to a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(member="User to add/remove a role", role="Role to add/remove")
    async def role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role.permissions.administrator or role.permissions.manage_guild or role.permissions.manage_roles or role.permissions.manage_channels or role.permissions.ban_members or role.permissions.kick_members:
            return await interaction.response.send_message("You can't add/remove this role due to security reasons, contact the owner if you think this is a mistake", ephemeral=True)
           
        await interaction.response.defer(thinking=True)
        if role in member.roles:
            await member.remove_roles(role)
            response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed {role.name} from {member.mention}", color=0x32CD32)
        else:
            await member.add_roles(role)
            response_embed = discord.Embed(description=f"<:allow:819194696874197004> | Added {role.name} to {member.mention}", color=0x32CD32)
        await interaction.followup.send(embed=response_embed)

    @app_commands.command(name="whois", description="Get info about a user")
    @app_commands.describe(member="User to get info about")
    @app_commands.guilds(785839283847954433)
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=f'{member.name}', color=member.color)

        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"{member.name} | {member.id}", icon_url=member.avatar.url)
        
        else:

            embed.set_thumbnail(url=member.default_avatar)
            embed.set_footer(text=f"{member.name} | {member.id}", icon_url=member.default_avatar)
        
        embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
        embed.add_field(name="Created At:", value=f"<t:{round(member.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name="Joined At:", value=f"<t:{round(member.joined_at.timestamp())}:R>", inline=False)
        Member = await self.bot.fetch_user(member.id)

        if Member.banner:
            embed.set_image(url=Member.banner)
        
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(30)
        await interaction.delete_original_message()

async def setup(bot):
    await bot.add_cog(Mod(bot))