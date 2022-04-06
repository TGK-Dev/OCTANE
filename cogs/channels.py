import discord
import re
from discord.ext import commands
from humanfriendly import format_timespan
from utils.checks import checks
from discord import app_commands
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
        self.load_tree_commands()
    
    def load_tree_commands(self):

        @app_commands.command(name="slowmod", description="Set the slowmode of a channel")
        @app_commands.describe(time="Slowmode time Exp: 1h30m",)
        async def slowmod(interaction: discord.Interaction, time: str):
            time = await TimeConverter().convert(interaction, time)
            if not interaction.user.guild_permissions.manage_messages:
                return await interaction.send("You don't have permission to use this command")
            if time is None or time == 0:
                await interaction.channel.edit(slowmode_delay=None)
                embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed slowmode from {interaction.channel.mention}",color=0x2f3136)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.channel.edit(slowmode_delay=time)
                embed = discord.Embed(description=f"<:allow:819194696874197004> | Set slowmode to {time}s on {interaction.channel.mention}",color=0x2f3136)
                await interaction.response.send_message(embed=embed)
        
        self.bot.slash_commands.append(slowmod)

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

async def setup(bot):
    await bot.add_cog(channel(bot))
