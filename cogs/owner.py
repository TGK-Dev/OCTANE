from discord.ext import commands
from discord import app_commands
from typing import Union, List
from utils.functions import make_db_temp
from utils.checks import Commands_Checks
from utils.functions import clean_code
from traceback import format_exception
from utils.paginator import Contex_Paginator
import discord
import io
import contextlib
import textwrap
import os
from io import BytesIO

class Owner(commands.Cog, name="Owner", description="Owner/admin commands."):
    def __init__(self, bot):
        self.bot = bot
    
    async def module_auto_complete(self, interaction: discord.Interaction, current:str) -> List[app_commands.Choice[str]]:
        _list =  [
            app_commands.Choice(name=module, value=module)
            for module in interaction.client.extensions if current.lower() in module.lower()
        ]
        return _list[:24]
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
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
        embed.add_field(name="Suggestion Channel", value=f"<#{guild_data['suggestion']}>")
        embed.add_field(name="Auto Roles", value=",".join([f"<@&{role}>" for role in guild_data['join_roles']]))
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    
    @config.command(name="Modlog", aliases=["ml", "modlog"], description="Set the mod log channel", brief="config modlog [channel]")
    @commands.has_guild_permissions(administrator=True)
    async def modlog(self, ctx, channel: discord.TextChannel):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
        
        guild_data['mod_log'] = channel.id
        await self.bot.config.upsert(guild_data)
        await ctx.send(f"{channel.mention} is now the mod log channel.")
    
    @config.command(name="joinr", aliases=["joinrole", "join-role"], description="Set the join role", brief="config joinr [role]")
    @commands.has_guild_permissions(administrator=True)
    async def joinr(self, ctx, role: discord.Role):
        guild_data = await self.bot.config.find(ctx.guild.id)

        if any(role.permissions.administrator, role.permissions.manage_guild, role.permissions.manage_channels, role.permissions.manage_roles, role.permissions.ban_members, role.permissions.kick_members, role.permissions.manage_messages):
            await ctx.send(f"{role.mention} is an staff role, please use a different role.")
            return

        if not guild_data:
            guild_data = make_db_temp(ctx.guild.id)
            await self.bot.config.insert(guild_data)

        if role.id not in guild_data['join_roles']:
            guild_data['join_roles'].append(role.id)
            await self.bot.config.update(guild_data)
            await ctx.send(f"{role.mention} is now the join role.", allowed_mentions=discord.AllowedMentions(roles=False))
        elif role.id in guild_data['join_roles']:
            guild_data['join_roles'].remove(role.id)
            await self.bot.config.update(guild_data)
            await ctx.send(f"{role.mention} is no longer the join role.", allowed_mentions=discord.AllowedMentions(roles=False))

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

    @app_commands.command(name="reload", description="Reload a cog")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(module=module_auto_complete)
    @app_commands.guilds(785839283847954433)
    async def reload(self, interaction: discord.Interaction, module: str):
        await interaction.response.send_message(embed=discord.Embed(description=f"Reloading module `{module}`...", color=discord.Color.green()))
        try:
            await self.bot.reload_extension(module)
            await interaction.edit_original_response(embed=discord.Embed(description=f"Successfully reloaded module `{module}`", color=discord.Color.green()))
        except Exception as e:
            await interaction.edit_original_response(content=None, embed=discord.Embed(description=f"Error while reloading module `{module}`: {e}", color=discord.Color.red()))

    @app_commands.command(name="get-logs", description="Get Logs of bot console")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(785839283847954433, 999551299286732871)
    async def get_logs(self, interaction: discord.Interaction):
        if interaction.user.id not in self.bot.owner_ids:
            await interaction.response.send_message("This Commands is only for the bot owner.", ephemeral=True)
            return
            
        await interaction.response.send_message(file=discord.File("./discord.log", filename="discord.log"))

async def setup(bot):
    await bot.add_cog(Owner(bot))

