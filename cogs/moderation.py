import asyncio
import datetime
import discord
import re

from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from discord.ext.buttons import Paginator

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


class Moderation(commands.Cog, description=description, command_attrs=dict(hidden=False)):
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
            for role in ctx.author.roles[-5:]:
                if role.id in mod_role:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
            return (ctx.command.name in check)
        return commands.check(predicate)


    @tasks.loop(minutes=5)
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
                    print(f"Unmuted: {member.display_name}")

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass

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
                reason = "Auto Unban"
                await guild.unban(member, reason=reason)
                print("Testings")
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

    @commands.command(
        name='mute',
        description="Mutes a given user for x time!",
        usage='<user> [time] [reason]'
    )
    @commands.check_any(perm_check(), is_me())
    async def mute(self, ctx, member: discord.Member, time: TimeConverter=None, *,reason):
        await ctx.message.delete()
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
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Muted**")
                await ctx.send(embed=em)
                await member.send(f"You Have Muted for {reason} || {time}")
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Muted I couldn't DM them.**")
                await ctx.send(embed=emb)
                
            log_channel = self.bot.get_channel(803687264110247987)
            embed = discord.Embed(title=f"Muted | {member.name}", inline=True)
            embed.add_field(name="User", value=f"{member.mention}", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Reason", value=f"{reason}", inline=True)
            embed.add_field(name="Time", value=f"{time}", inline=True)
            embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

            await log_channel.send(embed=embed)

        else:

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

            try:
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Muted**")
                await ctx.send(embed=em)
                await member.send(f"You Have Muted for {reason} || {time}")
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Muted I couldn't DM them.**")
                await ctx.send(embed=emb)
                
            log_channel = self.bot.get_channel(803687264110247987)
            embed = discord.Embed(title=f"Muted | {member.name}", inline=True)
            embed.add_field(name="User", value=f"{member.mention}", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Reason", value=f"{reason}", inline=True)
            embed.add_field(name="Time", value=f"{time}", inline=True)
            embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

            await log_channel.send(embed=embed)

            if time and time < 300:
                await asyncio.sleep(time)

                if role in member.roles:
                    await member.remove_roles(role)
                    await ctx.send(f"Unmuted `{member.display_name}`")

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass


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
        await ctx.send(f"Unmuted `{member.display_name}`")

        log_channel = self.bot.get_channel(803687264110247987)

        embed = discord.Embed(title=f"Unmuted | {member.name}")
        embed.add_field(name="User", value=f"{member.name}", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await log_channel.send(embed=embed)



    @commands.command(name="kick", description="kick User from the guild", usage="<user> [reason]")
    @commands.check_any(perm_check(), is_me())
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")

        await ctx.message.delete()
        try:
            await member.send(f"You Have Been kicked")
            await ctx.guild.kick(user=member, reason=reason)
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been kicked")
            await ctx.send(embed=em)
        except discord.HTTPException:
            await ctx.guild.kick(user=member, reason=reason)
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been kicked I couldn't DM them.**")
            await ctx.send(embed=emb)

        log_channel = self.bot.get_channel(803687264110247987)
        log2_channel = self.bot.get_channel(806107399005667349)

        embed = discord.Embed(title=f"kicked | {member.name}")
        embed.add_field(name="User", value=f"{member.name}", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await log_channel.send(embed=embed)


    @commands.command(name="Ban", description="Ban user From guild", usage="<user> [time] [reason]") 
    @commands.check_any(perm_check(), is_me())
    async def ban(self, ctx, member: discord.User, time: TimeConverter=None, *, reason=None):
        await ctx.message.delete()
        try:
            user = member.name.lower()
            user = await commands.MemberConverter().convert(ctx, user)
            if user.top_role >= ctx.author.top_role:
                return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")
        except:
           pass

        if time == None:
            await ctx.guild.ban(user=member, reason=reason)

            try:
                await member.send(f"You Have Been Banned | {reason}")
                await ctx.guild.ban(user=member, reason=reason)
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been Banned || {reason}")
                await ctx.send(embed=em)
            except discord.HTTPException:
                await ctx.guild.ban(user=member, reason=reason)
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name}** Has Been Banned || {reason}")
                await ctx.send(embed=emb)
        else:
        
        
            try:
                await member.send(f"You Have Been Banned | {reason}")
                await ctx.guild.ban(user=member, reason=reason)
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been Banned || {reason}")
                await ctx.send(embed=em)
            except discord.HTTPException:
                await ctx.guild.ban(user=member, reason=reason)
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name}** Has Been Banned || {reason}")
                await ctx.send(embed=emb)

            data = {
                '_id': member.id,
                'BannedAt': datetime.datetime.now(),
                'BanDuration': time or None,
                'BanedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }
            await self.bot.bans.upsert(data)
            self.bot.ban_users[member.id] = data


            log_channel = self.bot.get_channel(827245906331566180)


            embed = discord.Embed(title=f"Banned | {member.name}")
            embed.add_field(name="User", value=f"{member.name}")
            embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
            embed.add_field(name="Reason", value=f"{reason}", inline=False)

            embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

            await log_channel.send(embed=embed)

    @commands.command(name="unban", description="Unban user From guild", usage="<user> [reason]")
    @commands.check_any(perm_check(), is_me())
    async def unban(self, ctx, member, *, reason=None):
        await ctx.message.delete()
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} unbanned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

        await self.bot.bans.delete(member.id)
        try:
            self.bot.bot.ban_users.pop(member.id)
        except KeyError:
            pass

        log_channel = self.bot.get_channel(803687264110247987)

        embed = discord.Embed(title=f"unban | {member.name}")
        embed.add_field(name="User", value=f"{member.name}", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.set_footer(text=f"{member.id}")

        await log_channel.send(embed=embed)


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

        
        embed = discord.Embed(title=f'{member.name}', color=usercolor)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
        embed.add_field(name='Created at:', value=fomat_time(member.created_at))
        embed.add_field(name='Joined at', value=fomat_time(member.joined_at))
        embed.add_field(name='Account Status', value=str(member.status).title())
        embed.add_field(name='Account Activity', value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

        hsorted_roles = sorted([role for role in member.roles[-2:]], key=lambda x: x.position, reverse=True)
        

        embed.add_field(name='Top Role:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
        embed.add_field(name='Number of Roles', value=f"{len(member.roles) -1 }")
        embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="tag", hidden=True)
    @commands.check_any(perm_check(), is_me())
    async def tag(self, ctx):
        await ctx.message.delete()
        await ctx.send("**Avoid tagging Owners/Admins.**\nKindly tag available mods/admins for queries.\nOr simply raise a ticket from <#785901543349551104>.\n")


def setup(bot):
    bot.add_cog(Moderation(bot))