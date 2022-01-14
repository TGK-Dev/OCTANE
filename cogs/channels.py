import asyncio
import discord
import random
import re
import datetime

from discord.ext import commands

from humanfriendly import format_timespan

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

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636,
                        785845265118265376, 787259553225637889, 843775369470672916]
            for mod in mod_role:
                role = discord.utils.get(ctx.guild.roles, id=mod)
                if role in ctx.author.roles:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
                    return (ctx.command.name in check)
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902,799037944735727636,785845265118265376,787259553225637889,843775369470672916), is_me())
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
    @commands.check_any(perm_check(), is_me())
    async def hide(self, ctx, role: discord.Role = None):
        channel = ctx.channel
        role = role if role else discord.utils.get(
            ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.mention} is now hidden for{role.mention}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Unhide", description="Unhide Channels For mentioned Role", usage="[role]")
    @commands.check_any(perm_check(), is_me())
    async def unhide(self, ctx, role: discord.Role = None):
        channel = ctx.channel
        role = role if role else discord.utils.get(
            ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Visibal for for {role.name}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Sync", description="Sync Channels permissions to it's Category", usage="[channel]")
    @commands.check_any(perm_check(), is_me())
    async def sync(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel

        await channel.edit(sync_permissions=True)
        await ctx.send("permissions are Synced", delete_after=15)

def setup(bot):
    bot.add_cog(channel(bot))
