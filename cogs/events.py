from discord.ext import commands, tasks
from ui.buttons import verify
import datetime
import discord
from copy import deepcopy
import asyncio

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_task = self.check_update_task.start()
        self.vote_remider_task = self.check_remiders.start()
    
    def cog_unload(self):
        self.check_remiders.cancel()
        self.check_update_task.cancel()
    
    @tasks.loop(seconds=300)
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
        self.bot.add_view(verify(self.bot))
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
            return await ctx.send(f"An error occured while executing this command\n```\n{error}\n```")

        else:
            embed = discord.Embed(color=0xE74C3C,description=f"<:dnd:840490624670892063> | Error: `{error}`")
            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot: return
        guild_data = self.bot.config_cache.get(member.guild.id)
        guild = member.guild
        if not guild_data: return
        if guild.id != 785839283847954433: return
        
        roles = []
        for role in guild_data['join_roles']:
            role = discord.utils.get(member.guild.roles, id=role)
            if role:
                await member.add_roles(role)
                await asyncio.sleep(0.5)
        
        embed = discord.Embed()

        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url or None)
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar.url or None)
        else:
            embed.set_thumbnail(url=member.default_avatar)
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.default_avatar.url)

        
        embed.description = f"Welcome {member.mention} to {guild.name}!"
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=member.id)

        if guild_data['welcome'] is not None:
            channel = guild.get_channel(guild_data['welcome'])
            if channel:
                await channel.send(member.mention, embed=embed)
        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            pass
        
        if guild_data['qurantine'] == True:
            role = discord.utils.get(member.guild.roles, id=953006119436030054)
            await member.add_roles(role, reason="Verification Enabled")


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
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @tasks.loop(seconds=60)
    async def check_remiders(self):
        currentTime = datetime.datetime.utcnow()
        currentVotes = deepcopy(self.bot.current_votes)
        for key, value in currentVotes.items():
            
            if value['reminded'] == True:
                continue
                
            expired_time = value['last_vote'] + datetime.timedelta(hours=12)

            if currentTime >= expired_time and value['reminded'] == False:
                self.bot.dispatch("vote_reminder", value)
    
    @check_remiders.before_loop
    async def before_check_check_remiders(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_vote_reminder(self, vote):
        if vote['reminded'] == True:
            return
        
        embed = discord.Embed(title="You are able to vote again!",description="Your vote is ready at top.gg:", color=0xE74C3C)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Top.gg', url="https://top.gg/servers/785839283847954433/vote"))

        guild = self.bot.get_guild(785839283847954433)
        member = guild.get_member(vote['_id'])

        if member is None:
            return await self.bot.votes.delete(vote['_id'])

        await member.remove_roles(guild.get_role(786884615192313866))

        vote['reminded'] = True
        await self.bot.votes.upsert(vote)

        try:
            await member.send(embed=embed, view=view)
        except discord.HTTPException:
            pass

        try:
            self.bot.current_votes.pop(vote['_id'])
        except KeyError:
            pass

async def setup(bot):
    await bot.add_cog(Events(bot))