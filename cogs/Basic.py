import discord
import psutil
import time
import platform
import datetime
from humanfriendly import format_timespan
from discord_together import DiscordTogether

from discord.ext import commands

description = "Some Basic commands"

class Link(discord.ui.View):
    def __init__(self, url):
        self.url = url
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label='Youtube', url=self.url, emoji="<:yt:929015299481673749>"))

class Basic(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.togetherControl = await DiscordTogether(self.bot.config_token)
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    async def youtube(self, ctx):
        link = await self.bot.togetherControl.create_link(797363342238285844, 'youtube', max_age=60)
        await ctx.message.delete()
        embed = discord.Embed(description="You can Start Your Activiy By pressing bellow Button")
        await ctx.send(embed=embed, view=Link(link))
        

    @commands.command()
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        start = self.bot.uptime
        now = datetime.datetime.utcnow()
        newtime = (now - start)
        total_s = newtime.total_seconds()

        dstart = datetime.datetime.utcnow()
        await self.bot.config.find(ctx.guild.id)
        dend = datetime.datetime.utcnow()
        dping = (dend - dstart)
        dping = dping.total_seconds()

        embed = discord.Embed(title="Pingss", color=ctx.author.colour,
                              description=f"**Response TIme** {round(self.bot.latency * 1000)}ms\n**API**: {round((end_time - start_time) * 1000)}ms\n**Database Ping**: {round(dping * 1000)}Ms\n**My Age**: {format_timespan(total_s)}")

        await message.edit(content=None, embed=embed)

    @commands.command(
        name="stats", description="A useful command that displays bot statistics.", usage="stats"
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))
        cpu = round(psutil.cpu_percent(), 1)

        embed = discord.Embed(
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version:", value=self.bot.version)
        embed.add_field(name="Python Version:", value=pythonVersion)
        embed.add_field(name="Nextcord Version", value=dpyVersion)
        embed.add_field(name="Total Guilds:", value=serverCount)
        embed.add_field(name="Total Users:", value=memberCount)
        embed.add_field(name="CPU Useage:", value=f"{str(cpu)}%")
        embed.add_field(name="RAM Useage:",
                        value=f"{round(psutil.virtual_memory().percent,1)}%")
        embed.add_field(name="Bot Developers:",
                        value="<@488614633670967307>\n<@301657045248114690>")
        embed.add_field(name="Embed Format:",
                        value="<@413651113485533194>\n<@651711446081601545>")

        embed.set_footer(
            text=f"Developed by Jay & Utik007 | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url)

        view = discord.ui.View()

        view.add_item(discord.ui.Button(label='GitHub', url="https://github.com/Jay24004/TGK.bot", emoji="<:github1:931838892787785759>"))
        await ctx.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Basic(bot))
