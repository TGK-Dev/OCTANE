import discord
from discord.ext import commands

class error(commands.Cog):
	"""docstring for error"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
	    if isinstance(error, commands.CommandOnCooldown):
	        m, s = divmod(error.retry_after, 60)
	        h, m = divmod(m, 60)
	        if int(h) == 0 and int(m) == 0:
	            await ctx.message.reply(f' You must wait {int(s)} seconds to use this command!')
	        elif int(h) == 0 and int(m) != 0:
	            await ctx.message.reply(f' You must wait {int(m)} minutes and {int(s)} seconds to use this command!')
	        else:
	            await ctx.message.reply(f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!') 
	    elif isinstance(error, commands.MissingRequiredArgument):
	    	await ctx.message.reply(f'Please Enter all theRequird Argument')
	    elif isinstance(error, commands.CommandNotFound):
	    	await ctx.message.reply('Command not found', delete_after=10)
	    elif isinstance(error, commands.MemberNotFound):
	    	await ctx.message.reply('Please Check the Member mention/id beause Member is Not Found in Server')
	    elif isinstance(error, commands.UserNotFound):
	    	await ctx.message.reply('User not Found on discord')
	    elif isinstance(error, commands.ChannelNotFound):
	    	await ctx.message.reply('Channel Not Found')
	    elif isinstance(error, commands.RoleNotFound):
	    	await ctx.message.reply('Role Not Found')
	    elif isinstance(error, commands.MissingPermissions):
	    	await ctx.message.reply(f'You are missing Permissions')
	    elif isinstance(error, commands.ExtensionAlreadyLoaded):
	    	await ctx.message.reply(f'The {name} is Already Loaded')
	    elif isinstance(error, commands.ExtensionNotFound):
	    	await ctx.message.reply(f'The {name} is Already UnLoaded')
	    elif isinstance(error, commands.ExtensionNotFound):
	    	await ctx.message.reply(f'The Extension not Found')
	    else:
	    	raise error

def setup(client):
	client.add_cog(error(client))
