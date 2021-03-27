import discord
from datetime import datetime
import random
from discord.ext import commands

class Basic(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Basic Cogs is Loaded')

	@commands.command(aliases=['sinfo'])
	async def serverinfo(self, ctx):
		usercolor = ctx.author.color
		guild = self.client.get_guild(785839283847954433)
		booter= int(guild.premium_subscription_count)

		em = discord.Embed(title='Info for The Gamblers Kingdom', color=usercolor)
		em.set_thumbnail(url=guild.icon_url)
		em.add_field(name='Owners', value='utki007#007, JAY#0138', inline=True)
		em.add_field(name='Booster Count', value=f'The Total booster {booter} \n booster Role <@&786477872029892639>', inline=False)
		em.add_field(name='Server Member Count: ', value=f'{guild.member_count}', inline=False)
		em.set_footer(text='ID: 785839283847954433, Created•12/08/2020', icon_url=guild.icon_url)
		await ctx.send(embed=em)


	@commands.command()
	async def ping(self, ctx):
		await ctx.reply(f'Ping ``{round(self.client.latency * 1000)}``ms') 

	@commands.command()
	async def botinfo(self, ctx):
		embed = discord.Embed(color=0xffd700, title='Bots Infomation')
		embed.add_field(name='Bot Name', value=f'{self.client.user.name}')
		embed.add_field(name='Bot Owner', value=f'<@301657045248114690>, <@488614633670967307>')
		embed.add_field(name='Bot language', value="Python")
		embed.add_field(name='Bot Version', value="2.2")
		embed.set_footer(text=f'Requested by ID: {ctx.author.id} | Name: {ctx.author.name}')

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


