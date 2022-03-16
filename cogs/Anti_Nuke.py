import datetime
import discord
import aiohttp
from discord.ext import commands
from discord import Webhook

class Anti_nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        if before.guild.id != 785839283847954433:
            return
        if before.roles == after.roles:
            return
        
        new_role = set(after.roles) - set(before.roles)
        if not new_role:
            return

        guild = after.guild
        for role in new_role:
            perms = [perm[0] for perm in role.permissions if perm[1] == True]
            if (set(perms) & set(['kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'manage_messages', 'manage_roles', 'manage_permissions'])):

                logs = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update) if log.target.id == after.id]
                if logs:

                    if logs[0].user.id in [301657045248114690, 488614633670967307, 651711446081601545,457839031909351425,413651113485533194]:
                        return
                    else:
                        await after.remove_roles(role)
                        await after.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=10),reason="Possible Server Nuke attempt")
                        for role in logs[0].user.roles:
                            if role.permissions.administrator or role.permissions.manage_roles or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_channels or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_permissions:
                                await logs[0].user.remove_roles(role, reason="Possible Server Nuke attempt")
                        
                        await logs[0].user.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=10), reason="Possible Server Nuke attempt")

                        embed = discord.Embed(title="Possible Server Nuke attempt", description=f"{logs[0].user.mention} Has tryed to Give Moderator role to {after.mention}, Role is remove from {after.mention} and both user has put in Timeout", color=0xFF0000)
                        embed.timestamp = discord.utils.utcnow()
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(self.bot.nuke_webhook, session=session)
                            await webhook.send(embed=embed, username=f"{self.bot.user.name} Anti-Nuke", avatar_url=self.bot.user.avatar.url, content="@everyone")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.guild.id != 785839283847954433:
            return
        if before.permissions != after.permissions:
            diff = list(set(after.permissions).difference(set(before.permissions)))
            for changed_perm in diff:
                if changed_perm[0] in ['kick_members', 'ban_members', 'administrator', 'manage_channels', 'manage_guild', 'manage_messages', 'manage_roles', 'manage_permissions'] and changed_perm[1] == True:
                    guild = before.guild
                    role = discord.utils.get(guild.roles, id=before.id)
                    logs = await guild.audit_logs(limit=10, action=discord.AuditLogAction.role_update).flatten()
                    logs = [log async for log in guild.audit_logs(limit=10, action=discord.AuditLogAction.role_update)]
                    for log in logs:
                        if log.target.id == before.id and log.user.id != self.bot.user.id:
                            log = log
                            break

                    if log.user.id in [guild.owner.id, 488614633670967307, 301657045248114690]:
                        return 
                    await role.edit(permissions=before.permissions)
                                       
                    if log.target.id == before.id:

                        for role in log.user.roles:
                            if role.permissions.administrator or role.permissions.manage_roles or role.permissions.kick_members or role.permissions.ban_members or role.permissions.manage_channels or role.permissions.manage_guild or role.permissions.manage_messages or role.permissions.manage_roles or role.permissions.manage_permissions:
                                await log.user.remove_roles(role, reason="Possible Server Nuke attempt")

                        timeout = datetime.datetime.utcnow() + datetime.timedelta(hours=25)
                        await log.user.edit(timeout=timeout, reason="Possible Server Nuke attempt")

                        embed = discord.Embed(title="Alert", description=f"{log.user.mention} Has Tried to edit/create role with Admin/Mod power role perm has been reverted and user all mod role are removed and put in timeout")
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(self.bot.nuke_webhook, session=session)
                            await webhook.send(content="@everyone",username=f"{self.bot.user.name} NuKe", avatar_url=self.bot.user.avatar.url,embed=embed)

            
def setup(bot):
    bot.add_cog(Anti_nuke(bot))