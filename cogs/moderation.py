import re
import datetime
from copy import deepcopy

import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


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


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

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

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name='mute',
        description="Mutes a given user for x time!",
        ussage='<user> [time]'
    )
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
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


        try:
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Muted")
            await ctx.send(embed=em)
            await member.send(f"You Have Muted For |{time}|")
        except discord.HTTPException:
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Muted I couldn't DM them.**")
            await ctx.send(embed=emb)
        log_channel = self.bot.get_channel(827245906331566180)

        embed = discord.Embed(title=f"Muted | {member.name}")
        embed.add_field(name="User", value=f"{member.mention}")
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        embed.add_field(name="Time", value=f"{time}")
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await channel.send(embed=embed)


    @commands.command(
        name='unmute',
        description="Unmuted a member!",
        usage='<user>'
    )
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
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

    @commands.command(
        name="kick",
        description="A command which kicks a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.send(f"You Have Been kicked")
            await ctx.guild.kick(user=member, reason=reason)
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been kicked")
            await ctx.send(embed=em)
        except discord.HTTPException:
            await ctx.guild.kick(user=member, reason=reason)
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been kicked I couldn't DM them.**")
            await ctx.send(embed=emb)

        log_channel = self.bot.get_channel(827245906331566180)

        embed = discord.Embed(title=f"kicked | {member.name}")
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await channel.send(embed=embed)


    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.send(f"You Have Been kicked")
            await ctx.guild.ban(user=member, reason=reason)
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been kicked")
            await ctx.send(embed=em)
        except discord.HTTPException:
            await ctx.guild.ban(user=member, reason=reason)
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been kicked I couldn't DM them.**")
            await ctx.send(embed=emb)

        log_channel = self.bot.get_channel(827245906331566180)

        embed = discord.Embed(title=f"Banned | {member.name}")
        embed.add_field(name="User", value=f"{member.name}")
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await channel.send(embed=embed)
    @commands.command(
        name="unban",
        description="A command which unbans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} unbanned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="purge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=15):
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(name="User Info", description="Give all Infomation about user", usage="[member]")
    @commands.has_permissions(manage_messages=True)
    async def whois(self, ctx, member: discord.Member = None):
        
        def fomat_time(time):
          return time.strftime('%d-%B-%Y %I:%m %p')

        member = member if member else ctx.author
        usercolor = member.color

        
        embed = discord.Embed(title=f'{member.name}', color=usercolor)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
        embed.add_field(name='Created at:', value=fomat_time(member.created_at))
        embed.add_field(name='Joined at', value=fomat_time(member.joined_at))

        hsorted_roles = sorted([role for role in member.roles[+1:]], key=lambda x: x.position, reverse=True)
        

        embed.add_field(name='Top:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
        embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))