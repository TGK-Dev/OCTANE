import asyncio
import platform
import random

import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="stats", description="A useful command that displays bot statistics."
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version:", value=self.bot.version)
        embed.add_field(name="Python Version:", value=pythonVersion)
        embed.add_field(name="Discord.Py Version", value=dpyVersion)
        embed.add_field(name="Total Guilds:", value=serverCount)
        embed.add_field(name="Total Users:", value=memberCount)
        embed.add_field(name="Bot Developers:", value="<@488614633670967307>")

        embed.set_footer(text=f"Carpe Noctem | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=['sinfo'])
    async def serverinfo(self, ctx):
        usercolor = ctx.author.color
        guild = self.bot.get_guild(785839283847954433)
        booter= int(guild.premium_subscription_count)

        em = discord.Embed(title='Info for The Gamblers Kingdom', color=usercolor)
        em.set_thumbnail(url=guild.icon_url)
        em.add_field(name='Owners', value='utki007#007, JAY#0138', inline=True)
        em.add_field(name='Booster Count', value=f'The Total booster {booter} \n booster Role <@&786477872029892639>', inline=False)
        em.add_field(name='Server Member Count: ', value=f'{guild.member_count}', inline=False)
        em.set_footer(text='ID: 785839283847954433, Created•12/08/2020', icon_url=guild.icon_url)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Misc(bot))
