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
from discord import app_commands
from typing import Union
from utils.converter import TimeConverter


class Mod(commands.Cog, name="Moderation",description = "Moderation commands"):
    def __init__(self, bot):
        self.bot = bot
        self.ban_task = self.check_current_bans.start()
    
    def cog_unload(self):
        self.ban_task.cancel()
    
    @tasks.loop(seconds=60)
    async def check_current_bans(self):
        currentTime = datetime.datetime.now()
        bans = deepcopy(self.bot.current_bans)
        for key, value in bans.items():
            if value['BanDuration'] is None:
                continue

            unbantime = value['BannedAt'] + relativedelta(days=7)

            if currentTime >= unbantime:
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
        try:
            await guild.unban(user, reason="Auto Automatic ban expired")
        except discord.NotFound:
            pass
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

    @commands.hybrid_command(name="slowmode", aliases=["sm"], description="Set slowmode for a channel", usage="<time>")
    @app_commands.describe(time="Slowmod Time")
    @app_commands.guilds(964377652813234206)
    async def slowmode(self, ctx, time: TimeConverter=None):

        if time is None:
            await ctx.channel.edit(slowmode_delay=None)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed slowmode from {ctx.channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)
        elif time > 21600:
            await ctx.send("Slowmode can't be more than 6 hours",ephemeral=True)
        else:
            await ctx.channel.edit(slowmode_delay=time)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Set slowmode to {format_timespan(time)}s in {ctx.channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mod(bot))