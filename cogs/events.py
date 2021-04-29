import re
import datetime
from copy import deepcopy
from discord.ext.buttons import Paginator
import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link','vote Link','Vote link', 'pls vote', 'pls Vote', 'Pls vote']

        if message.author.bot:
            return

        messageContent = message.content
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    return await message.reply('**Vote for us here**:\nhttps://top.gg/servers/785839283847954433/vote\n\n__**Voting Perks**__\n❥ Special "Voted" Role.\n❥ 2,500 Casino Cash. Collect using ,collectincome in #:game_die:。casino.\n❥ Access to Dank Memer Premium with 2x Amaari.\n❥ Guild wide 1x Amaari.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild.id 
        guild = self.bot.get_guild(785839283847954433)
        channel =  self.bot.get_channel(837285329610080276)
        robot = discord.utils.get(guild.roles, id=810153515610537994)
        count = guild.member_count

        if member.guild.id == 785839283847954433:

            embed = discord.Embed(title=f'**WELCOME TO TGK, {member.display_name}!**',
                description=f"\n\n:sparkles: Get your favorite roles from [Self Roles](https://discord.gg/6WmKQZrKD9),\nand say _Hello_ to everyone in [Chat](https://discord.gg/B2FDCggkES) !\n\n**To access Dank Memer, react in [Dank Bifrost](https://discord.gg/BUtTb7FVxJ).**\n\n:circus_tent: Also check out other fun game bots on the server:\n✦ [Pokemon](https://discord.gg/6dGkammu6P)  ✦ [Casino](https://discord.gg/f4YzaVyhRE)  ✦[Akinator](https://discord.gg/HyVgTrF2E5)  ✦ [Mudae](https://discord.gg/u2XJ8SaY) ✦\n\nMake sure you follow the [Rules](https://discord.gg/Z4rbTcvDyb) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [Server Support](https://discord.gg/gJhmaFJmra).\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len(robot.members) -1}",
                color=0x000000)
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(f"{member.mention}", embed=embed)

        else:
            return

    @commands.command(name="joint", hidden=True)
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def joint(self, ctx):
        embed = discord.Embed(title=f'**WELCOME TO TGK, {ctx.author.display_name}!**',
            description=f"\n\n:sparkles: Get your favorite roles from [Self Roles](https://discord.gg/6WmKQZrKD9),\nand say _Hello_ to everyone in [Chat](https://discord.gg/B2FDCggkES) !\n\n**To access Dank Memer, react in [Dank Bifrost](https://discord.gg/BUtTb7FVxJ).**\n\n:circus_tent: Also check out other fun game bots on the server:\n✦ [Pokemon](https://discord.gg/6dGkammu6P)  ✦ [Casino](https://discord.gg/f4YzaVyhRE)  ✦[Akinator](https://discord.gg/HyVgTrF2E5)  ✦ [Mudae](https://discord.gg/u2XJ8SaY) ✦\n\nMake sure you follow the [Rules](https://discord.gg/Z4rbTcvDyb) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [Server Support](https://discord.gg/gJhmaFJmra).\n\nHave fun!\n\n__Server Member Count:__ {ctx.author.guild.member_count}",
            color=0x2ECC71)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('Member not Found')
        elif isinstance(error, commands.UserNotFound):
            await ctx.send('User not Found')
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send('Channel Not Found')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('Role Not Found')
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.send(f'The {name} is Already Loaded')
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send(f'The {name} is Already UnLoaded')
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send(f'The Extension not Found')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('The command is disabed by Owner')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply(f'Please Enter all the Requird Argument')
        else:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
"""
    @commands.Cog.listener()
    async def on_message(self, meg):
        if meg.author.bot:
            return

        odd = [1,3,5,7,9]
        even = [0,2,4,6,8]

        num1 = random.choice(odd)
        num2 = random.choice(even)

        if num1 > num2:

            embed = discord.Embed(title="Random Event",
                description="Server Is been raided type `ban` to ban them all",
                color=0x09fa2c)
            mess = await meg.channel.send(embed=embed)
            try:
                await self.bot.wait_for("message", check=lambda m: m.content.startswith(f"ban"), timeout=60)
                over = discord.Embed(title="Event expired",
                    description=f"All Reider Was Banned by {m.author.mention}",
                    color=0xbf1932)
                await mess.edit(embed=over)
            except asyncio.TimeoutError:
                over = discord.Embed(title="Event expired",
                    description=f"Server got raided no one saved Server",
                    color=0xbf1932)

                await mess.edit(embed=over)
"""