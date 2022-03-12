import asyncio
import discord
import random
import re
import datetime
from discord.ext import commands
from humanfriendly import format_timespan
from utils.checks import checks

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Channel Management Commands"

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


class channel(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
    @commands.check_any(checks.can_use())
    async def slowmode(self, ctx, time: TimeConverter = None):
        await ctx.message.delete()
        channel = ctx.channel

        if time is None or time == 0:
            time = 0
            await ctx.channel.edit(slowmode_delay=time)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed slowmode from {channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)

        if time >= 21600:
            return await ctx.send(f"Slowmode interval can't be greater than 6 hours.", delete_after=30)

        await ctx.channel.edit(slowmode_delay=time)

        embed = discord.Embed(description=f"<:allow:819194696874197004> | Set {channel.mention} slowmode to {format_timespan(time)}",
                              color=0x2f3136)
        await ctx.send(embed=embed)

    @commands.command(name="Hide", description="Hide Channels For mentioned Role", usage="[role]")
    @commands.check_any(checks.can_use())
    async def hide(self, ctx):
        channel = ctx.channel
        role =  ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.mention} is now hidden for @everyone')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Unhide", description="Unhide Channels For mentioned Role", usage="[role]")
    @commands.check_any(checks.can_use())
    async def unhide(self, ctx, role: discord.Role = None):
        channel = ctx.channel
        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.mention} is Now Visible for for @everyone')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Sync", description="Sync Channels permissions to it's Category", usage="[channel]")
    @commands.check_any(checks.can_use())
    async def sync(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel

        await channel.edit(sync_permissions=True)
        await ctx.send("permissions are Synced", delete_after=15)

def setup(bot):
    bot.add_cog(channel(bot))
