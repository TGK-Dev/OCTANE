from discord import app_commands
from discord.ext import commands, tasks
from copy import deepcopy
import datetime
import discord
class Votes(commands.Cog, name="Votes",description="Server Vote counter with Top.gg"):
    def __init__(self, bot):
        self.bot = bot
        self.vote_remider_task = self.check_remiders.start()
    
    def cog_unload(self):
        self.check_remiders.cancel()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @tasks.loop(seconds=60)
    async def check_remiders(self):
        currentTime = datetime.datetime.utcnow()
        currentVotes = deepcopy(self.bot.current_votes)
        for key, value in currentVotes.items():
            
            if value['reminded'] == True:
                continue
                
            expired_time = value['last_vote'] + datetime.timedelta(hours=12)

            if currentTime >= expired_time and value['reminded'] == False:
                self.bot.dispatch("vote_reminder", value)
    
    @commands.Cog.listener()
    async def on_vote_reminder(self, vote):
        if vote['reminded'] == True:
            return
        
        embed = discord.Embed(title="You are able to vote again!",description="Your vote is ready at top.gg:", color=0xE74C3C)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='Top.gg', url="https://top.gg/servers/785839283847954433/vote"))

        guild = self.bot.get_guild(785839283847954433)
        member = guild.get_member(vote['_id'])

        if member is None:
            return await self.bot.votes.delete(vote['_id'])

        await member.remove_roles(guild.get_role(786884615192313866))

        vote['reminded'] = True
        await self.bot.votes.upsert(vote)

        try:
            await member.send(embed=embed, view=view)
        except discord.HTTPException:
            pass

        try:
            self.bot.current_votes.pop(vote['_id'])
        except KeyError:
            pass

    @commands.command(name="vote", description="Vote for a server", brife="vote")
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



