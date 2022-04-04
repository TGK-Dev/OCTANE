import discord
import time
import platform
import datetime
from humanfriendly import format_timespan
from discord.ext import commands
from utils.checks import checks

description = "Some Basic commands"

class April_FOOl(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Mystery Button", style=discord.ButtonStyle.green, custom_id="mystery")
    async def mystery_button(self, button: discord.Button, interaction: discord.Interaction):
        data = await self.bot.april.find(interaction.user.id)
        await interaction.response.defer(thinking=True, ephemeral=True)
        if data:
            return await interaction.followup.send(f"You have already Clicked the Mystery Button")
        last_name = interaction.user.display_name
        try:
            await interaction.user.edit(nick=interaction.user.name [::-1])
        except:
            return await interaction.followup.send("Missing Permissions", ephemeral=True)
        await interaction.followup.send("Something happened", ephemeral=True)
        await self.bot.april.upsert({"_id": interaction.user.id, "last_name": last_name})
        await self.bot.get_channel(959157972985081856).send(f"{interaction.user.mention} Clicked the Mystery Button")
        
class Basic(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(April_FOOl(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.command()
    @commands.check(checks.is_me())
    async def april(self, ctx):
        await ctx.send("An Random Button has appeared, who have power to click it", view=April_FOOl(self.bot))

    @commands.command()
    async def ping(self, ctx):
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        start = self.bot.uptime
        now = datetime.datetime.utcnow()
        newtime = (now - start)
        total_s = newtime.total_seconds()

        dstart = datetime.datetime.utcnow()
        await self.bot.config.find(ctx.guild.id)
        dend = datetime.datetime.utcnow()
        dping = (dend - dstart)
        dping = dping.total_seconds()

        embed = discord.Embed(title="Pingss", color=ctx.author.colour,
                              description=f"**Response TIme** {round(self.bot.latency * 1000)}ms\n**API**: {round((end_time - start_time) * 1000)}ms\n**Database Ping**: {round(dping * 1000)}Ms\n**My Age**: {format_timespan(total_s)}")

        await message.edit(content=None, embed=embed)

    @commands.command(
        name="stats", description="A useful command that displays bot statistics.", usage="stats"
    )
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = discord.Embed(
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version:", value=self.bot.version)
        embed.add_field(name="Python Version:", value=pythonVersion)
        embed.add_field(name="Discord.py Version", value=dpyVersion)
        embed.add_field(name="Total Guilds:", value=serverCount)
        embed.add_field(name="Total Users:", value=memberCount)
        embed.add_field(name="Total Commands:", value=len(list(self.bot.commands)))
        embed.add_field(name="Bot Developers:",
                        value="<@488614633670967307>\n<@301657045248114690>")
        embed.add_field(name="Embed Format:",
                        value="<@413651113485533194>\n<@651711446081601545>")

        embed.set_footer(
            text=f"Developed by Jay & Utik007 | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        if message.content.startswith(">") or message.content.startswith('?'): return
        self.bot.snipe[message.channel.id] = {'message': message.content, 'author': message.author.id}

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: return
        if before.content.startswith(">") or before.content.startswith('?'): return
        self.bot.esnipe[before.channel.id] = {'message': before.content, 'author': before.author.id, 'after': after.content}

    @commands.command(name="esnipe", aliases=["es"])
    @commands.check_any(checks.can_use())
    async def esnipe(self, ctx):
        data = self.bot.esnipe.get(ctx.channel.id)
        if data is None:
            await ctx.send("there is nothing to snipe")
            return
        user = ctx.guild.get_member(data['author'])
        if user is None:
            user = await ctx.guild.fetch_member(data['author'])

        embed = discord.Embed(description=f"**Before:** {data['message']}\n**After:** {data['after']}", color=user.colour)
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"Sniped by: {ctx.author}")
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="snipe", aliases=["s"])
    @commands.check_any(checks.can_use())
    async def snipe(self, ctx):
        data = self.bot.snipe.get(ctx.channel.id)
        if data is None:
            await ctx.send("there is nothing to snipe")
            return
        user = ctx.guild.get_member(data['author'])
        if user is None:
            user = await ctx.guild.fetch_member(data['author'])
        embed = discord.Embed(description=data['message'], color=user.colour)
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"Sniped by: {ctx.author}")
        await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Basic(bot))
