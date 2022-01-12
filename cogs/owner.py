import asyncio
import contextlib
import discord
import io
import os
import random
import textwrap

from discord.ext import commands
from discord.ext.buttons import Paginator
from traceback import format_exception
import traceback
from utils.util import Pag
from utils.util import clean_code

description = "Owners Commands"


class Owner(commands.Cog, description=description):
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

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="test")
    @commands.check_any(perm_check(), is_me())
    async def test(self, ctx):
        await ctx.send(f"Ping `{round(self.bot.latency * 1000)}`ms")

    @commands.group(name="config", description="set Server config", invoke_without_command=True)
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(perm_check(), is_me())
    async def deleteprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")

    @config.command(
        name="welcome", description="Set welcome channel for server",)
    @commands.check_any(perm_check(), is_me())
    async def welcome(self, ctx, channel: discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Please use the `config` command frist")
        await self.bot.config.upsert({"_id": ctx.guild.id, "welcome": channel.id})
        await ctx.send("welcome channel Updated")

    @config.command(name="event", description="set event channel")
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(commands.has_any_role(799037944735727636, 785845265118265376, 803635405638991902), is_me())
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
    @commands.check_any(commands.has_any_role(799037944735727636, 785845265118265376), is_me())
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
    @commands.check_any(perm_check(), is_me())
    async def activity(self, ctx, *, activity):
        # This changes the bots 'activity'
        await self.bot.change_presence(activity=discord.Game(name=f"{activity}"), status=discord.Status.dnd)
        await ctx.send('Bot activity is Updated')

    @commands.command(name="Say", description="And classic say command", usage="[anything]")
    @commands.check_any(perm_check(), is_me())
    async def say(self, ctx, *, say):
        await ctx.message.delete()
        await ctx.send(f'{say}')

    @commands.command(
        name="logout",
        aliases=["disconnect", "stopbot"],
        description="disconnect Bot from discord",
        usage="",
        hidden=True
    )
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902), is_me())
    async def logout(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.bot.logout()

    @commands.command(name="toggle", description="Enable or disable a command!")
    @commands.check_any(perm_check(), is_me())
    async def toggle(self, ctx, *, command):
        command = self.bot.get_command(command)

        if command is None:
            await ctx.send("I can't find a command with that name!")

        elif ctx.command == command:
            await ctx.send("You cannot disable this command.")

        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send(f"I have {ternary} {command.qualified_name} for you!")

    @commands.command(name="nuke", description="Nuke The Channel", hidden=True)
    @commands.check_any(perm_check(), is_me())
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

    @commands.command(name="eval", description="Let Owner Run Code within bot", aliases=["exec"])
    @is_me()
    async def _eval(self, ctx, *, code):
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
            result = "".join(format_exception(e, e, e.__traceback__))

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```"
        )

        await pager.start(ctx)

    @commands.command(name="vsetup", hidden=True)
    @commands.check_any(perm_check(), is_me())
    async def vsetup(self, ctx):
        embed = discord.Embed(title="SERVER VERIFICATAON",
                              description="To unlock the Server find the Emoji Below and add your reaction if, if you still can't unlock the server please dm any online <@&799037944735727636>, <@&785845265118265376> to unlock server.",
                              color=0x2ECC71)
        message = await ctx.send(embed=embed)
        emoji = self.bot.get_emoji(843395086284357632)
        await message.add_reaction(emoji)

    @commands.command(
        name='reload', description="Reload all/one of the bots cogs!", usage="", hidden=True
    )
    @is_me()
    async def reload(self, ctx, cog=None):
        if not cog:
            # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=e,
                                inline=False
                            )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
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
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
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


def setup(bot):
    bot.add_cog(Owner(bot))
