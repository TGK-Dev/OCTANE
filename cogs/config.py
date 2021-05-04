import os
import random
import platform
import traceback
import utils.json_loader
import asyncio
import discord


from discord.ext import commands
from discord.ext.buttons import Paginator


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    async def ping(self, ctx):
        message = await ctx.send(f'Ping') 
        await message.edit(content=f"Ping `{round(self.bot.latency * 1000)}`ms")

    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
        description="Change your guilds prefix!",
        usage="prefix [New_prefix]",
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix="py."):
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @commands.command(
        name="deleteprefix", aliases=["dp"], description="Delete your guilds prefix!", usage="", hidden=True
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")

    @commands.command(
        name="blacklist", description="Blacklist a user from the bot", usage="<user>", hidden=True
    )
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx, user: discord.Member=None):
        user = user if user else ctx.author
        if user.id in [self.bot.user.id, ctx.author.id,488614633670967307, 488614633670967307]:
            return await ctx.send("Hey, you cannot blacklist yourself / bot/ Owner")

        blacklist = {
            '_id': user.id
        }

        await self.bot.blacklist.upsert(blacklist)

        current_blacklist_user = await self.bot.blacklist.get_all()
        for blacklisted_user in current_blacklist_user:
            self.bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

        embed = discord.Embed(description=f"The User {user.mention} is now blacklisted")
        await ctx.send(embed=embed)
        
    @commands.command(
        name="unblacklist",
        description="Unblacklist a user from the bot",
        usage="<user>",
        hidden=True
    )
    @commands.has_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        """
        Unblacklist someone from the bot
        """
        blacklist = {'_id': user.id}

        await self.bot.blacklist.delete_by_custom(blacklist)

        current_blacklist_user = await self.bot.blacklist.get_all()
        for blacklisted_user in current_blacklist_user:
            self.bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

        try:
            self.bot.blacklist_user.pop(user.id)
        except KeyError:
            pass

        embed = discord.Embed(description=f"The User {user.mention} is now unblacklisted")
        await ctx.send(embed=embed)

    @commands.command(name="activity", description="Change Bot activity", usage="[activity]", hidden=True)
    @commands.has_permissions(administrator=True)
    async def activity(self, ctx, *, activity): 
        await self.bot.change_presence(activity=discord.Game(name=f"{activity}"), status=discord.Status.dnd) # This changes the bots 'activity'
        await ctx.send('Bot activity is Updated')

    @commands.command(name="Status", description="Change Bot Status to online & Dnd & idle", usage="[dnd & idle & online]", hidden=True)
    @commands.has_permissions(administrator=True)
    async def status(self,ctx, arg):
        if arg.lower() == 'dnd':
            await self.client.change_presence(status=discord.Status.dnd)
            await ctx.send('Bot status is Updated')
        elif arg.lower() == 'online':
            await self.client.change_presence(status=discord.Status.online)
            await ctx.send('Bot status is Updated')
        elif arg.lower() == 'idle' :
            await self.client.change_presence(status=discord.Status.idle)
            await ctx.send('Bot status is Updated')
        else: 
            await ctx.send(f':warning: {ctx.author.mention} Please provide valid status you dimwit!! :warning:')

    @commands.command(
        name="logout",
        aliases=["disconnect","stopbot"],
        description="Log the bot out of discord! Owner role only",
        usage="",
        hidden=True
    )
    @commands.has_role(785842380565774368)
    async def logout(self, ctx):
        """
        If the user running the command owns the bot then this will disconnect the bot from discord.
        """
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.bot.logout()

    @commands.command(name="Say", description="And classic say command", usage="[anything]", hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def say(self,ctx, *, say):
        await ctx.message.delete()
        await ctx.send(f'{say}')

    @commands.command(
        name="stats", description="A useful command that displays bot statistics.", usage="stats"
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version:", value=self.bot.version)
        embed.add_field(name="Python Version:", value=pythonVersion)
        embed.add_field(name="Discord.Py Version", value=dpyVersion)
        embed.add_field(name="Total Guilds:", value=serverCount)
        embed.add_field(name="Total Users:", value=memberCount)
        embed.add_field(name="Bot Developers:", value="<@488614633670967307>\n<@301657045248114690>")

        embed.set_footer(text=f"Carpe Noctem | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="toggle", description="Enable or disable a command!", hidden=True)
    @commands.has_role(785842380565774368)
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

    @commands.command(name="nuke", hidden=True)
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel
        try:
            await ctx.send("are you Sure [Y/N]")
            await self.bot.wait_for("message", check=lambda m: m.content.startswith("Y") or m.content.startswith("y"), timeout=60)
            embed_delete = discord.Embed(description="` Nuking Channel in 10s Type>fstop/>fs to cancel`")
            await ctx.send(embed=embed_delete)
            try:
                await self.bot.wait_for("message",check=lambda m: m.content.startswith(">fstop") or m.content.startswith(">fs"), timeout=10)
                embed = discord.Embed(description="`canceling the command`")
                return await ctx.send(embed=embed)
            except asyncio.TimeoutError:
                    nuke_channel = discord.utils.get(ctx.guild.channels, name=channel.name)
                    new_channel = await nuke_channel.clone(reason="Has been Nuked!")
                    await nuke_channel.delete()
                    await new_channel.send("THIS CHANNEL HAS BEEN NUKED!\n https://tenor.com/view/nuke-bomb-deaf-dool-explode-gif-14424973")
                    await ctx.send("Nuked the Channel sucessfully!")
        except asyncio.TimeoutError:
            embed = discord.Embed(description="`Time out canceling the command`")
            await ctx.send(embed=embed)


    @commands.command(
        name='reload', description="Reload all/one of the bots cogs!", usage="", hidden=True
    )
    @commands.has_permissions(administrator=True)
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
    bot.add_cog(Config(bot))
