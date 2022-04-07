import asyncio
import contextlib
from dis import disco
import re
import discord
import io
import os
import textwrap

from discord.ext import commands
import traceback
from utils.checks import checks
from typing import Union
from discord import app_commands
from utils.util import clean_code
from traceback import format_exception
from paginator import Paginator
from Views.Cogs import Cog_select
description = "Owners Commands"

def is_me(interaction: discord.Interaction):
    return interaction.user.id in [488614633670967307, 301657045248114690]
    
class Owner(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot
        self.load_app_command()

    def load_app_command(self):

        @app_commands.context_menu(name="eval")
        async def eval_(interaction: discord.Interaction, message: discord.Message):
            if interaction.user.id not in [488614633670967307, 301657045248114690]: 
                return await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)

            code = clean_code(message.content)
            local_variables = {
                "discord": discord,
                "commands": commands,
                "bot": self.bot,
                "ctx": interaction,
                "channel": interaction.channel,
                "author": interaction.user,
                "guild": interaction.guild,
                "message": interaction.message
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
                page.append(discord.Embed(description=f'```py\n{result[i:i + 2000]}\n```', color=interaction.user.color))

            await Paginator(interaction, page).start(embeded=True, quick_navigation=False)

        self.bot.slash_commands.append(eval_)


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.group(name="config", description="set Server config", invoke_without_command=True)
    @commands.check_any(checks.can_use())
    async def config(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)

        if data is None:
            data = {"_id": ctx.guild.id, "prefix": "!", "case": 0,
                    "welcome": None, "event": None, "lockdown_channels": []}

            await self.bot.config.upsert(data)
            return await ctx.send("Server config Setup Done, now use the `help config` command")
        else:
            await ctx.send("config set is Done")

    @config.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
        description="Change your guilds prefix!",
        usage="prefix [New_prefix]",
    )
    @commands.check_any(checks.can_use())
    async def prefix(self, ctx, *, prefix):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Please use the `config` command frist")
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @config.command(
        name="deleteprefix", aliases=["dp"], description="Delete your guilds prefix!", usage="")
    @commands.check_any(checks.can_use())
    async def deleteprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")

    @config.command(
        name="welcome", description="Set welcome channel for server",)
    @commands.check_any(checks.can_use())
    async def welcome(self, ctx, channel: discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Please use the `config` command frist")
        await self.bot.config.upsert({"_id": ctx.guild.id, "welcome": channel.id})
        await ctx.send("welcome channel Updated")

    @config.command(name="event", description="set event channel")
    @commands.check_any(checks.can_use())
    async def event(self, ctx, channel: discord.TextChannel):
        data = self.bot.config.find(ctx.guil.id)
        if data is None:
            return await ctx.send("Please use the `config` command frist")
        await self.bot.upsert({"_id": ctx.guild.id, "event": channel.id})
        await ctx.send("welcome channel Updated")

    @commands.command(
        name="blacklist",
        description="blacklist user from the bot",
        usage="<user>",
    )
    @commands.check_any(checks.is_me())
    async def blacklist(self, ctx, user: discord.Member):
        if user.id in [self.bot.user.id, ctx.author.id, 488614633670967307, 488614633670967307]:
            return await ctx.send("Hey, you cannot blacklist yourself / bot/ Owner")

        data = await self.bot.config.find(ctx.guild.id)
        if data:
            if user.id in data['blacklist']:
                return await ctx.send("User is allready blacklisted")
            else:
                data['blacklist'].append(user.id)

            await self.bot.config.upsert(data)

            current_blacklist_user = await self.bot.config.find(785839283847954433)
            for blacklisted_user in current_blacklist_user['blacklist']:
                self.blacklist_users.append(blacklisted_user)

            embed = discord.Embed(
                description=f"The User {user.mention} is now blacklisted")
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            embed = discord.Embed(description=f"The User {user.mention} is already Blacklisted")
            await ctx.send(embed=embed)

    @commands.command(
        name="unblacklist",
        description="Unblacklist a user from the bot",
        usage="<user>"
    )
    @commands.check_any(checks.is_me())
    async def unblacklist(self, ctx, user: discord.Member):
        """
        Unblacklist someone from the bot
        """
        data = await self.bot.config.find(ctx.guild.id)
        if data:
            if user.id in data['blacklist']:
                data['blacklist'].remove(user.id)
            else:
                return await ctx.send("User is not blacklisted")
                
            await self.bot.config.upsert(data)

            current_blacklist_user = await self.bot.config.find(785839283847954433)
            for blacklisted_user in current_blacklist_user['blacklist']:
                self.blacklist_users.append(blacklisted_user)

            embed = discord.Embed(
                description=f"The User {user.mention} is now blacklisted")
            await ctx.send(embed=embed)
            await ctx.message.delete()
        else:
            embed = discord.Embed(description=f"The User {user.mention} is already Blacklisted")
            await ctx.send(embed=embed)

    @commands.command(name="activity", description="Change Bot activity", usage="[activity]")
    @commands.check_any(checks.is_me())
    async def activity(self, ctx, *, activity):
        # This changes the bots 'activity'
        await self.bot.change_presence(activity=discord.Game(name=f"{activity}"), status=discord.Status.dnd)
        await ctx.send('Bot activity is Updated')

    @commands.command(
        name="logout",
        aliases=["disconnect", "stopbot"],
        description="disconnect Bot from discord",
        usage="",
        hidden=True
    )
    @commands.check_any(checks.is_me())
    async def logout(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.bot.close()

    @commands.command(name="toggle", description="Enable or disable a command!")
    @commands.check_any(checks.can_use(), commands.has_any_role(799037944735727636, 803635405638991902))
    async def toggle(self, ctx, *, command):
        command = self.bot.get_command(command)

        if command is None or command == ctx.command:
            return await ctx.send("Invalid Command")
        
        cmd_data = await self.bot.active_cmd.find(command.name)
        if not cmd_data: return await ctx.send("no data found ping Jay Fast")
        
        if cmd_data['disable'] == True:
            cmd_data['disable'] = False
            await ctx.send(f"{command.name} Is Now Enable")
            return await self.bot.active_cmd.upsert(cmd_data)

        if cmd_data['disable'] == False:
            cmd_data['disable'] = True
            await ctx.send(f"{command.name} Is Now disabled")
            return await self.bot.active_cmd.upsert(cmd_data)

    @commands.command(name="nuke", description="Nuke The Channel", hidden=True)
    @commands.check_any(checks.can_use())
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel
        try:
            await ctx.send("are you Sure [Y/N]")
            await self.bot.wait_for("message", check=lambda m: m.content.startswith("Y") or m.content.startswith("y"), timeout=60)
            embed_delete = discord.Embed(
                description="` Nuking Channel in 10s Type>fstop/>fs to cancel`")
            await ctx.send(embed=embed_delete)
            try:
                await self.bot.wait_for("message", check=lambda m: m.content.startswith(">fstop") or m.content.startswith(">fs"), timeout=10)
                embed = discord.Embed(description="`canceling the command`")
                return await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                nuke_channel = discord.utils.get(
                    ctx.guild.channels, name=channel.name)
                new_channel = await nuke_channel.clone(reason="Has been Nuked!")
                await nuke_channel.delete()
                await new_channel.send("THIS CHANNEL HAS BEEN NUKED!\n https://tenor.com/view/nuke-bomb-deaf-dool-explode-gif-14424973")
                await ctx.send("Nuked the Channel sucessfully!")
        except asyncio.TimeoutError:
            embed = discord.Embed(
                description="`Time out canceling the command`")
            await ctx.send(embed=embed)

    # @commands.command(
    #     name='reload', description="Reload all/one of the bots cogs!", usage="", hidden=True
    # )
    # @commands.check_any(checks.is_me())
    # async def reload(self, ctx, cog=None):
    #     if not cog:
    #         # No cog, means we reload all cogs
    #         async with ctx.typing():
    #             embed = discord.Embed(
    #                 title="Reloading all cogs!",
    #                 color=0x808080,
    #                 timestamp=ctx.message.created_at
    #             )
    #             for ext in os.listdir("./cogs/"):
    #                 if ext.endswith(".py") and not ext.startswith("_"):
    #                     try:
    #                         await self.bot.unload_extension(f"cogs.{ext[:-3]}")
    #                         await self.bot.load_extension(f"cogs.{ext[:-3]}")
    #                         embed.add_field(
    #                             name=f"Reloaded: `{ext}`",
    #                             value='\uFEFF',
    #                             inline=False
    #                         )
    #                     except Exception as e:
    #                         embed.add_field(
    #                             name=f"Failed to reload: `{ext}`",
    #                             value=e,
    #                             inline=False
    #                         )
    #                     await asyncio.sleep(0.5)
    #             await ctx.send(embed=embed)
    #     else:
    #         # reload the specific cog
    #         async with ctx.typing():
    #             embed = discord.Embed(
    #                 title="Reloading all cogs!",
    #                 color=0x808080,
    #                 timestamp=ctx.message.created_at
    #             )
    #             ext = f"{cog.lower()}.py"
    #             if not os.path.exists(f"./cogs/{ext}"):
    #                 # if the file does not exist
    #                 embed.add_field(
    #                     name=f"Failed to reload: `{ext}`",
    #                     value="This cog does not exist.",
    #                     inline=False
    #                 )

    #             elif ext.endswith(".py") and not ext.startswith("_"):
    #                 try:
    #                     await self.bot.unload_extension(f"cogs.{ext[:-3]}")
    #                     await self.bot.load_extension(f"cogs.{ext[:-3]}")
    #                     embed.add_field(
    #                         name=f"Reloaded: `{ext}`",
    #                         value='\uFEFF',
    #                         inline=False
    #                     )
    #                 except Exception:
    #                     desired_trace = traceback.format_exc()
    #                     embed.add_field(
    #                         name=f"Failed to reload: `{ext}`",
    #                         value=desired_trace,
    #                         inline=False
    #                     )
    #             await ctx.send(embed=embed)
    
    @commands.command(name="reload", description="Reload all/one of the bots cogs!", usage=None, hidden=True)
    @commands.check_any(checks.is_me())
    async def reload(self, ctx, cog=None):
        if cog:
            async with ctx.typing():
                embed = discord.Embed(
                    title=f"Reloading {cog}!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        await self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        await self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)
        else:
            await ctx.send("Select Your Cog from Dropdown", view=Cog_select(self.bot, ctx))


    @commands.group(name="permission", description="Edit permmsion for any command", aliases=['perm'], invoke_without_command=True)
    @commands.check_any(checks.can_use(),commands.has_any_role(785842380565774368, 803635405638991902,799037944735727636))
    async def permission(self, ctx):
        await ctx.send("Looks like you forgot to add sub-command")

    @permission.command()
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902,799037944735727636, 488614633670967307), checks.is_me())
    async def check(self, ctx, target: Union[discord.Role, str]):
        if type(target) == str:
            
            command = self.bot.get_command(target)
            if command is None: return await ctx.send("I can't find a command with that name!")

            cmd_data = await self.bot.active_cmd.find(command.name)
            if not cmd_data:return await ctx.send("NO data found")

            embed = discord.Embed(title=f"permission {command.name}",color=ctx.author.color)
            roles,users = [], []

            for role in cmd_data['allowed_roles']: 
                roles.append(f"<@&{role}>")
            if len(roles) == 0: 
                embed.add_field(name="Allowed roles", value="None")
            else: 
                embed.add_field(name="Allowed roles", value=", ".join(roles))

            embed.add_field(name="Disabed?:", value=cmd_data['disable'], inline=False)
            await ctx.send(embed=embed)

        if type(target) == discord.Role:
            cmd_data = await self.bot.active_cmd.get_all()
            if not cmd_data:return await ctx.send("NO data found")

            embed = discord.Embed(description=f"***Permission's  {target.mention}***",color=ctx.author.color)
            allowed_list = " "
            for cmd in cmd_data:
                if target.id in cmd['allowed_roles']: 
                    allowed_list += f"{cmd['_id']}, "
            
            if allowed_list != " ":
                embed.add_field(name="Allowed commands", value=allowed_list)
            else:
                embed.add_field(name="Allowed commands", value="None")

            await ctx.send(embed=embed)
        
    @permission.command(name="add")
    @commands.check_any(checks.can_use(),commands.has_any_role(785842380565774368, 803635405638991902,799037944735727636))
    async def add(self, ctx, command, *targets: discord.Role):

        targets = [int(target.id) for target in targets]

        command = self.bot.get_command(command)
        if command is None: return await ctx.send("I can't find a command with that name!")
        elif ctx.command == command: return await ctx.send("You cannot edit perm for this command")
        
        data = await self.bot.active_cmd.find(command.name)
        if not data:
            data = {"_id": command.name, "allowed_roles": [], 'allowed_users': [],"disable": False}

        for target in targets:
            if target in data['allowed_roles']:
                pass
            else:
                data['allowed_roles'].append(target)
                

        # elif type(target) == discord.Member:
        #     if target.id in data['allowed_users']:
        #         return await ctx.send(f"{target.mention} had no permission to use this command {command.name}", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        #     else:
        #         data['allowed_users'].remove(target.id)

        await self.bot.active_cmd.upsert(data)
        await ctx.send(f"permission of {command.name} is Updated", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        self.bot.perm[command.name] = data
    
    @permission.command(name="remove")
    @commands.check_any(checks.can_use(),commands.has_any_role(785842380565774368, 803635405638991902,799037944735727636))
    async def remove(self, ctx, command, *targets: str.split(' ')):
        targets = [int(target.id) for target in targets]

        command = self.bot.get_command(command)
        if command is None: return await ctx.send("I can't find a command with that name!")
        elif ctx.command == command: return await ctx.send("You cannot edit perm for this command")
        
        data = await self.bot.active_cmd.find(command.name)
        if not data:return await ctx.send("NO data found")

        for target in targets:
            if target in data['allowed_roles']:
                data['allowed_roles'].remove(target)
                

        # elif type(target) == discord.Member:
        #     if target.id in data['allowed_users']:
        #         return await ctx.send(f"{target.mention} had no permission to use this command {command.name}", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        #     else:
        #         data['allowed_users'].remove(target.id)

        await self.bot.active_cmd.upsert(data)
        await ctx.send(f"permission of {command.name} is Updated", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        self.bot.perm[command.name] = data

async def setup(bot):
    await bot.add_cog(Owner(bot))
