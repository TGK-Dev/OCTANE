import discord
from discord.ext import commands

class Moderator(commands.Cog):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Moderator Cog Is Loaded')

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def whois(self, ctx, member: discord.Member = None):
		
		def fomat_time(time):
		  return time.strftime('%d-%B-%Y %I:%m %p')

		member = member if member else ctx.author
		usercolor = member.color

		
		embed = discord.Embed(title=f'{member.name}', color=usercolor)
		embed.set_thumbnail(url=member.avatar_url)
		embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
		embed.add_field(name='Created at:', value=fomat_time(member.created_at))
		embed.add_field(name='Joined at', value=fomat_time(member.joined_at))

		hsorted_roles = sorted([role for role in member.roles[-1:]], key=lambda x: x.position, reverse=True)
		

		embed.add_field(name='Top:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
		embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
		await ctx.send(embed=embed)


	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		try:
			await member.send(f'You Have Kicked From the The Gamblers Kingdom | {reason}')
			await ctx.message.delete()
			await ctx.send(f'<:allow:819194696874197004> | ***The {member.name} Is Now Kicked From Server***')
		except:
			await ctx.send(f"I Can't Dm them but\n<:allow:819194696874197004> | ***The {member.name} Is Now Kicked From Server***")
		

		await member.kick(reason=reason)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		try:
			await member.send(f'You Have Benned From the The Gamblers Kingdom | {reason}')
			await ctx.message.delete()
			await ctx.send(f'<:allow:819194696874197004> | ***The {member.name} Is Now Banned From Server***')
		except:
			await member.ban(reason=reason)
			await ctx.send(f"I Can't Dm them but\n<:allow:819194696874197004> | ***The {member.name} Is Now Banned From Server***")
	
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unban(self, ctx, user: discord.User):
		    await ctx.guild.unban(user)
		    await ctx.send(f"Successfully Removed the Ban from {user.name}")
	
	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, amount=5):
		await ctx.message.delete()	
		await ctx.channel.purge(limit=amount)
		await ctx.send(f"Last {amount} Message Are Purged", delete_after=3)
		
	@commands.command(pass_context=True)
	@commands.has_permissions(manage_messages=True)
	async def setnick(self, ctx, member: discord.Member, *, nick):
		await member.edit(nick=nick)
		await ctx.message.delete()
		await ctx.send(f'Nickname was changed for {nick} ')

	@commands.command(aliases=['av'])
	@commands.has_permissions(manage_messages=True)
	async def avatar(self, ctx, member: discord.Member = None):

		member = member if member else ctx.author

		embed = discord.Embed(color=0x00ffff)
		embed.set_image(url=member.avatar_url)
		await ctx.send(embed=embed, delete_after=30)


def setup(bot):
	bot.add_cog(Moderator(bot))




"""
channel = self.bot.get_channel(821802944235700234)

eembed = discord.Embed(titel=f'Member Banned', color=0xff0000)
eembed.add_field(name=f'Mamber Name: ', value=f'{member.name}')
eembed.add_field(name=f'Reason: ', value=reason)

await channel.send(embed=eembed)
"""