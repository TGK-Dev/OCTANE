import discord
from discord.ext import commands
from utils.checks import checks

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')

    @commands.command(name='suggestion', description="Suggest something for serve", aliases=['suggest'])
    @commands.check_any(checks.can_use())
    async def suggestion(self, ctx, *, suggestion):
        embed = discord.Embed(title=f"Suggestion # {self.bot.total_suggestions + 1}", description=suggestion, color=0x7289da)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar.url)
        channel = self.bot.get_channel(int(self.bot.config_data[ctx.guild.id]['suggestion']))
        message = await channel.send(embed=embed)
        data = {"_id": message.id, "suggestion": suggestion, "author": ctx.author.id, "guild": ctx.guild.id}
        await self.bot.suggest.upsert(data)
        await message.add_reaction('<a:up_suggest:952869422178111498>')
        await message.add_reaction('<a:down_suggest:952869487642812446>')
        self.bot.total_suggestions += 1
        await ctx.message.delete()
    
    @commands.command(name="approve", description="Approve a suggestion")
    @commands.check_any(checks.can_use())
    async def approve(self, ctx, id: int, *,reason: str):
        data = await self.bot.suggest.find(id)
        if not data:
            return await ctx.send("That suggestion doesn't exist")
        channel = self.bot.get_channel(int(self.bot.config_data[ctx.guild.id]['suggestion']))
        message = await channel.fetch_message(id)
        embed = message.embeds[0]
        embed.title += f" Approved By {ctx.author}"
        embed.color = 0x00ff00
        embed.add_field(name=f"Reason:", value=reason, inline=False)
        await message.edit(embed=embed)
        await message.clear_reactions()
    
    @commands.command(name="deny", description="Deny a suggestion")
    @commands.check_any(checks.can_use())
    async def deny(self, ctx, id: int, *,reason: str):
        data = await self.bot.suggest.find(id)
        if not data:
            return await ctx.send("That suggestion doesn't exist")
        channel = self.bot.get_channel(int(self.bot.config_data[ctx.guild.id]['suggestion']))
        message = await channel.fetch_message(id)
        embed = message.embeds[0]
        embed.title += f" Denied By {ctx.author}"
        embed.color = 0xff0000
        embed.add_field(name=f"Reason:", value=reason, inline=False)
        await message.edit(embed=embed)
        await message.clear_reactions()
    
    @commands.command(name="considered", description="Mark a suggestion as considered")
    @commands.check_any(checks.can_use())
    async def considered(self, ctx, id: int, *,reason: str):
        data = await self.bot.suggest.find(id)
        if not data:
            return await ctx.send("That suggestion doesn't exist")
        channel = self.bot.get_channel(int(self.bot.config_data[ctx.guild.id]['suggestion']))
        message = await channel.fetch_message(id)
        embed = message.embeds[0]
        embed.title += f" Considered By {ctx.author}"
        embed.color = 0xffff00
        embed.add_field(name=f"Reason:", value=reason, inline=False)
        await message.edit(embed=embed)
        await message.clear_reactions()
    
    @commands.command(name="implemented", description="Mark a suggestion as implemented")
    @commands.check_any(checks.can_use())
    async def implemented(self, ctx, id: int, *,reason: str):
        data = await self.bot.suggest.find(id)
        if not data:
            return await ctx.send("That suggestion doesn't exist")
        channel = self.bot.get_channel(int(self.bot.config_data[ctx.guild.id]['suggestion']))
        message = await channel.fetch_message(id)
        embed = message.embeds[0]
        embed.title += f" Implemented By {ctx.author}"
        embed.color = 0x0000ff
        embed.add_field(name=f"Reason:", value=reason, inline=False)
        await message.edit(embed=embed)
        await message.clear_reactions()

def setup(bot):
    bot.add_cog(Suggestions(bot))