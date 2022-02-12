import datetime
import discord
import re
from discord import Webhook
import aiohttp

from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from utils.checks import checks

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Moderation commands"

class roles(discord.ui.View):
    def __init__(self, bot, ctx, user: discord.Member, message: discord.Message):
        super().__init__(timeout=60)
        self.bot = bot
        self.ctx = ctx
        self.user = user
        self.message = message
    
    @discord.ui.button(label="Show Roles", style=discord.ButtonStyle.blurple)
    async def roles(self, button: discord.ui.Button, interaction: discord.Interaction):
        hsorted_roles = sorted([role for role in self.user.roles[1:]], key=lambda x: x.position)
        embed = discord.Embed(description=", ".join(role.mention for role in hsorted_roles),color=self.user.color)
        embed.add_field(name="Total Roles", value=len(self.user.roles))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Permissions", style=discord.ButtonStyle.blurple)
    async def perms(self, button: discord.ui.Button, interaction: discord.Interaction):
        perm = ", ".join([str(p[0]).replace("_", " ").title() for p in self.user.guild_permissions if p[1]])
        embed = discord.Embed(description=f"`{perm}`", color=self.user.color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction):
        if interaction.user.guild_permissions.manage_messages:
            return True
        else:
            return False

    async def on_timeout(self):
        for b in self.children:
            b.disabled = True
        await self.message.edit(view=self)

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
        self.ban_task = self.check_current_bans.start()

    def cog_unload(self):
        self.ban_task.cancel()

    @tasks.loop(seconds=5)
    async def check_current_bans(self):
        currentTime = datetime.datetime.now()
        bans = deepcopy(self.bot.current_ban)
        for key, value in bans.items():
            if value['BanDuration'] is None:
                continue

            unbantime = value['BannedAt'] + relativedelta(days=7)

            if currentTime >= unbantime:
                print(value)
                guild = self.bot.get_guild(int(value['guildId']))
                member = await self.bot.fetch_user(int(value['_id']))
                moderator = guild.get_member(value['BanedBy'])
                self.bot.dispatch('ban_expired', guild, member, moderator)

                await self.bot.bans.delete(member.id)

                try:
                    self.bot.current_ban.pop(member.id)
                except KeyError:
                    pass
    
    @check_current_bans.before_loop
    async def before_check_current_bans(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_ban_expired(self, guild: discord.Guild, user: discord.User, moderator: discord.Member):
        if await guild.fetch_ban(user) == None:
            return
        await guild.unban(user, reason="Auto Automatic ban expired")
        data = await self.bot.config.find(785839283847954433)
        embed = discord.Embed(title=f"🔨 UnBan | Case ID: {data['case']}",
                                    description=f" **Offender**: {user.name} | {user.mention} \n**Reason**: Auto Automatic expired\n **Moderator**: {moderator.name} {moderator.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {user.id}")
        data["case"] += 1
        await self.bot.config.upsert(data)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.bot.logging_webhook, session=session)
            await webhook.send(username=f"{self.bot.user.name} Logging", avatar_url=self.bot.user.avatar.url,embed=embed)
            await session.close()

    @commands.command(name="uerinfo", description="Give all Infomation about user", usage="[member]", aliases=['whois'])
    @commands.check_any(checks.can_use())
    async def uerinfo(self, ctx, member: discord.Member = None):
        await ctx.message.delete()

        def fomat_time(time):
            return time.strftime('%d-%B-%Y %I:%m %p')

        member = member if member else ctx.author
        usercolor = member.color

        embed = discord.Embed(title=f'{member.name}', color=usercolor)
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name='Account Name:',
                        value=f'{member.name}', inline=False)
        embed.add_field(
            name='Created at:', value=f"{fomat_time(member.created_at)}")
        embed.add_field(name='Joined at', value=fomat_time(member.joined_at))
        embed.add_field(name='Account Status',
                        value=str(member.status).title())
        embed.add_field(name='Account Activity',
                        value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")
        embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar.url)

        Member = await self.bot.fetch_user(member.id)
        if Member.banner:
            embed.set_image(url=Member.banner)
        m = await ctx.send(embed=embed)
        await m.edit(view=roles(self.bot, ctx, member, m))


    @commands.command(name="mute", description="put user in timeout", usage="[member] [time]", aliases=["timeout"])
    @commands.check_any(checks.can_use())
    async def mute(self, ctx, user: discord.Member, time: TimeConverter):
        await ctx.message.delete()
        if int(time) > 2419200:return await ctx.send("You can't set timeout for more than 28days")
        time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
        
        await user.edit(timeout=time)

        embed = discord.Embed(description=f"<:dynosuccess:898244185814081557> ***{user} Was Timeout***",color=0x11eca4)
        await ctx.channel.send(embed=embed)

        log_embed = discord.Embed(title=f"Mute | {user}")
        log_embed.add_field(name="User", value=user.mention)
        log_embed.add_field(name="Moderator", value=ctx.author.mention)
        channel = self.bot.get_channel(803687264110247987)
        await channel.send(embed=log_embed)
    
    @commands.command(name="unmute", description="Remove timeout from user", usage="[member] [time]")
    @commands.check_any(checks.can_use())
    async def unmute(self, ctx, user: discord.Member):
        await ctx.message.delete()
        
        await user.edit(timeout=None)

        embed = discord.Embed(description=f"<:dynosuccess:898244185814081557> ***{user} Was Timeout***",color=0x11eca4)
        await ctx.channel.send(embed=embed)

        log_embed = discord.Embed(title=f"UnMute | {user}")
        log_embed.add_field(name="User", value=user.mention)
        log_embed.add_field(name="Moderator", value=ctx.author.mention)
        channel = self.bot.get_channel(803687264110247987)
        await channel.send(embed=log_embed)
    
    @commands.command(name="selfmute", description="put Your self in timeout", usage="[member] [time]", aliases=["smt"])
    async def selfmute(self, ctx, time: TimeConverter):
        if int(time) > 2419200:return await ctx.send("You can't set timeout for more than 28days")
        mutet = time
        time = datetime.datetime.utcnow()+ datetime.timedelta(seconds=time)
        await ctx.author.edit(timeout=time)        
        await ctx.reply(f"You Have SelfMuted your self for {format_timespan(mutet)}\nPlease don't ask staff for unmute")

def setup(bot):
    bot.add_cog(v2Moderation(bot))
