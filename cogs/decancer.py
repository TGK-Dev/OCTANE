import asyncio
import random
import re
import unicodedata
import discord
import stringcase
import unidecode
from datetime import datetime, timedelta
from discord.ext import commands

class Decancer(commands.Cog, description="Fix Member name on Join"):
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def is_cancerous(text: str) -> bool:
        for segment in text.split():
            for char in segment:
                if not (char.isascii() and char.isalnum()):
                    return True
        return False
    
    @staticmethod
    def strip_accs(text):
        try:
            text = unicodedata.normalize("NFKC", text)
            text = unicodedata.normalize("NFD", text)
            text = unidecode.unidecode(text)
            text = text.encode("ascii", "ignore")
            text = text.decode("utf-8")
        except Exception as e:
            print(e)
        return str(text)
    
    async def nick_maker(self, guild: discord.Guild, old_shit_nick):
        old_shit_nick = self.strip_accs(old_shit_nick)
        new_cool_nick = re.sub("[^a-zA-Z0-9 \n.]", "", old_shit_nick)
        new_cool_nick = " ".join(new_cool_nick.split())
        new_cool_nick = stringcase.lowercase(new_cool_nick)
        new_cool_nick = stringcase.titlecase(new_cool_nick)
        default_name = "Reqest new name"
        if len(new_cool_nick.replace(" ", "")) <= 1 or len(new_cool_nick) > 32:
            if default_name == "random":
                new_cool_nick = await self.get_random_nick(2)
            elif default_name:
                new_cool_nick = default_name
            else:
                new_cool_nick = "simp name"
        return new_cool_nick
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        guild: discord.Guild = member.guild
        old_nick: str = member.display_name

        if not self.is_cancerous(old_nick):
            return
        await asyncio.sleep(5)
        member = guild.get_member(member.id)

        if not member:
            return
        
        if member.top_role >= guild.me.top_role:
            return
        
        new_nick: str = await self.nick_maker(guild, old_nick)
        if old_nick.lower() != new_nick.lower():
            try:
                await member.edit(nick=new_nick, reason="Auto Decancer")
            except discord.NotFound:
                pass
            except discord.Forbidden:
                pass
    
    @commands.command(name="decancer-server", description="Decancer Server", usage="decancer-server")
    @commands.has_permissions(administrator=True)
    async def decancer_server(self, ctx):
        await ctx.send("Starting Decancer Server")        
        edited = 0
        channel = self.bot.get_channel(1007717533018759178)
        async with channel.typing():
            for member in ctx.guild.members:
                if member.bot:
                    continue
                old_nick: str = member.display_name
                if not self.is_cancerous(old_nick):
                    continue
                if member.top_role >= ctx.guild.me.top_role:
                    continue
                new_nick: str = await self.nick_maker(ctx.guild, old_nick)
                if old_nick.lower() != new_nick.lower():
                    try:
                        await member.edit(nick=new_nick, reason="Auto Decancer")
                        await channel.send(f"{member.mention} {old_nick} -> {new_nick}")
                    except discord.NotFound:
                        pass
                    except discord.Forbidden:
                        await channel.send(f"failed to edit {member.mention} {old_nick} -> {new_nick}")
        await ctx.send(f"{edited} members have been edited")

async def setup(bot):
    await bot.add_cog(Decancer(bot))