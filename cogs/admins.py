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
	@commands.has_permissions(administrator=True)
	async def logout(self, ctx):

		await ctx.reply(f'Shuting Down Bot \n logout command used By {ctx.author.name}')
		await ctx.bot.logout()

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def activity(self, ctx, *, activity):
		
		await self.client.change_presence(activity=discord.Game(name=f"{activity}")) # This changes the bots 'activity'
		await ctx.send('Bot activity is Updated')
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def status(self,ctx, arg):
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

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def say(self,ctx, *, say):
		await ctx.message.delete()
		await ctx.send(f'{say}')


def setup(client):
	client.add_cog(Admins(client))