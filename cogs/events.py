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
        self.member_task = self.check_current_mambers.start()

    def cog_unload(self):
        self.member_task.cancel()

    @tasks.loop(seconds=10)
    async def check_current_mambers(self):
        #guild = self.bot.get_guild(785839283847954433)
        #total = discord.utils.get(guild.voice_channels, id=821747329316290560)
        #human = discord.utils.get(guild.voice_channels, id=821747332327931995)
        #robot = discord.utils.get(guild.roles, id=810153515610537994)
        temp = self.bot.get_channel(830493297407164426)
        count = 0
        #await total.edit(name=f"💪。Total: {len(guild.member_count)}")

        #await human.edit(name=f"😊。Humans: {len(guild.member_count) - len(robot)}")
        await temp.send(f"{count + 1}")

    @check_current_mambers.before_loop
    async def before_check_current_mambers(self):
        await self.bot_wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link', 'vote Link', 'Vote link', 'Vote Link']

        messageContent = message.content
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    return await message.reply('Please Vote us here, <https://top.gg/servers/785839283847954433/vote>, Thanks For Support ^0^', )

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
            await ctx.message.reply('Member not Found')
        elif isinstance(error, commands.UserNotFound):
            await ctx.message.reply('User not Found')
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.message.reply('Channel Not Found')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.message.reply('Role Not Found')
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.message.reply(f'The {name} is Already Loaded')
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.message.reply(f'The {name} is Already UnLoaded')
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.message.reply(f'The Extension not Found')
        else:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
