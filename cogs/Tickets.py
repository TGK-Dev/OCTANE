from discord import app_commands
from discord.ext import commands
import discord
from ui.Ticket_system import Ticket_main, Ticket_Control
class Ticket(commands.Cog, name="Ticket System", description="Create Ticket Without Any Worry"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_main(self.bot))
        self.bot.add_view(Ticket_Control(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.command()
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=Ticket_main(self.bot))

    
async def setup(bot):
    await bot.add_cog(Ticket(bot))