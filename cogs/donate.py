import discord
from discord.ext import commands


class Donate(commands.Cog):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Donate Cogs is Loaded')

	@commands.command()
	async def sgive(self, ctx, price, winner, req, game):
		channel = self.bot.get_channel(819968735557189666)
		
		if channel == ctx.channel:

			embed = discord.Embed(color=0x00ffff, title=f'Sponsorship from For the Giveaway')
			embed.add_field(name='Price: ', value=f'{price}',)
			embed.add_field(name='Winners: ', value=f'{winner}', inline=False)
			embed.add_field(name='Recruitment: ', value=f'{req}', inline=False)
			embed.add_field(name='Game:', value=f'{game}', inline=False)
			embed.add_field(name='Sposor from: ', value=f'{ctx.author.mention}', inline=False)

			await ctx.send(f'{ctx.author.mention} plsease Mention the any online Staff', embed=embed)
		else:
			await ctx.send(f'{ctx.author.mention} your in worng channel! Try in this channel <#812711254790897714>')

	@commands.command()
	async def sheist(self, ctx, price, req):
		channel = self.bot.get_channel(819968735557189666)
		
		if channel == ctx.channel:

			embed = discord.Embed(color=0x00ffff, title=f'Sponsorship from For the Heist')
			embed.add_field(name='Amount: ', value=f'{price}',)
			embed.add_field(name='Recruitment: ', value=f'{req}', inline=False)
			embed.add_field(name='Sposor from: ', value=f'{ctx.author.mention}', inline=False)

			await ctx.send(f'{ctx.author.mention} plsease Mention the any online Staff', embed=embed)
		else:
			await ctx.send(f'{ctx.author.mention} your in worng channel! Try in this channel <#812711254790897714>')

def setup(bot):
	bot.add_cog(Donate(bot))


