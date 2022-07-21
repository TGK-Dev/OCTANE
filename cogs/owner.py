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

    async def cog_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_cogs = []
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                current_cogs.append(file[:-3])
        new_options = [app_commands.Choice(name="reload all cogs", value="*")]
        for cog in current_cogs:
            new_options.append(app_commands.Choice(name=cog, value=cog))
        return new_options[:24]


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
        elif user.id in [self.bot.user.id ,ctx.guild.owner.id, ctx.author.id ,self.bot.owner_id]:
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
        embed.add_field(name="Suggestion Channel", value=f"<#{guild_data['suggestion']}>")
        embed.add_field(name="Auto Roles", value=",".join([f"<@&{role}>" for role in guild_data['join_roles']]))
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
    
    @config.command(name="qurantine", aliases=["q"], description="Toggle Verification system", brief="config qurantine [on/off]")
    @commands.has_guild_permissions(administrator=True)
    async def qurantine(self, ctx, state: str):
        if state.lower() not in ['on', 'off', 'true', 'false', 'enable', 'disable', 'yes', 'no', '1', '0', 'y', 'n']:
            await ctx.send("Please use `on` or `off`.")
            return

        data = await self.bot.config.find(ctx.guild.id)
        if not data:
            data = make_db_temp(ctx.guild.id)
            await self.bot.config.insert(data)
        
        if state.lower() in ['on', 'true', 'enable', 'yes', '1', 'y']:
            data['qurantine'] = True
            await self.bot.config.update(data)
            await ctx.send("Verification is now enabled.")
        elif state.lower() in ['off', 'false', 'disable', 'no', '0', 'n']:
            data['qurantine'] = False
            await self.bot.config.update(data)
            await ctx.send("Verification is now disabled.")
        else:
            await ctx.send("Please Enter Valid Input.")

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
    @app_commands.autocomplete(cog=cog_autocomplete)
    @app_commands.guilds(785839283847954433)
    async def reload(self, interaction: discord.Interaction, cog: str):
        if cog != "*":
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                await self.bot.load_extension(f"cogs.{cog}")
                embed = discord.Embed(description=f"{cog} has been reloaded.", color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                embed = discord.Embed(description="Error | {}".format(e), color=0xFF0000)
                await interaction.response.send_message(embed=embed)
                return
        elif cog == "*":
            await interaction.response.defer(thinking=True)
            embed = discord.Embed(description="Reloading all cogs...", color=discord.Color.green())
            for module in os.listdir("./cogs"):
                if module.endswith(".py") and not module.startswith("_"):
                    try:
                        await self.bot.unload_extension(f"cogs.{module[:-3]}")
                        await self.bot.load_extension(f"cogs.{module[:-3]}")
                        embed.add_field(name=module, value="Reloaded", inline=False)
                    except Exception as e:
                        error = "".join(format_exception(e,e,e.__traceback__))
                        embed.add_field(name=f"{module}", value=f"Failure | {error[:100]}", inline=False)
            await interaction.followup.send(embed=embed)


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

