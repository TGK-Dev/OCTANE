import datetime
import discord
import aiohttp
from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
from utils.functions import make_db_temp
from utils.checks import Dynamic_cooldown
from utils.transformers import TimeConverter
from bson.objectid import ObjectId
from ui.confirm import Confirm
from utils.paginator import Paginator
import ui.member_view

class Mod(commands.Cog, name="Moderation",description = "Moderation commands"):
    def __init__(self, bot):
        self.bot = bot
        self.ban_task = self.check_current_bans.start()
        self.mute_task = self.check_current_mutes.start()
        self.ban_session = aiohttp.ClientSession()
    
    def cog_unload(self):
        self.ban_task.cancel()
        self.mute_task.cancel()
        self.ban_session.close()
    
    async def send_modlog(self, target: discord.Member, moderator: discord.Member, reason: str, action: str, duration: str = None, color: discord.Color = discord.Color.red()):
        data = await self.bot.config.find(moderator.guild.id)
        if not data: 
            data = make_db_temp(moderator.guild.id)
            await self.bot.config.upsert(data)
            return
        embed = discord.Embed(title=f"Case #{data['case']} | {action}", color=discord.Color.red(), description="")
        embed.description += f"**Offender:** {target.mention} ({target.id})\n"
        embed.description += f"**Moderator:** {moderator.mention} ({moderator.id})\n"
        embed.description += f"**Reason:** {reason}\n"
        if duration:
            embed.description += f"**Duration:** {format_timespan(duration) if duration != 'Permanent' else duration}\n"
        embed.set_footer(text=f"User ID: {target.id}")
        data['case'] += 1
        await self.bot.config.upsert(data)
        log_channel = moderator.guild.get_channel(data['mod_log'])
        if log_channel:
            await log_channel.send(embed=embed)
    
    warnings = app_commands.Group(name="warnings", description="Manage warnings")

    @tasks.loop(seconds=30)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        Mutes = deepcopy(self.bot.current_mutes)
        for key, value in Mutes.items():
            if datetime.datetime.now() >= value['UnMuteAt']:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])
                if not member: return
                moderator = guild.get_member(value['MutedBy'])
                self.bot.dispatch("unmute", member, moderator, value)
                try:
                    self.bot.current_mutes.pop(key)
                except KeyError:
                    pass
            else:
                print(f"someone is still muted for {round((value['UnMuteAt'] - currentTime).total_seconds())}")
    
    @tasks.loop(seconds=20)
    async def check_current_bans(self):
        currentTime = datetime.datetime.now()
        bans = deepcopy(self.bot.current_bans)
        for key, value in bans.items():
            if datetime.datetime.now() >= value['UnbanAt']:
                guild = self.bot.get_guild(value['guildId'])
                member = await self.bot.fetch_user(value['_id'])
                moderator = guild.get_member(value['BannedBy'])
                self.bot.dispatch("unban", guild, member, moderator, value)
                try:
                    self.bot.current_bans.pop(key)
                except KeyError:
                    pass
            else:
                print(f"someone is still banned for {round((value['UnBanAt'] - currentTime).total_seconds())}")
    
    @check_current_bans.before_loop
    async def before_check_current_bans(self):
        await self.bot.wait_until_ready()
    
    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_ready(self):
        for bans in await self.bot.bans.get_all(): self.bot.current_bans[bans['_id']] = bans
        for mutes in await self.bot.mutes.get_all(): self.bot.current_mutes[mutes['_id']] = mutes

        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_unban(self, guild: discord.Guild, user: discord.User, moderator: discord.Member, data: dict):
        try:
            await guild.unban(user, reason="Automatic ban expired")
        except discord.NotFound:
            pass   
        await self.send_modlog(user, guild.me, f"Automatic ban expired made by {moderator.mention} ,<t:{round(data['UnbanAt'].timestamp())}:R>", "Unban", color=discord.Color.green())

        await self.bot.bans.delete(user.id)

    @commands.Cog.listener()
    async def on_unmute(self, member: discord.Member, moderator: discord.Member, data: dict):
        guild: discord.Guild = member.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role:
            await member.remove_roles(muted_role, reason="Automatic unmute")
        roles = [guild.get_role(role) for role in data['old_roles']]
        await member.edit(roles=roles, reason="Automatic unmute")

        await self.send_modlog(member, guild.me, f"Automatic mute expired made by {moderator.mention} ,<t:{round(data['UnMuteAt'].timestamp())}:R>", "Unmute", color=discord.Color.green())
        await self.bot.mutes.delete(member.id)

    @commands.hybrid_command(name="slowmode", aliases=["sm"], description="Set slowmode for a channel", usage="<time>")
    @app_commands.describe(time="Slowmod Time")
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
    @app_commands.describe(reason="Reason for ban", time="Duration of ban", member="User to ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str , time: app_commands.Transform[str, TimeConverter]=None):
        if member == interaction.user or member == interaction.guild.owner:
            return await interaction.response.send_message("You can't ban this user", ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message("I can't ban this user", ephemeral=True)
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't ban this user due to role hierarchy", ephemeral=True)
        
        data = {'_id': member.id, 'guildId': interaction.guild.id, 'BannedBy': interaction.user.id, 'UnbanAt': datetime.datetime.now() + relativedelta(seconds=time) if time else None, 'duration': time if time else None, 'reason': reason}

        try:
            await member.send(embed=discord.Embed(description=f"You have been banned from {interaction.guild.name} for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136))
        except discord.HTTPException:
            pass
            
        await interaction.guild.ban(member, reason=reason)
        await interaction.response.send_message(f"Banned {member.mention}", ephemeral=True)
        await self.bot.bans.insert(data)
        self.bot.current_bans[member.id] = data
        await interaction.followup.send(embed=discord.Embed(description=f"{member.mention} has been banned for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136), ephemeral=False)
        await self.send_modlog(member, interaction.user, reason, "Ban", time if time else "Permanent", color=discord.Color.red())

    
    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(member="User to unban", reason="Reason for unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member: discord.User, reason: str):
        try:
            await interaction.guild.unban(member, reason=reason)
        except discord.NotFound:
            return await interaction.response.send_message("This user is not banned", ephemeral=True)
        await interaction.response.send_message(f"Unbanned {member.mention}", ephemeral=True)
        embed = discord.Embed(description=f"{member.mention} has been unbanned\n**Reason**: {reason}", color=0x2f3136)
        await interaction.followup.send(embed=embed, ephemeral=False)
        await self.send_modlog(member, interaction.user, reason, "Unban", color=discord.Color.green())
        await self.bot.bans.delete(member.id)
        try:
            del self.bot.current_bans[member.id]
        except KeyError:
            pass
    
    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.describe(member="User to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True, ban_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if member == interaction.user or member == interaction.guild.owner:
            return await interaction.response.send_message("You can't kick this user", ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message("I can't kick this user", ephemeral=True)
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't kick this user due to role hierarchy", ephemeral=True)
        try:
            await member.send(embed=discord.Embed(description=f"You have been kicked from {interaction.guild.name}\n**Reason**: {reason}", color=discord.Color.red()))
        except discord.HTTPException:
            pass
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention}", ephemeral=True)
        embed = discord.Embed(description=f"{member.mention} has been kicked\n**Reason**: {reason}", color=0x2f3136)
        await interaction.followup.send(embed=embed, ephemeral=False)
        await self.send_modlog(member, interaction.user, reason, "Kick", color=discord.Color.red())

    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(time="Time to mute", reason="Reason for mute",member="User to mute")
    async def mute(self, interaction: discord.Interaction, member: discord.Member,reason: str,  time: app_commands.Transform[str, TimeConverter]=None):
        if member == interaction.user or member == interaction.guild.owner:
            return await interaction.response.send_message("You can't mute this user", ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message("I can't mute this user", ephemeral=True)
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("You can't mute this user due to role hierarchy", ephemeral=True)
        if member.id in self.bot.current_mutes:
            return await interaction.response.send_message("This user is already muted", ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted", reason="Mute command")
            await mute_role.edit(position=interaction.guild.me.top_role.position - 1, reason="Mute command")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
        
        roles = []
        old_roles = []
        for r in member.roles:
            if r == interaction.guild.default_role or r.managed or r.position >= interaction.guild.me.top_role.position: 
                roles.append(r)
            else:
                old_roles.append(r.id)
        
        roles.append(mute_role)
        await member.edit(roles=roles, reason=reason)
        data = { '_id': member.id,'guildId': interaction.guild.id,'MutedBy': interaction.user.id, 'UnMuteAt': datetime.datetime.now() + datetime.timedelta(seconds=time) if time else None, 'old_roles': old_roles, 'duration': time if time else None}
        await self.bot.mutes.insert(data)
        self.bot.current_mutes[member.id] = data
        await interaction.followup.send(embed=discord.Embed(description=f"{member.mention} has been muted for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136), ephemeral=False)
        await interaction.channel.send(embed=discord.Embed(description=f"{member.mention} has been muted **Reason**: {reason}", color=0x2f3136))

        await self.send_modlog(member, interaction.user, reason, "Mute", time if time else "Permanent", color=discord.Color.red())
        try:
            await member.send(embed=discord.Embed(description=f"You have been muted in {interaction.guild.name} for {format_timespan(time)}\n**Reason**: {reason}", color=0x2f3136))
        except discord.HTTPException:
            pass
    
    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(member="User to unmute", reason="Reason for unmute")
    @app_commands.checks.has_permissions(administrator=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason given"):
        if member.id not in self.bot.current_mutes:
            return await interaction.response.send_message("This user is not muted", ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if not mute_role:
            return await interaction.response.send_message("This user is not muted", ephemeral=True)

        roles = []
        await member.remove_roles(mute_role, reason=reason)

        for r in self.bot.current_mutes[member.id]['old_roles']:
            roles.append(interaction.guild.get_role(r))            
        await member.edit(roles=roles, reason=reason)

        await interaction.followup.send(embed=discord.Embed(description=f"{member.mention} has been unmuted\n**Reason**: {reason}", color=0x2f3136), ephemeral=False)
        await interaction.channel.send(embed=discord.Embed(description=f"{member.mention} has been unmuted **Reason**: {reason}", color=0x2f3136), ephemeral=False)

        await self.send_modlog(member, interaction.user, reason, "Unmute", color=discord.Color.green())

        await self.bot.mutes.delete({'_id': member.id})
        try:
            del self.bot.current_mutes[member.id]
        except KeyError:
            pass
    
    @warnings.command(name="add", description="Add a warning to a user")
    @app_commands.describe(member="User to warn", reason="Reason for warn")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason given"):
        if member.id in [488614633670967307, 301657045248114690 , self.bot.user.id] or member.bot:
            return await interaction.response.send_message("You can't warn this user", ephemeral=True)
        
        warn_data = {"user":member.id, "reason":reason, "mod":interaction.user.id, 'time': datetime.datetime.now(), "guild":interaction.guild.id}
        await self.bot.warns.insert(warn_data)
        embed = discord.Embed(description=f"{member.mention} has been warned\n**Reason**: {reason}", color=0x2f3136)
        await interaction.channel.send(embed=embed, ephemeral=False)
        await interaction.response.send_message("User has been warned Successfully", ephemeral=True)

        await self.send_modlog(member, interaction.user, reason, "Warn", color=discord.Color.orange())
        try:
            await member.send(f"You have been warned in {interaction.guild.name} for {reason}")
        except discord.HTTPException:
            pass

    @warnings.command(name="remove", description="Remove a warning from a user")
    @app_commands.describe(member="User to remove warn from", warn_id="ID of warning to remove")
    @app_commands.checks.has_permissions(kick_members=True)
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, warn_id: str):
        warn_id = ObjectId(warn_id)
        warn = await self.bot.warns.find(['_id', warn_id])
        if not warn: return await interaction.response.send_message("This warning doesn't exist", ephemeral=True)
        if warn['user'] != member.id: return await interaction.response.send_message("This warning doesn't belong to this user", ephemeral=True)
        embed = discord.Embed(description=f"Are you sure you want to remove {member.mention}'s warning with ID `{warn_id}` and reason `{warn['reason']}`?", color=0x2f3136)
        view = Confirm(interaction.user, 60)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_message()
        await view.wait()
        if view.value:
            await self.bot.warns.delete({'_id': warn_id})
            embed = discord.Embed(description=f"Warning with ID `{warn_id}` and reason `{warn['reason']}` from {member.mention} has been removed", color=0x2f3136)
            await view.interaction.response.edit_message(embed=embed, view=None)
            await self.send_modlog(member, interaction.user, f"Removed warning with ID `{warn_id}` and reason `{warn['reason']}`", "Unwarn", color=discord.Color.green())
        else:
            await view.interaction.response.edit_message(embed=discord.Embed(description="Command cancelled", color=0x2f3136), view=None)
    
    @warnings.command(name="list", description="List a user's warnings")
    @app_commands.describe(member="User to list warns from")
    @app_commands.checks.has_permissions(kick_members=True)
    async def listwarns(self, interaction: discord.Interaction, member: discord.Member):
        data = await self.bot.warns.find_many_by_custom({'user': member.id, 'guild': interaction.guild.id})
        if not data: await interaction.response.send_message("This user has no warnings", ephemeral=True)
        pages, = []
        for warn in data:
            embed = discord.Embed(description=f"ID: `{warn['_id']}`\nReason: `{warn['reason']}`\nModerator: <@{warn['mod']}>\nIssued: `{warn['time'].strftime('%d/%m/%Y %H:%M:%S')}`", color=0x2f3136)
            embed.set_footer(text="Showing {}/{} wanrings".format(data.index(warn)+1, len(data)))
            pages.append(embed)
        
        await Paginator(interaction, pages, 60).start(embeded=True, quick_navigation=False)
    
    @warnings.command(name="clear", description="Clear a user's warnings")
    @app_commands.describe(member="User to clear warns from")
    @app_commands.checks.has_permissions(kick_members=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        data = await self.bot.warns.find_many_by_custom({'user': member.id, 'guild': interaction.guild.id})
        if not data: await interaction.response.send_message("This user has no warnings", ephemeral=True)

        embed = discord.Embed(description=f"Are you sure you want to clear {member.mention}'s {len(data)} warnings?", color=0x2f3136)
        view = Confirm(interaction.user, 60)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_message()
        await view.wait()

        if view.value:
            await interaction.response.defer()
            for warn in data: await self.bot.warns.delete(warn['_id'])
            await interaction.followup.edit_message(embed=discord.Embed(description=f"{member.mention}'s {len(data)} warnings have been cleared", color=0x2f3136), view=None)
            await self.send_modlog(member, interaction.user, f"Cleared {len(data)} warnings", "Clearwarns", color=discord.Color.green())
        else:
            await view.interaction.response.edit_message(embed=discord.Embed(description="Command cancelled", color=0x2f3136), view=None)

    @app_commands.command(name="role", description="add/remove a role to a user")
    @app_commands.describe(member="User to add/remove a role", role="Role to add/remove")
    async def role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role.permissions.administrator or role.permissions.manage_guild or role.permissions.manage_roles or role.permissions.manage_channels or role.permissions.ban_members or role.permissions.kick_members or role.position >= interaction.guild.me.top_role.position or role.position >= interaction.user.top_role.position:
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
    @app_commands.checks.dynamic_cooldown(Dynamic_cooldown.low_dc)
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member=None):
        member = member if member else interaction.user

        embed = discord.Embed(title=f"User Info - {member.name}#{member.discriminator}")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        embed.add_field(name="<:authorized:991735095587254364> ID:", value=member.id)
        embed.add_field(name="<:displayname:991733326857654312> Display Name:", value=member.display_name)

        embed.add_field(name="<:bot:991733628935610388> Bot Account:", value=member.bot)

        embed.add_field(name="<:settings:991733871118917683> Account creation:", value=member.created_at.strftime('%d/%m/%Y %H:%M:%S'))
        embed.add_field(name="<:join:991733999477203054> Server join:", value=member.joined_at.strftime('%d/%m/%Y %H:%M:%S'))

        if not member.bot:
            view = ui.member_view.Member_view(self.bot, member, interaction)
            await interaction.response.send_message(embed=embed,view=view)
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(embed=embed)
    
    @userinfo.error
    async def afk_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(description=f"Error | {error}",color=discord.Color.red())
        await interaction.response.send_message(embed=embed,ephemeral=True)
    
    @app_commands.command(name="quarantine", description="Quarantine a user")
    @app_commands.describe(member="User to quarantine", reason="Reason for quarantine")
    @app_commands.checks.has_permissions(ban_members=True)
    async def quarantine(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        data = await self.bot.qurantine.find(member.id)
        if data: return await interaction.response.send_message("This user is already quarantined", ephemeral=True)

        quran = discord.utils.get(interaction.guild.roles, name="Quarantine")
        if not quran: return await interaction.response.send_message("The role `Quarantine` doesn't exist ping owner fast", ephemeral=True)
        await interaction.response.send_message("Quarantining user...", ephemeral=True)
        data = {"_id": member.id, "roles": [role.id for role in member.roles], "guild": interaction.guild.id, 'reason': reason}

        roles = [role for role in member.roles if role.managed]
        roles.append(quran)
        await member.edit(roles=roles)
        await self.bot.qurantine.insert(data)
        try:
            await member.send(f"You have been quarantined in {interaction.guild.name} for {reason}")
        except:
            pass
        embed = discord.Embed(description=f"{member.mention} has been warned\n**Reason**: {reason}", color=0x2f3136)
        await interaction.channel.send(embed=embed)
        await interaction.edit_original_response(embed=embed, content=None)
        await self.send_modlog(target=member, reason=reason, action="Unquarantine", moderator=interaction.user)

    @app_commands.command(name="unquarantine", description="Unquarantine a user")
    @app_commands.describe(member="User to unquarantine")
    @app_commands.checks.has_permissions(administrator=True)
    async def unquarantine(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        data = await self.bot.qurantine.find(member.id)
        if not data: return await interaction.response.send_message("This user isn't quarantined", ephemeral=True)

        quran = discord.utils.get(interaction.guild.roles, name="Quarantine")
        if not quran: return await interaction.response.send_message("The role `Quarantine` doesn't exist ping owner fast", ephemeral=True)
        await interaction.response.send_message("Unquarantining user...", ephemeral=True)
        roles = [interaction.guild.get_role(role) for role in data['roles']]
        await member.edit(roles=roles)
        await self.bot.qurantine.delete(member.id)
        try:
            await member.send(f"You have been unquarantined in {interaction.guild.name}")
        except:
            pass
        embed = discord.Embed(description=f"{member.mention} has been unquarantined", color=0x2f3136)
        await interaction.channel.send(embed=embed)
        await interaction.edit_original_response(embed=embed, content=None)
        await self.send_modlog(target=member, reason=reason, action="Unquarantine", moderator=interaction.user)

        
async def setup(bot):
    await bot.add_cog(Mod(bot), guilds=[discord.Object(785839283847954433)])

#data = {'_id': member.id, 'guildId': interaction.guild.id, 'BannedBy': interaction.user.id, 'BannedAt': datetime.datetime.now(), 'BanDuration': time, 'Reason': reason}