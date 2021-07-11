import asyncio
import datetime
import discord
import re


from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from typed_flags import TypedFlags

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Moderation commands"

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class v2Moderation(commands.Cog, description=description, command_attrs=dict(hidden=False)):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()
        self.ban_task = self.check_current_bans.start()

    def cog_unload(self):
        self.mute_task.cancel()

    def cog_unload(self):
        self.ban_task.cancel()

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307 , 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916]
            for mod in mod_role:
                role = discord.utils.get(ctx.guild.roles, id=mod)
                if role in ctx.author.roles:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
                    return (ctx.command.name in check)
        return commands.check(predicate)


    @tasks.loop(seconds=10)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in member.roles:
                    await member.remove_roles(role)

                    log_channel = self.bot.get_channel(855784930494775296)
                    data = await self.bot.config.find(guild.id)
                    log_embed = discord.Embed(title=f"🔊 UnMute | Case ID: {data['case']}",
                    	description=f"**Offender**: {member.name} | {member.mention} \n**Moderator**: {self.bot.user.name} | {self.bot.user.mention} \n**Reason**: Temporary Mute expired", color=0x2ECC71)
                    log_embed.set_thumbnail(url=member.avatar_url)
                    log_embed.timestamp = datetime.datetime.utcnow()
                    log_embed.set_footer(text=f"ID: {member.id}")

                    await log_channel.send(embed=log_embed)

                    data["case"] += 1
                    await self.bot.config.upsert(data)

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass#🔓

    @tasks.loop(seconds=10)
    async def check_current_bans(self):
        currentTime = datetime.datetime.now()
        bans = deepcopy(self.bot.ban_users)
        for key, value in bans.items():
            if value['BanDuration'] is None:
                continue

            unbanTime = value['BannedAt'] + relativedelta(seconds=value['BanDuration'])

            if currentTime >= unbanTime:
                guild = self.bot.get_guild(value['guildId'])
                member = await self.bot.fetch_user(int(value['_id']))
                reason = "Temporary Ban expired"
                try:
                    await guild.unban(member, reason=reason)
                except:
                    pass

                case = await self.bot.config.find(guild.id)
                log_channel = self.bot.get_channel(855784930494775296)

                log_embed = discord.Embed(title=f"🔓 UnBan | Case ID: {case['case']}",
                    description=f" **Offender**: {member.name} | {member.mention}\n**Reason** {reason}:\n**Moderator**: {self.bot.user.name} {self.bot.user.mention}", color=0x2ECC71)
                log_embed.set_thumbnail(url=member.avatar_url)
                log_embed.set_footer(text=f"ID: {member.id}")
                log_embed.timestamp = datetime.datetime.utcnow()
                await log_channel.send(embed=log_embed)

                case["case"] += 1
                await self.bot.config.upsert(case)

                await self.bot.bans.delete(member.id)
                try:
                    self.bot.ban_users.pop(member.id)
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

    """
    @commands.command(
        name='mute',
        description="Mutes a given user for x time!",
        usage='<user> --reason <reason> --time <time>'
    )
    @commands.check_any(perm_check(), is_me())
    async def mute(self, ctx, member: discord.Member, *,args: TypedFlags):
        #await ctx.message.delete()
        flags = args
        try:
            reason = flags['reason']
        except KeyError:
            reason = "No Reason Provided"

        try:
            time = flags['time']
        except KeyError:
            time = None

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        try:
            if self.bot.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        if time == None:
            await member.add_roles(role)

            try:
                await member.send(f"You Have Muted in {ctx.guild.name}")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004>|**{member.name} Has been Muted**")
                await ctx.send(embed=em)
            except discord.HTTPException:
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004>|**{member.name} Has been Muted**")
                await ctx.send(embed=emb)

            data = await self.bot.config.find(ctx.guild.id)
            log_channel = self.bot.get_channel(855784930494775296)

            log_embed = discord.Embed(title=f"🔇 Mute | Case ID: {data['case']}",
                description=f" **Offender**: {member.name} | {member.mention}\n **Reason**: {reason}\n **Duration**: None \n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}",
                color=0x706e6d)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            data["case"] += 1
            await self.bot.config.upsert(data)

        else:

            time = await TimeConverter().convert(ctx, time)

            data = {
                '_id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': time or None,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }
            await self.bot.mutes.upsert(data)
            self.bot.muted_users[member.id] = data

            await member.add_roles(role)

            time = format_timespan(time)

            try:
                await member.send(f"You Have Muted in {ctx.guild.name}\n**Reason**:{reason}\nDuration: {time}")
                
            except discord.HTTPException:
                pass
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004>|**{member.display_name} Has been Muted for {time}**")
            await ctx.send(embed=em)


            case = await self.bot.config.find(ctx.guild.id)
            log_channel = self.bot.get_channel(855784930494775296)

            log_embed = discord.Embed(title=f"🔇 Mute | Case ID: {case['case']}",
                description=f" **Offender**: {member.name} | {member.mention}\n **Reason**: {reason}\n **Duration**: {time} \n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}",
                color=0x706e6d)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            case["case"] += 1
            await self.bot.config.upsert(case)

    @commands.command(
        name='unmute',
        description="Unmuted a member!",
        usage='<user>'
    )
    @commands.check_any(perm_check(), is_me())
    async def unmute(self, ctx, member: discord.Member):
        await ctx.message.delete()
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await member.remove_roles(role)
        embed = discord.Embed(description=f"<:allow:819194696874197004>|{member.mention} unmuted",color=0x2ECC71)
        await ctx.send(embed=embed)

        log_channel = self.bot.get_channel(855784930494775296)
        data = await self.bot.config.find(ctx.guild.id)
        log_embed = discord.Embed(title=f"🔊 UnMute | Case ID: {data['case']}",
            description=f" **Offender**: {member.name} | {member.mention} \n **Moderator**: {ctx.author.display_name} {ctx.author.mention}", color=0x2ECC71)
        log_embed.set_thumbnail(url=member.avatar_url)
        log_embed.timestamp = datetime.datetime.utcnow()
        log_embed.set_footer(text=f"ID: {member.id}")

        await log_channel.send(embed=log_embed)

        data["case"] += 1
        await self.bot.config.upsert(data)

    @commands.command(name="kick", description="kick User from the guild", usage="<user> [**Reason**]")
    @commands.check_any(perm_check(), is_me())
    async def kick(self, ctx, member: discord.Member, *,reason=None):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")
        reason = reason if reason else "No **Reason** Provided"
        await ctx.message.delete()
        try:
            await member.send(f"You Have Been kicked")
        except discord.HTTPException:
        	pass
        await ctx.guild.kick(user=member, reason=reason)

        emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has Been kicked.**")
        await ctx.send(embed=emb)

        log_channel = self.bot.get_channel(855784930494775296)
        data = await self.bot.config.find(ctx.guild.id)
        log_embed = discord.Embed(title=f"👢 Kick | Case ID: {data['case']}",
            description=f" **Offender**: {member.name} | {member.mention}\n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}\n **Reason**: {reason}.", color=0xE74C3C)
        log_embed.set_thumbnail(url=member.avatar_url)
        log_embed.timestamp = datetime.datetime.utcnow()
        await log_channel.send(embed=log_embed)

        data["case"] += 1
        await self.bot.config.upsert(data)

    @commands.command(name="Ban",
        description="Ban user From guild",
        usage='<user> --reason <reason> --time <time>')
    @commands.check_any(perm_check(), is_me())
    async def ban(self, ctx, member: discord.User,*,args: TypedFlags):
        flags = args
        try:
            reason = flags['reason']
        except KeyError:
            reason = "No Reason Provided"

        try:
            time = flags['time']
        except KeyError:
            time = None

        await ctx.message.delete()
        try:
            user = member.name.lower()
            user = await commands.MemberConverter().convert(ctx, user)
            if user.top_role >= ctx.author.top_role:
                return await ctx.send("You cannot do this action on this user due to role hierarchy.")
        except:
           pass
        reason = reason if reason else "No Reason Provided"
        if time == None:

            try:
                await member.send(f"You Have Been Banned from {ctx.guild.name} | {reason}")
            except discord.HTTPException:
                pass

            await ctx.guild.ban(user=member, reason=reason, delete_message_days=0)

            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004>|**{member.name}** Has been Banned")
            await ctx.send(embed=em)

            log_channel = self.bot.get_channel(855784930494775296)
            data = await self.bot.config.find(ctx.guild.id)
            log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
                description=f" **Offender**: {member.name} | {member.mention} \n**Reason**: {reason}\n **Moderator**: {ctx.author.display_name} {ctx.author.mention}", color=0xE74C3C)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            data["case"] += 1
            await self.bot.config.upsert(data)

        else:       
        
            data = {
                '_id': member.id,
                'BannedAt': datetime.datetime.now(),
                'BanDuration': time or None,
                'BanedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }
            await self.bot.bans.upsert(data)
            self.bot.ban_users[member.id] = data

            time = format_timespan(time)

            try:
                await member.send(f"You Have Been Banned from {ctx.guild.name} for {time} Reason: {reason}")
            except discord.HTTPException:
                await ctx.guild.ban(user=member, reason=reason)
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004>|**{member.name}** Has Been Banned for {time}")
                await ctx.send(embed=emb)

            await ctx.guild.ban(user=member, reason=reason, delete_message_days=0)

            case = await self.bot.config.find(ctx.guild.id)
            log_channel = self.bot.get_channel(855784930494775296)

            log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {case['case']}",
                description=f" **Offender**: {member.name} | {member.mention} \n**Reason**: {reason}\n **Duration**: {time}\n **Moderator**: {ctx.author.display_name} {ctx.author.mention}", color=0xE74C3C)
            log_embed.set_thumbnail(url=member.avatar_url)
            log_embed.set_footer(text=f"ID: {member.id}")
            log_embed.timestamp = datetime.datetime.utcnow()
            await log_channel.send(embed=log_embed)

            case["case"] += 1
            await self.bot.config.upsert(case)

    @commands.command(name="unban", description="Unban user From guild", usage="<user> [reason]")
    @commands.check_any(perm_check(), is_me())
    async def unban(self, ctx, member, *, reason=None):
        await ctx.message.delete()
        reason = reason if reason else "No Reason Provided"
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)

        embed = discord.Embed(
            description=f"<:allow:819194696874197004>|**{member.name}** Has Been Unbanned"
        )
        await ctx.send(embed=embed)

        await self.bot.bans.delete(member.id)
        try:
            self.bot.bot.ban_users.pop(member.id)
        except :
            pass

        case = await self.bot.config.find(ctx.guild.id)
        log_channel = self.bot.get_channel(855784930494775296)

        log_embed = discord.Embed(title=f"🔓 UnBan | Case ID: {case['case']}",
            description=f" **Offender**: {member.name} | {member.mention}\n **Moderator**: {ctx.author.display_name} {ctx.author.mention}", color=0x2ECC71)
        log_embed.set_thumbnail(url=member.avatar_url)
        log_embed.set_footer(text=f"ID: {member.id}")
        log_embed.timestamp = datetime.datetime.utcnow()
        await log_channel.send(embed=log_embed)

        case["case"] += 1
        await self.bot.config.upsert(case)
    """
    @commands.command(name="purge", description="A command which purges the channel it is called in", usage="[amount]", invoke_without_command = True)
    @commands.check_any(perm_check(), is_me())
    async def purge(self, ctx, amount=10):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="uerinfo", description="Give all Infomation about user", usage="[member]", aliases=['whois'])
    @commands.check_any(perm_check(), is_me())
    async def uerinfo(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        def fomat_time(time):
          return time.strftime('%d-%B-%Y %I:%m %p')

        member = member if member else ctx.author
        usercolor = member.color

        today = (datetime.datetime.utcnow() - member.created_at).total_seconds()

        embed = discord.Embed(title=f'{member.name}', color=usercolor)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
        embed.add_field(name='Created at:', value=f"{fomat_time(member.created_at)}\n{format_timespan(today)}")
        embed.add_field(name='Joined at', value=fomat_time(member.joined_at))
        embed.add_field(name='Account Status', value=str(member.status).title())
        embed.add_field(name='Account Activity', value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

        hsorted_roles = sorted([role for role in member.roles[-2:]], key=lambda x: x.position, reverse=True)
        

        embed.add_field(name='Top Role:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
        embed.add_field(name='Number of Roles', value=f"{len(member.roles) -1 }")
        embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="flags")
    @commands.check_any(is_me())
    async def flags(self, ctx, user: discord.Member, *,args: TypedFlags):
        data = args.lower()
        await ctx.send(f'{user.name}|{args}')


def setup(bot):
    bot.add_cog(v2Moderation(bot))