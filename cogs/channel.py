import discord
from datetime import datetime
from discord.ext import commands



class Channels(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Channels Cogs is Loaded')

	@commands.command()
	async def lock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
		if  ctx.author.guild_permissions.manage_messages:

			channel = channel if channel else ctx.channel
			role = role if role else ctx.guild.default_role

			overwrite = channel.overwrites_for(ctx.guild.default_role)
			overwrite.send_messages = False
			
			await ctx.message.delete()			
			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
			
			embed = discord.Embed(color=0xff0000, description=f'The {channel.name} is lock for {role.name}')
			await ctx.send(embed=embed)
		else:
			await ctx.send(f'{ctx.author.mention} You dont have permissions to use this commands')

	@commands.command()
	async def unlock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
		if  ctx.author.guild_permissions.manage_messages:

			channel = channel if channel else ctx.channel
			role = role if role else ctx.guild.default_role

			overwrite = channel.overwrites_for(ctx.guild.default_role)
			overwrite.send_messages = True
			
			await ctx.message.delete()			
			await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

			embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is unlock for {role.name}')
			await ctx.send(embed=embed)
		else:
			await ctx.send(f'{ctx.author.mention} You dont have permissions to use this command')

	@commands.command(aliases=['sm'])
	async def slowmode(self, ctx, channel: discord.TextChannel, Sec: int):
		if ctx.author.guild_permissions.manage_messages:

			channel = channel if channel else ctx.channel
			await ctx.channel.edit(slowmode_delay=Sec)

			await ctx.send(f'The {ctx.channel.mention} channel slowmode iS now *{Sec}* Seconds')
		else:
			await ctx.send(f'The {ctx.author.mention} You Cant Use This Command.')

	@commands.command()
	async def hide(self, ctx, channel: discord.TextChannel = None):
		if ctx.author.guild_permissions.ban_members:

			channel = channel if channel else ctx.channel
			role = discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
			overwrite = channel.overwrites_for(role)
			overwrite.view_channel = False
			await channel.set_permissions(role, overwrite=overwrite)


			embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is Now Hidded for for {role.mention}')
			await ctx.send(embed=embed, delete_after=10)
			await ctx.message.delete()

			await ctx.send(embed=embed)
		else:
			await ctx.send(f'This commands is only for server Moderator')

	@commands.command(aliases=['uhide'])
	async def unhide(self, ctx, channel: discord.TextChannel = None):
		if ctx.author.guild_permissions.ban_members:

			channel = channel if channel else ctx.channel
			role = discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
			overwrite = channel.overwrites_for(role)
			overwrite.view_channel = True
			await channel.set_permissions(role, overwrite=overwrite)
			await ctx.message.delete()

			embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is Now Not Hidded for for {role.mention}')
			await ctx.send(embed=embed, delete_after=10)
		else:
			await ctx.send(f'This commands is only for server Moderator')



def setup(client):
	client.add_cog(Channels(client))