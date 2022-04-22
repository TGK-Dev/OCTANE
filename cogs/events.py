from discord.ext import commands, tasks
import datetime
import discord

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_task = self.check_update_task.start()
    
    @tasks.loop(seconds=900)
    async def check_update_task(self):

        current_vote = await self.bot.votes.get_all()
        for votes in current_vote:
            self.bot.current_votes[votes['_id']] = votes
        
        current_ban = await self.bot.bans.get_all()
        for bans in current_ban:
            self.bot.current_bans[bans['_id']] = bans
        
        current_afk = await self.bot.afk.get_all()
        for afk in current_afk:
            self.bot.current_afk[afk['_id']] = afk
        
        current_mute = await self.bot.mutes.get_all()
        for mute in current_mute:
            self.bot.current_mutes[mute['_id']] = mute
        
        current_perm = await self.bot.perms.get_all()
        for perm in current_perm:
            self.bot.perm[perm['_id']] = perm
    
    @check_update_task.before_loop
    async def before_check_current_free(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"This command is on cooldown for {error.retry_after:.2f} seconds")
        
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Missing required argument {error.param.name}")
        
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f"Bad argument {error.param.name}")
        
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"You don't have permission to use this command")
        
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"I don't have permission to use this command")
        
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send(f"You don't have permission to use this command")
        
        elif isinstance(error, commands.CommandInvokeError):
            return await ctx.send(f"An error occured while executing this command")

        else:
            embed = discord.Embed(color=0xE74C3C,description=f"<:dnd:840490624670892063> | Error: `{error}`")
            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_data = self.bot.config_cache.get(member.guild.id)
        guild = member.guild
        if not guild_data: return
        
        roles = []
        for role in guild_data['join_roles']:
            role = discord.utils.get(member.guild.roles, id=role)
            if role:
                roles.append(role)
        await member.add_roles(roles, reason="Join Roles")

        embed = discord.Embed(title=f'**WELCOME TO TGK, {member.display_name}!**',
                        description=f"\n\nGet your favorite roles from [self-roles](https://discord.gg/58bc5QWE4q),\nand say _Hello_ to everyone in [chat](https://discord.gg/yEPYYDZ3dD)!\n\nAlso check out other fun game bots on the server:\n✦ [Casino](https://discord.gg/DJycdCqnqt) ✦ [Mudae](https://discord.gg/ujCHVRctHY) ✦ [Akinator](https://discord.gg/fzDTdGZFh6) ✦ [Pokemon](https://discord.gg/DpJ4mAUC9m)\n\nMake sure you follow the [rules](https://discord.gg/NmD4JGCaNc) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [support](https://discord.gg/T8VWyvDfeB).\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len([m for m in guild.members if m.bot])}",
                        color=0x000000)
        
        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url or None)
        else:
            embed.set_thumbnail(url=member.default_avatar)

        if guild_data['welcome'] is not None:
            channel = guild.get_channel(guild_data['welcome'])
            if channel:
                await channel.send(embed=embed)
        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            pass
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if guild.id != 785839283847954433: return
        logs = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
        logs = logs[0]

        if logs.user.id == 816699167824281621:
            return
        if logs.target != member: return

        data = await self.bot.config.find(guild.id)
        if data is None:
            return
        if data['mod_log'] is None:
            return
        if logs.reason is None:
            logs.reason = "None"
        
        log_channel = self.bot.get_channel(data['mod_log'])
        log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
                                    description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0xE74C3C)
        if member.avatar != None:
            log_embed.set_thumbnail(url=member.avatar.url)
        else:
            log_embed.set_thumbnail(url=member.default_avatar)
        log_embed.timestamp = datetime.datetime.utcnow()
        log_embed.set_footer(text=f"ID: {member.id}")

        await log_channel.send(embed=log_embed)

        data["case"] += 1
        await self.bot.config.update(data)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        if guild.id != 785839283847954433: return
        logs = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban)]
        logs = logs[0]

        if logs.user.id == 816699167824281621:
            return
        if logs.target != member: return

        data = await self.bot.config.find(guild.id)
        if data is None:
            return
        if data['mod_log'] is None:
            return
        if logs.reason is None:
            logs.reason = "None"
        
        log_channel = self.bot.get_channel(data['mod_log'])
        log_embed = discord.Embed(title=f"🔨 Unban | Case ID: {data['case']}",
                                    description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0xE74C3C)
        if member.avatar != None:
            log_embed.set_thumbnail(url=member.avatar.url)
        else:
            log_embed.set_thumbnail(url=member.default_avatar)
        log_embed.timestamp = datetime.datetime.utcnow()
        log_embed.set_footer(text=f"ID: {member.id}")

        await log_channel.send(embed=log_embed)

        data["case"] += 1
        await self.bot.config.update(data)

async def setup(bot):
    await bot.add_cog(Events(bot))