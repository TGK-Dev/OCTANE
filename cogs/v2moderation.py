import asyncio
from code import interact
import datetime
from dis import dis
from email import message
from typing import MutableSet
import discord
import re
from discord import user
from aiohttp import ClientSession
import json

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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="uerinfo", description="Give all Infomation about user", usage="[member]", aliases=['whois'])
    @commands.check_any(checks.is_me(), checks.can_use())
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
        m = await ctx.send(embed=embed)
        await m.edit(view=roles(self.bot, ctx, member, m))


    @commands.command(name="mute", description="put user in timeout", usage="[member] [time]", aliases=["timeout"])
    @commands.check_any(checks.is_me(), checks.can_use())
    async def mute(self, ctx, user: discord.Member, time: TimeConverter):
        await ctx.message.delete()
        if int(time) > 2419200:return await ctx.send("You can't set timeout for more than 28days")
        time = datetime.datetime.utcnow() + datetime.timedelta(seconds=time)
        time = time.isoformat()
        url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}"
        payload = {
            "communication_disabled_until": time
            }
        headers = {
            "Authorization": f"Bot {self.bot.config_token}",
            "Content-Type": "application/json",
            }

        async with ClientSession() as session:
            async with session.patch(url, data=json.dumps(payload),headers=headers) as response:
                r = await response.json()
                await session.close()

        embed = discord.Embed(description=f"<:dynosuccess:898244185814081557> ***{user} Was Timeout***",color=0x11eca4)
        await ctx.channel.send(embed=embed)
        log_embed = discord.Embed(title=f"Mute | {user}")
        log_embed.add_field(name="User", value=user.mention)
        log_embed.add_field(name="Moderator", value=ctx.author.mention)
        channel = self.bot.get_channel(803687264110247987)
        await channel.send(embed=log_embed)
    
    @commands.command(name="selfmute", description="put Your self in timeout", usage="[member] [time]", aliases=["smt"])
    async def selfmute(self, ctx, time: TimeConverter):
        if int(time) > 2419200:return await ctx.send("You can't set timeout for more than 28days")
        mutet = time
        time = datetime.datetime.utcnow()+ datetime.timedelta(seconds=time)
        time = time.isoformat()
        url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{ctx.author.id}"
        payload = {
            "communication_disabled_until": time
            }
        headers = {
            "Authorization": f"Bot {self.bot.config_token}",
            "Content-Type": "application/json",
            }

        async with ClientSession() as session:
            async with session.patch(url, data=json.dumps(payload),headers=headers) as response:
                r = await response.json()
                await session.close()
        
        await ctx.reply(f"You Have SelfMuted your self for {format_timespan(mutet)}\nPlease don't ask staff for unmute")

def setup(bot):
    bot.add_cog(v2Moderation(bot))
