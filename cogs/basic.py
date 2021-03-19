import discord
from datetime import datetime
from discord.ext import commands

class Basic(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Basic Cogs is Loaded')

	@commands.command()
	async def ping(self, ctx):
		await ctx.send(f'Ping ``{round(self.client.latency * 1000)}``ms') 

	@commands.command()
	async def botinfo(self, ctx):
		embed = discord.Embed(color=0xffd700, title='Bots Infomation')
		embed.add_field(name='Bot Name', value=f'{self.client.user.name}')
		embed.add_field(name='Bot Owner', value=f'JAY 2404', )
		embed.add_field(name='Bot language', value="Python")
		embed.add_field(name='Bot Version', value="1.5")
		embed.set_footer(text=f'Requested by {ctx.author.name}')

		await ctx.send(embed=embed)

	@commands.command()
	async def verify(self, ctx):
		channel = self.client.get_channel(812906607301099520)
		channel1 = self.client.get_channel(786098255448375296)
		verify=discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
		member = ctx.author
		await ctx.message.delete()

		if channel == ctx.channel:
			
			await member.add_roles(verify)
			await channel1.send(f'{ctx.author.mention}/{ctx.author.name} is has done his basic verfications')
		else:
			await ctx.send(f"{ctx.author.mention} You are verifed or either in worng channel which is not possibal time to ban you")


def setup(client):
	client.add_cog(Basic(client))


