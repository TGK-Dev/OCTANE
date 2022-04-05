import datetime
import discord
import re
import asyncio
# ----------------------
from bson.objectid import ObjectId
from discord.ext import commands
from utils.util import Pag
from utils.checks import checks

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
description = "Warnings System"


class Warns(commands.Cog, description=description):
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

    @commands.command(name="Warnings", description="Show All Warnings for User", usage="[member]")
    @commands.check_any(checks.can_use())
    async def Warnings(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)

        if not bool(warns):
            return await ctx.send(f"Couldn't find any warns for: `{member.display_name}`")

        warns = sorted(warns, key=lambda x: x["number"])

        pages = []
        for warn in warns:
            description = f"""
            Warn id: `{warn['_id']}`
            Warn Number: `{warn['number']}`
            Warn Reason: `{warn['reason']}`
            Warned By: <@{warn['warned_by']}>
            Warn Time: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)

        await Pag(
            title=f"Warns for `{member.display_name}`",
            colour=0xCE2029,
            entries=pages,
            length=2
        ).start(ctx)

async def setup(bot):
    await bot.add_cog(Warns(bot))
