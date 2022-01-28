import datetime
import datetime
import discord
import aiohttp
from discord.ext import commands
from nextcord import Webhook

class Anti_nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')

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
                            await session.close()
            
def setup(bot):
    bot.add_cog(Anti_nuke(bot))