import re
import datetime
from copy import deepcopy
from discord.ext.buttons import Paginator
import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta


# In cogs we make our own class
# for d.py which subclasses commands.Cog


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link','pls vote']

        messageContent = message.content
        if len(messageContent) > 0:
            for word.lower() in word_list:
                if word in messageContent:
                    return await message.reply('**Vote for us here**:\nhttps://top.gg/servers/785839283847954433/vote\n\n__**Voting Perks**__\n❥ Special "Voted" Role.\n❥ 2,500 Casino Cash. Collect using ,collectincome in #:game_die:。casino.\n❥ Access to 2x Amaari Channels, including Exclusive Chat and Dank Memer Premium.\n❥ Guild wide 1x Amaari.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild.id 
        channel =  self.bot.get_channel(785847439579676672)
        guild = self.bot.get_guild(785839283847954433)

        if member.guild.id == 785839283847954433:
            embed = discord.Embed(title=f'<a:celeyay:821818380406882315> WELCOME TO TGK {member.name} <a:celeyay:821818380406882315> ', color=0xff00ff)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name='Info Counter:', value='➻ Read our [Rules](https://discord.com/channels/785839283847954433/785841560918163501) \n ➻ Get your roles from :sparkles:[。self-roles](https://discord.com/channels/785839283847954433/785882615202316298/795729352062140537), and say Hi to everyone at :speech_balloon:[。general](https://discord.com/channels/785839283847954433/785847439579676672/817100365665009684)!', inline=False)
            embed.add_field(name='Server Games:', value='➻ To access specific sections, simply follow:\n◉ :frog:[。dank-bifröst](https://discord.com/channels/785839283847954433/801394407521517578/812654537873162261) for Dank Memer Channels\n◉ :dragon:[。poke-bifröst](https://discord.com/channels/785839283847954433/802195590208421908/802538839838556170) for Pokémon Channels\n◉ :game_die:[:。casino-bifrost](https://discord.com/channels/785839283847954433/804042634011738112/804051999879462982) for Casino Channels', inline=False)
            embed.add_field(name='Server Support', value='To get in touch with staff, simply Raise an ticket from 💌。[server-support](https://discord.com/channels/785839283847954433/785901543349551104/829248763646050324)', inline=False)
            embed.add_field(name='Server Member Count: ', value=f'{guild.member_count}', inline=False)
            embed.set_footer(text='Once again, a warm welcome. Have a great time!', icon_url=member.avatar_url)
            await channel.send(f'{member.mention}', embed=embed)

            #await member.send(embed=embed)
            #channel = get(guild.channels, name )
            #await channel.edit(name = f'Member Count: {guild.membe}')
        else:
            return

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