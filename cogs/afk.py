import discord
import datetime
from copy import deepcopy
from discord.ext import commands
import re
from cogs.v2moderation import roles
from utils.checks import checks

pc_mention_regex = re.compile("(@)(!|&)(\d\d\d)")
mo_mention_regex = re.compile("<(@)")


class Afk(commands.Cog, description="An Afk commands"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} is ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        afks = deepcopy(self.bot.afk_user)

        if message.author.id in afks:

            try:
                self.bot.afk_user.pop(message.author.id)
            except KeyError:
                pass

            await message.reply("your AFK status has been Removed", mention_author=False, delete_after=30)
            data = await self.bot.afk.find(message.author.id)
            try:
                await message.author.edit(nick=f"{data['last_name']}")
            except:
                pass

            await self.bot.afk.delete(message.author.id)

            try:
                self.bot.afk_user.pop(message.author.id)
            except KeyError:
                return

        if type(message.reference) == None:
            pass
        else:
            try:
                msg = await message.channel.fetch_message(int(message.reference.message_id))
                for key, value in afks.items():
                    user = await message.guild.fetch_member(value['_id'])
                    if msg.author.id == user.id:
                        time = round(value['time'].timestamp())
                        return await message.reply(f"{user.display_name} is afk {value['message']} -<t:{time}:R> <t:{time}:f>", mention_author=False, delete_after=30, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
            except:
                pass
        if len(message.mentions) == 0:
            return
        else:
            for key, value in afks.items():
                user = await message.guild.fetch_member(value['_id'])
                if user in message.mentions:
                    time = round(value['time'].timestamp())
                    await message.reply(f"{user.display_name} is afk {value['message']} -<t:{time}:R> <t:{time}:f>", mention_author=False, delete_after=30, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.command(name="afk", description="set your status afk with this command")
    @commands.check_any(checks.is_me(), checks.can_use())
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def afk(self, ctx, *, message=None):
        message = message if message else ""

        data = {'_id': ctx.author.id,
                'message': message,
                'last_name': ctx.author.display_name,
                'time': datetime.datetime.now()}
        try:
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
        except:
            pass
        await ctx.send("I have set your status as afk")
        await self.bot.afk.upsert(data)
        self.bot.afk_user[ctx.author.id] = data

    @commands.command(name="afkreset", description="Remove any user afk message")
    @commands.check_any(checks.can_use())
    async def afkreset(self, ctx, user: discord.Member):
        data = await self.bot.afk.find(user.id)
        if data is None:
            return await ctx.send("No data Found, check your id")
        data['message'] = "⠀"
        await self.bot.afk.upsert(data)
        try:
            self.bot.afk_user.pop(user.id)
        except KeyError:
            pass
        self.bot.afk_user[user.id] = data
        await ctx.send("User Afk message has been reset")


def setup(bot):
    bot.add_cog(Afk(bot))
