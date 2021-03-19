import discord
from discord.ext import commands

class Moderator(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Moderator Cog Is Loaded')

	@commands.command()
	async def whois(self, ctx, member: discord.Member = None):
		if ctx.author.guild_permissions.manage_messages:

			def fomat_time(time):
			  return time.strftime('%d-%B-%Y %I:%m %p')

			member = member if member else ctx.author
			usercolor = member.color

			
			embed = discord.Embed(title=f'{member.name}', color=usercolor)
			embed.set_thumbnail(url=member.avatar_url)
			embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
			embed.add_field(name='Created at:', value=fomat_time(member.created_at))
			embed.add_field(name='Joined at', value=fomat_time(member.joined_at))

			sorted_roles = sorted([role for role in member.roles[1:]], key=lambda x: x.position, reverse=True)
			hsorted_roles = sorted([role for role in member.roles[-1:]], key=lambda x: x.position, reverse=True)
			

			embed.add_field(name='Top:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
			embed.add_field(name='Roles', value=', '.join(role.mention for role in sorted_roles))
			embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
			await ctx.send(embed=embed)
		else:
			await ctx.send(f'{ctx.author.mention} You dont have permissions to use this command!')



	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason=None):

		if ctx.author.guild_permissions.kick_members:
			
			await member.send(f'You Have Kicked From the The Gamblers Kingdom | {reason}')
			await ctx.message.delete()
			await member.kick(reason=reason)
			await ctx.send(f'<:allow:819194696874197004> | ***The {member.name} Is Now Kicked From Server***')
		else:
			await ctx.send(f'{ctx.author.mention} You Cant Use This Command.')

	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason=None):

		if ctx.author.guild_permissions.ban_members:
			
			await member.send(f'You Have Benned From the The Gamblers Kingdom | {reason}')
			await ctx.message.delete()
			await member.ban(reason=reason)
			await ctx.send(f'<:allow:819194696874197004> | ***The {member.name} Is Now Banned From Server***')

			channel = self.client.get_channel(821802944235700234)

			eembed = discord.Embed(titel=f'Member Banned', color=0xff0000)
			eembed.add_field(name=f'Mamber Name: ', value=f'{member.name}')
			eembed.add_field(name=f'Reason: ', value=reason)

			await channel.send(embed=eembed)
		else:
			await ctx.send(f'{ctx.author.mention} You cant Use This Command.')


	@commands.command()
	async def unban(self, ctx, user: discord.User):
		if ctx.author.guild_permissions.administrator:
		    await ctx.guild.unban(user)
		    await ctx.send(f"Successfully unbanned user with id {user.name}")
		else:
			await ctx.send("You Dont have permission to use ths Command")
	
	@commands.command()
	async def purge(self, ctx, amount=5):
		if ctx.author.guild_permissions.manage_messages:
	
			await ctx.message.delete()	
			await ctx.channel.purge(limit=amount)
			await ctx.send(f"Last {amount} Message Are Purged", delete_after=10)
		else:
			await ctx.send(f'{ctx.author.mention} you dont have permission to use this command')

	@commands.command(pass_context=True)
	async def setnick(self, ctx, member: discord.Member, *, nick):
		if ctx.author.guild_permissions.manage_messages:
			await member.edit(nick=nick)
			await ctx.message.delete()
			await ctx.send(f'Nickname was changed for {nick} ')
		else:
			await ctx.send(f'{ctx.author.mention} you dont have permission to use this command')




def setup(client):
	client.add_cog(Moderator(client))




