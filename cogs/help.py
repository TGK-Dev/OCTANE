import discord
from datetime import datetime
from discord.ext import commands


class help(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client


	@commands.Cog.listener()
	async def on_ready(self):
		print('Help cmd lodded')

	@commands.group(invoke_without_command=True)
	async def help(self, ctx):

		embed = discord.Embed(title='Help', color=0x02ff06, description='This Bot Help command, You can see the All bot command Category')
		embed.add_field(name='Basics', value='List of the commands: \n 1.Bot Info \n 2.ping \n 3.verify \n ', inline=False)
		embed.add_field(name='Funs', value='1. 8ball<question> \n2. There are many many different commands to Expres your Feeling \npossitive:\n ```cheer, thunbsup, ,happy.``` \nNeutral:\n ```bonk, dab, sleep, yes```\nNegative:\n``` sad, angry, cay```')
		embed.add_field(name='Donate', value='List of the commands: \n 1.sgive \n 2.sheist', inline=False)
		embed.add_field(name='Moderator: ', value='List of the commands: \n 1.Ban \n 2.unban \n 3.kick \n 4.purge \n 5. whois \n 6. setnick \n 7.avatar', inline=False)
		embed.add_field(name='Channels Management: ', value='List of the commands: \n 1.hide \n 2.ubhide \n 3.lock \n 4.unlock \n 5.slowmod', inline=False)
		embed.add_field(name='Administrator: ', value='List of the commands: \n 1.activity \n 2.status \n 3.logout', inline=False)

		await ctx.message.reply(embed=embed, delete_after=300)

	@help.command()
	async def botinfo(self, ctx):

		em = discord.Embed(title='Bot information', color=0x02ff06, description='Gives information about the Bot')
		em.add_field(name='***Sytax***', value='>botinfo')

		await ctx.send(embed=em)

	@help.command()
	async def ping(self, ctx):

		em = discord.Embed(title='Ping', color=0x02ff06, description='Gives latency of the bot with discord')
		em.add_field(name='***Sytax***', value='>ping')

		await ctx.send(embed=em)

	@help.command()
	async def verify(self, ctx):

		em = discord.Embed(title='verify', color=0x02ff06, description='Only ca used when joining server first time')
		em.add_field(name='***Sytax***', value='>verify')
		await ctx.send(embed=em)

	@help.command()
	async def _8ball(self, ctx):

		em = discord.Embed(title='8 ball Game', value='An classic 8 ball Game')
		em.add_field(name='***Sytax***', value='>8ball <question>')

		await ctx.send(embed=em)

	#Donate Commands
	@help.command()
	async def sgive(self, ctx):

		em = discord.Embed(title='Sponsor Giveaway', color=0x02ff06, description='Want to Sponsor a Giveaway use this to make thing go smoother \n *make sure to keep thing ready give to the winner, or give them to Giveaway Manager* you add a message for Giveaway to post when stating a Giveaway')
		em.add_field(name='***Sytax***', value='>sgive <price> <winners number> <Recruitment like lvl 3+ etc or type none>')

		await ctx.send(embed=em)

	@help.command()
	async def sheist(self, ctx):

		em = discord.Embed(title='Sponsor Dank Memer Heist', color=0x02ff06, description='Want to Sponsor a dank heist use this to make thing go smoother \n *make your bank ready for heist or be ready to give money to Heist Manager*** you can add message aslo that will posted before stating the Heist')
		em.add_field(name='***Sytax***', value='>sheist <amount> <Recruitment>')

		await ctx.send(embed=em)

	#mode Commands
	@help.command()
	async def ban(self, ctx):

		em = discord.Embed(title='Ban', color=0x02ff06, description='Ban The member from Server')
		em.add_field(name='***Sytax***', value='>ban <user_id/mention> <reason>')

		await ctx.send(embed=em)

	@help.command()
	async def unban(self, ctx):

		em = discord.Embed(title='Unban', color=0x02ff06, description='UnBan The member from Server')
		em.add_field(name='***Sytax***', value='>unban <user_id>')

		await ctx.send(embed=em)

	@help.command()
	async def kick(self, ctx):

		em = discord.Embed(title='Kick', color=0x02ff06, description='Kick member form server')
		em.add_field(name='***Sytax***', value='>kick <user_id/mention> <reason>')

		await ctx.send(embed=em)


	@help.command()
	async def purge(self, ctx):

		em = discord.Embed(title='purge', color=0x02ff06, description='Purge Number of the message in current Channels \n***default number is 5*** ')
		em.add_field(name='***Sytax***', value='>purge <number od the message to be purge>')

		await ctx.send(embed=em)
	@help.command()
	async def setnick(self, ctx):

		em = discord.Embed(title='Nick name', color=0x02ff06, description='Change mention member Nick name')
		em.add_field(name='***Sytax***', value='>setnick <user_id/mention> <Nick_name>')

		await ctx.send(embed=em)

	#channle management
	@help.command()
	async def lock(self, ctx):

		em = discord.Embed(title='Lock The Channels', color=0x02ff06, description='Lock the mention channel,\n if channel id not given current channel get lock')
		em.add_field(name='***Sytax***', value='>lock <#channel> <@role.id>')

		await ctx.send(embed=em)

	@help.command()
	async def unlock(self, ctx):

		em = discord.Embed(title='Unlock The Channels', color=0x02ff06, description='Unlock the Lock Channel')
		em.add_field(name='***Sytax***', value='>unlock <#channel> <@role.id>')

		await ctx.send(embed=em)

	@help.command()
	async def slowmod(self, ctx):

		em = discord.Embed(title='Change The Channels slowmod', color=0x02ff06, description='Set slowmod in channel max 6 hour 0s = none')
		em.add_field(name='***Sytax***', value='>slowmod <slowmode time only seconds for now>')

		await ctx.send(embed=em)

	@help.command()
	async def hide(self, ctx):

		em = discord.Embed(title='Hide the Channel for Member', color=0x02ff06, description='Remove member ability to Viwe the Channel make it staff only channel')
		em.add_field(name='***Sytax***', value='>hide <#channel>')

		await ctx.send(embed=em)

	@help.command()
	async def unhide(self, ctx):

		em = discord.Embed(title='Unhide The Channel for Member', color=0x02ff06, description='give member ability to Viwe the Channel')
		em.add_field(name='***Sytax***', value='>unhide <channel>')

		await ctx.send(embed=em)

	@help.command()
	async def avatar(self, ctx):

		em = discord.Embed(title='Show mentioned Avatar', description='can be use full to check the serer Member Avatar')
		em.add_field(name='***Sytax***', value='>avatar/av <user_id & mention>')

		await ctx.send(embed=em)
	#admins
	@help.command()
	async def activity(self, ctx):

		em = discord.Embed(title='Bot Playing activity', color=0x02ff06, description='Change Bot playing activity')
		em.add_field(name='***Sytax***', value='>activity <activity>')

		await ctx.send(embed=em)

	@help.command()
	async def status(self, ctx):

		em = discord.Embed(title='Channel Bot Status', color=0x02ff06, description='Change Bot Status')
		em.add_field(name='***Sytax***', value='>status <dnd/online/idle>')

		await ctx.send(embed=em)

	@help.command()
	async def unload(self, ctx):

		em = discord.Embed(title='unload the Category of the commands', color=0x02ff06, description='name of the Category 1.admins \n 2.mode \n 3.channel \n 4.donate \n 5.basics \n Note: Use the commands will be loged in Server Console')
		em.add_field(name='***Sytax***', value='>unload <category name> ')

		await ctx.send(embed=em)

	@help.command()
	async def load(self, ctx):

		em = discord.Embed(title='Load The unloaded Category of the commands', color=0x02ff06, description='name of the Category 1.admins \n 2.mode \n 3.channel \n 4.donate \n 5.basics \n Note: Use the commands will be loged in Server Console')
		em.add_field(name='***Sytax***', value='>load <category name>')

		await ctx.send(embed=em)

	@help.command()
	async def logout(self, ctx):

		em = discord.Embed(title='Make Bot go ofline ', color=0x02ff06, description='Use the commands will be loged in Server Console')
		em.add_field(name='***Sytax***', value='>loged')

		await ctx.send(embed=em)

def setup(client):
	client.add_cog(help(client))
