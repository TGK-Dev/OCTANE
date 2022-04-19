from discord.ext import commands
from discord import app_commands
from typing import Union
from utils.functions import make_db_temp
from utils.checks import Commands_Checks
from utils.functions import clean_code
from traceback import format_exception
from utils.paginator import Contex_Paginator
import discord
import io
import contextlib
import textwrap


class Owner(commands.Cog, name="Owner", description="Owner/admin commands."):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="Blacklist", aliases=["bl"], description="Blacklist a user from using the bot", brief="blacklist [user]")
    @commands.is_owner()
    async def blacklist(self, ctx, user: Union[discord.Member, discord.User]):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
        
        if user.id in guild_data['blacklist']:
            await ctx.send(f"{user.mention} is already blacklisted.")
        elif user.id == self.bot.user.id or ctx.guild.owner.id == user.id or user.id == ctx.author.id or user.id == self.bot.owner_id:
            await ctx.send(f"You can't blacklist that user.")
        else:
            guild_data['blacklist'].append(user.id)
            await self.bot.config.upsert(guild_data)
            await ctx.send(f"{user.mention} has been blacklisted.")
    
    @commands.command(name="Unblacklist", aliases=["ubl"], description="Unblacklist a user from using the bot", brief="unblacklist [user]")
    @commands.is_owner()
    async def unblacklist(self, ctx, user: Union[discord.Member, discord.User]):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
        
        if user.id not in guild_data['blacklist']:
            await ctx.send(f"{user.mention} is not blacklisted.")
        else:
            guild_data['blacklist'].remove(user.id)
            await self.bot.config.upsert(guild_data)
            await ctx.send(f"{user.mention} has been unblacklisted.")
    
    @commands.group(name="Configuration", invoke_without_command=True, description="Configure the bot", brief="config [command]", aliases=["config"])
    @commands.has_guild_permissions(administrator=True)
    async def config(self, ctx):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
            await self.bot.config.upsert(guild_data)
            await ctx.send(f"{ctx.guild.name} has been added to the database.\nPlease use `config help` to see the available commands.")
            return
        
        embed = discord.Embed(title=f"{ctx.guild.name}'s Config", color=0x00ff00)
        embed.add_field(name="Welcome Message", value=f"<#{guild_data['welcome']}>")
        embed.add_field(name="Mod Log Channel", value=f"<#{guild_data['mod_log']}>")
        embed.add_field(name="Case Number", value=f"{guild_data['case']}")
        embed.add_field(name="Starboard Channel", value=f"<#{guild_data['starboard']['channel']}>\nThreshold: {guild_data['starboard']['threshold']}\nSelf Star: {guild_data['starboard']['self_star']}\nToggle: {guild_data['starboard']['toggle']}")
        embed.add_field(name="Suggestion Channel", value=f"<#{guild_data['suggestion_channel']}>")
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    
    @config.command(name="Welcome", aliases=["w", "welcome"], description="Set the welcome channel", brief="config welcome [channel]")
    @commands.has_guild_permissions(administrator=True)
    async def welcome(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel]):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
        
        guild_data['welcome'] = channel.id
        await self.bot.config.upsert(guild_data)
        await ctx.send(f"{channel.mention} is now the welcome channel.")
    
    @config.command(name="Modlog", aliases=["ml", "modlog"], description="Set the mod log channel", brief="config modlog [channel]")
    @commands.has_guild_permissions(administrator=True)
    async def modlog(self, ctx, channel: discord.TextChannel):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
        
        guild_data['mod_log'] = channel.id
        await self.bot.config.upsert(guild_data)
        await ctx.send(f"{channel.mention} is now the mod log channel.")
    
    @config.command(name="Suggestion", aliases=["suggestion", "guggest"], description="Set the suggestion channel", brief="config suggestion [channel]")
    @commands.has_guild_permissions(administrator=True)
    async def suggestion(self, ctx, channel: discord.TextChannel):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)

        guild_data['suggestion'] = channel.id
        await self.bot.config.upsert(guild_data)
        await ctx.send(f"{channel.mention} is now the suggestion channel.")
    
    @commands.command(name="eval", description="Evaluate a code", brief="eval [code]", hidden=True)
    @commands.check_any(Commands_Checks.is_me())
    async def _eval(self, ctx, *,code):
        code = clean_code(code)
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):

                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )
                obj = await local_variables["func"]()

                result = f"{stdout.getvalue()}\n-- {obj}\n"
                
        except Exception as e:
            result = "".join(format_exception(e,e,e.__traceback__))
        page = []
        for i in range(0, len(result), 2000):
            page.append(discord.Embed(description=f'```py\n{result[i:i + 2000]}\n```', color=ctx.author.color))
        
        await Contex_Paginator(ctx, page).start(embeded=True, quick_navigation=False)


async def setup(bot):
    await bot.add_cog(Owner(bot))

