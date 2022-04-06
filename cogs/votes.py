#make discord py cog name votes
import discord
from discord.ext import commands, tasks
from copy import deepcopy
import datetime
import requests
from humanfriendly import format_timespan
from discord import app_commands
from utils.Slash_check import can_bypass_cd
class Votes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.load_tree_commands()
        self.vote_task = self.check_current_votes.start()
    
    def cog_unload(self):
        self.vote_task.cancel()
    

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @tasks.loop(seconds=5)
    async def check_current_votes(self):
        currentTime = datetime.datetime.now()
        votes = deepcopy(self.bot.current_vote)
        for key, value in votes.items():

            if value['reminded'] == True:
                continue
            
            expired_time = value['last_vote'] + datetime.timedelta(hours=12)

            if currentTime >= expired_time:
                            
                self.bot.dispatch("vote_expired", value)
                try:
                    self.bot.current_vote.pop(key)
                except KeyError:
                    pass

    @commands.Cog.listener()
    async def on_vote_expired(self, data: dict):
        if data['reminded'] == True: return
        embed = discord.Embed(title="You are able to vote again!",description="Your vote is ready at top.gg:", color=0xE74C3C)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Top.gg', url="https://top.gg/servers/785839283847954433/vote"))

        guild = self.bot.get_guild(785839283847954433)
        member = guild.get_member(data['_id'])
        if member is None:
            return await self.bot.votes.delete(data['_id'])
        await member.remove_roles(guild.get_role(786884615192313866))
        data['reminded'] = True
        await self.bot.votes.upsert(data)
        try:
            await member.send(embed=embed, view=view)
        except discord.HTTPException:
            pass

    @app_commands.command(name="votes", description="Get the count of votes of a user")
    @app_commands.guilds(discord.Object(785839283847954433))
    @app_commands.checks.dynamic_cooldown(can_bypass_cd)
    @app_commands.describe(user="Select a user to get the vote count")
    async def votes(self, interaction: discord.Interaction, user: discord.Member=None):
        user = user if user else interaction.user
        data = await self.bot.votes.find(user.id)
        if not data:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label=f'Vote for us here!', url="https://top.gg/servers/785839283847954433/vote"))
            await interaction.response.send_message(content=f"{user.mention}, you have 0 votes!", view=view)
            return
        embed = discord.Embed(title=f"{user.name}'s votes", description=f"Total Votes: {data['total_vote']}\nVote Streak: {data['streak']}\nLast Vote: <t:{round(data['last_vote'].timestamp())}:R>", color=user.color)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/830519601384128523.gif?v=1")
        embed.timestamp =datetime.datetime.utcnow()
        embed.set_footer(text=f"Requested by {interaction.user.mention}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="vote", description="Vote for a server")
    async def vote(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            title=f"Vote for {ctx.guild.name}", 
            description =
                f"❥ Special <@&786884615192313866> Role with 1x guild-wide multi.\n"
                f"❥ 1x extra entry into all frisky giveaways.\n"
                f"❥ 2,500 Casino Cash. Collect using ,collectincome in <#786117471840895016>.\n"
                f"❥ Access to <#929613393097293874> with 2x Amaari\n", 
            color=ctx.author.color
        )
        embed.set_thumbnail(url = "https://cdn.discordapp.com/emojis/942521024476487741.webp?size=128&quality=lossless")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f'Top.gg', url="https://top.gg/servers/785839283847954433/vote"))
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Votes(bot))
    