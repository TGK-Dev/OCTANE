import discord
from discord.ext import commands

class events(commands.Cog):
	"""docstring for Example"""
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Events Cogs are Loaded')

	@commands.Cog.listener()
	async def on_member_join(self, member):
	   channel =  self.client.get_channel(785847439579676672)
	   guild = self.client.get_guild(785839283847954433)
	   embed = discord.Embed(title=f'<a:celeyay:821818380406882315> WELCOME TO TGK {member.name} <a:celeyay:821818380406882315> ', color=0xff00ff)
	   embed.set_thumbnail(url=member.avatar_url)
	   embed.add_field(name='Info Counter:', value='➻ Read our [Rules](https://discord.com/channels/785839283847954433/785841560918163501) \n ➻ Get your roles from [:sparkles:。self-roles](https://discord.com/channels/785839283847954433/785882615202316298/795729352062140537), and say Hi to everyone at :speech_balloon:[。general](https://discord.com/channels/785839283847954433/785847439579676672/817100365665009684)!', inline=False)
	   embed.add_field(name='Server Games:', value='➻ To access specific sections, simply follow: \n ◉ :frog:[。dank-bifröst](https://discord.com/channels/785839283847954433/801394407521517578/812654537873162261) for Dank Memer Channels \n       ◉ :dragon:[。poke-bifröst](https://discord.com/channels/785839283847954433/802195590208421908/802538839838556170) for Pokémon Channels \n       ◉ :game_die:[:。casino-bifrost](https://discord.com/channels/785839283847954433/804042634011738112/804051999879462982) for Casino Channels', inline=False)
	   embed.add_field(name='Server Support', value='To get in touch with staff, simply send a dm to our lovely <@823645552821665823> more info in :love_letter:[。mod-mail](https://discord.com/channels/785839283847954433/823659390108303410/823667017517105192)', inline=False)
	   embed.add_field(name='Server Member Count: ', value=f'{guild.member_count}', inline=False)
	   embed.set_footer(text='Once again, a warm welcome. Have a great time!', icon_url=member.avatar_url)
	   await channel.send(f'{member.mention}', embed=embed)
	   await member.send(embed=embed)
	   
	
	@commands.Cog.listener()
	async def on_message(self, message):
		word_list = ['vote link', 'vote Link', 'Vote link', 'Vote Link']

		messageContent = message.content
		if len(messageContent) > 0:
			for word in word_list:
				if word in messageContent:
					return await message.reply('Please Vote us here, <https://top.gg/servers/785839283847954433/vote>, Thanks For Support ^0^')

	#@commands.Cog.listener()
	#async def on_message(self, message):
	#	heist = ['Time is up to join ']
	#	channel = message.channel
	#	guild = self.client.get_guild(785839283847954433)
	#	if message.author.id == 488614633670967307:
	#		
	#		messageContent = message.content
	#		if len(messageContent) > 0:
	#			for word in heist:
	#				if word in messageContent:
	#					
	#					overwrite = channel.overwrites_for(message.guild.default_role)
	#					overwrite.send_messages = False
	#					await channel.set_permissions(guild.default_role, overwrite=overwrite)
	#					
	#					await message.reply('The Channels is Lock for ``everyone``')
	#					return
	#	else:
	#		return


		
def setup(client):
	client.add_cog(events(client))
