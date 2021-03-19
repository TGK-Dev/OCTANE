import discord
from datetime import datetime
from discord.ext import commands


class Admins(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Administrator Cog  is Loaded')

	@commands.command()
	async def logout(self, ctx):
		if ctx.author.guild_permissions.administrator:

			await ctx.send(f'Bye Loging out from discord taking some Sleep commands used by {ctx.author.mention}')
			await ctx.bot.logout()
		else:
			await ctx.send(f'{ctx.author.mention} Why you think you a administrator of the Server')

	@commands.command()
	async def activity(self, ctx, *, activity):
		if ctx.author.guild_permissions.administrator:

			await self.client.change_presence(activity=discord.Game(name=f"{activity}")) # This changes the bots 'activity'
			await ctx.send('Bot activity is Updated')
		else:
			await ctx.send(f'{ctx.author.mention} You not an **ADMINISTRATOR** in server!')
	@commands.command()
	async def status(self,ctx, arg):
		if ctx.author.guild_permissions.administrator:

			if arg == 'dnd':
				await self.client.change_presence(status=discord.Status.dnd)
				await ctx.send('Bot status is Updated')
			elif arg == 'online':
				await self.client.change_presence(status=discord.Status.online)
				await ctx.send('Bot status is Updated')
			elif arg == 'idle' :
				await self.client.change_presence(status=discord.Status.idle)
				await ctx.send('Bot status is Updated')
			else: 
				await ctx.send(f'{ctx.author.mention} Plsease Provide The vaild Status')
				await ctx.send('Bot status is Updated')
		else:
			await ctx.send(f'{ctx.author.mention} You not an **ADMINISTRATOR** in server!')

	@commands.command()
	async def say(self,ctx, *, say):
		if ctx.author.guild_permissions.administrator:
			await ctx.message.delete()
			await send(f'{say}')
		else:
			return



def setup(client):
	client.add_cog(Admins(client))