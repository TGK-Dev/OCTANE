import datetime
import discord
import aiohttp
from discord.ext import commands
from discord import Webhook
from utils.Anti_Nuke import Anti_Nuke
from utils.db import Document
from typing import Union
class Anti_nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.quarantine = Document(self.bot.db, "Quarantine")
        self.bypass_role = []
        for i in [786281307063189565, 785842380565774368,803635405638991902]:
            guild = self.bot.get_guild(785839283847954433)
            role = guild.get_role(i)
            self.bypass_role.append(role)
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild: discord.Guild = channel.guild
        if guild.id != 785839283847954433: return
        
        server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.channel_delete)]
        for log in server_audit_logs:
            if log.target.id == channel.id:
                user = log.user
                user_role = [role for role in user.roles]

                if any(role in self.bypass_role for role in user_role) or user.id == self.bot.user.id:
                    return
                else:
                    self.bot.dispatch("Quarantine", channel, log, 'UnAuthorized Channel Delete')    
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild: discord.Guild = channel.guild
        if guild.id != 785839283847954433: return
        server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.channel_create)]
        for log in server_audit_logs:
            if log.target.id == channel.id:
                
                user = log.user
                user_roles = [role for role in user.roles]
                if any(role in self.bypass_role for role in user_roles) or user.id == self.bot.user.id:
                    return
                else:
                    self.bot.dispatch('Quarantine', channel, log, 'UnAuthorized Channel Creation')
                
        permisson = discord.PermissionOverwrite(send_messages=False, read_messages=False, view_channel=False)
        await channel.set_permissions(guild.default_role, overwrite=permisson)
    

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        print(f"{role} created")
        if role.is_bot_managed == True or role.managed == True: return
        guild: discord.Guild = role.guild
        if guild.id != 785839283847954433: return
        server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.role_create)]
        for log in server_audit_logs:
            print("log", log.target.id == role.id)
            if log.target.id == role.id:
                user = log.user
                user_roles = [role for role in user.roles]

                if any(role in self.bypass_role for role in user_roles) or user.id == self.bot.user.id:
                    return
                else:
                    self.bot.dispatch("Quarantine", role, log, "UnAuthorized Role Creation")
                    break

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        print(f"{role} deleted")
        if role.is_bot_managed == True or role.managed == True: return
        guild: discord.Guild = role.guild
        if guild.id != 785839283847954433: return
        server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.role_delete)]
        for log in server_audit_logs:
            print("log", log.target.id, role.id)
            if log.target.id == role.id:
                user = log.user
                user_role = [role for role in user.roles]

                if any(role in self.bypass_role for role in user_role):
                    return
                else:
                    self.bot.dispatch("Quarantine", role, log, "UnAuthorized Role Deletion")
                    break
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        event_start = datetime.datetime.now()
        if before.guild.id != 785839283847954433: return
        if before.is_bot_managed == True or before.managed == True: return
        if before.permissions == after.permissions: return
        guild: discord.Guild = before.guild

        permmissions_diffrence = list(set(after.permissions).difference(set(before.permissions)))
        for permmission in permmissions_diffrence:
            if permmission[0] in ['kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'manage_messages', 'manage_roles', 'manage_permissions'] and permmission[1] == True:
                role = discord.utils.get(guild.roles, id=before.id)
                
                
                server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.role_update)]
                for log in server_audit_logs:

                    if log.target.id == role.id:
                        print(f"{log.user} updated {role}")
                        user = log.user
                        user_role = [role for role in user.roles]

                        if any(role in self.bypass_role for role in user_role):
                            return
                        else:
                            await role.edit(permissions=before.permissions, reason=f"UnAuthorized Role Update")
                            self.bot.dispatch("Quarantine", role, log, "UnAuthorized Role Update")
                            event_end = datetime.datetime.now()
                            event_duration = event_end - event_start
                            #print event duration in ms
                            print(f"Possible UnAuthorized Role Update, took {event_duration.total_seconds()} seconds revert changes")
                            return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != 785839283847954433: return
        if before.is_bot_managed == True or before.managed == True: return
        if before.roles == after.roles: return
        guild: discord.Guild = before.guild

        diffrent_role = list(set(after.roles).difference(set(before.roles)))
        for permmission in diffrent_role:
            if any(permmission.administrator, permmission.manage_channels, permmission.manage_guild, permmission.manage_messages, permmission.manage_roles, permmission.manage_permissions):
                role = discord.utils.get(guild.roles, id=before.id)
                server_audit_logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.member_update)]
                for log in server_audit_logs:
                    if log.target.id == before.id:
                        user = log.user
                        user_role = [role for role in user.roles]

                        if any(role in self.bypass_role for role in user_role):
                            return
                        else:
                            self.bot.dispatch("Quarantine", user,log, "UnAuthorized distribution of mod roles")
                            self.bot.dispatch("Quarantine", log.target, log, "UnAuthorized gain of mod roles")

    @commands.Cog.listener()
    async def on_Quarantine(self, traget: Union[discord.Role, discord.TextChannel, discord.Member], log: discord.AuditLogEntry, reason: str):
        user: discord.Member = log.user
        guild: discord.Guild = traget.guild
        data = {'_id': user.id, 'channel_id': None, 'Role_id': None,'guild_id': guild.id, 'timestamp': datetime.datetime.utcnow(), 'reason': reason, 'roles': []}

        if isinstance(traget, discord.Role):
            data['Role_id'] = traget.id
        elif isinstance(traget, discord.TextChannel):
            data['channel_id'] = traget.id

        for role in user.roles:
            try:
                if role == guild.default_role or role.managed:
                    continue
                await user.remove_roles(role)
                data['roles'].append(role.id)
            except Exception as e:
                pass
        role = discord.utils.get(guild.roles, name="Quarantine")
        if not role:
            role = await guild.create_role(name="Quarantine")
            for channel in guild.text_channels:
                await channel.set_permissions(role, send_messages=False, read_messages=False, view_channel=False)
        
        await user.add_roles(role)
        await self.bot.quarantine.insert(data)
        owner, owner2 = guild.owner, guild.get_member(488614633670967307)
        await owner.send(f"{user} has been quarantined for {reason}")
        await owner2.send(f"{user} has been quarantined for {reason}")

        await user.send(f"You have been quarantined")
        channel = self.bot.get_channel(792246185238069249)
        embed = discord.Embed(title="Quarantine", description=f"", color=0x00ff00)
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Target", value=f"{traget.mention} ({traget.id})", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        await channel.send(content="@everyone",embed=embed)


async def setup(bot):
    await bot.add_cog(Anti_nuke(bot))
