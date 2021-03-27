import discord
import os
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=commands.when_mentioned_or('>'), case_insensitive=True, intents=intents)
client.remove_command('help')


@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	print(f'The {extension} is loaded by {ctx.author.name}')
	await ctx.send(f'The {extension} is successfully Loaded.')

@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	print(f'The {extension} is unloaded by {ctx.author.name}')
	await ctx.send(f'The {extension} is successfully unloaded.')

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

@client.group(invoke_without_command=True)
async def help(ctx):

	embed = discord.Embed(title='Help', color=0x02ff06, description='This Bot Help command, You can see the All bot command Category')
	embed.add_field(name='Basics', value='List of the commands: \n 1.Bot Info \n 2.ping \n 3.verify \n ', inline=False)
	embed.add_field(name='Funs', value='1. 8ball<question> \n2. There are many many different commands to Expres your Feeling \npossitive:\n ```cheer, thunbsup, ,happy.``` \nNeutral:\n ```bonk, dab, sleep, yes```\nNegative:\n``` sad, angry, cay```')
	embed.add_field(name='Donate', value='List of the commands: \n 1.sgive \n 2.sheist', inline=False)
	embed.add_field(name='Moderator: ', value='List of the commands: \n 1.Ban \n 2.unban \n 3.kick \n 4.purge \n 5. whois \n 6. setnick \n 7.avatar', inline=False)
	embed.add_field(name='Channels Management: ', value='List of the commands: \n 1.hide \n 2.ubhide \n 3.lock \n 4.unlock \n 5.slowmod', inline=False)
	embed.add_field(name='Administrator: ', value='List of the commands: \n 1.activity \n 2.status \n 3.logout', inline=False)

	await ctx.message.reply(embed=embed, delete_after=300)
#info commands
@help.command()
async def botinfo(ctx):

	em = discord.Embed(title='Bot information', color=0x02ff06, description='Gives information about the Bot')
	em.add_field(name='***Sytax***', value='>botinfo')

	await ctx.send(embed=em)

@help.command()
async def ping(ctx):

	em = discord.Embed(title='Ping', color=0x02ff06, description='Gives latency of the bot with discord')
	em.add_field(name='***Sytax***', value='>ping')

	await ctx.send(embed=em)

@help.command()
async def verify(ctx):

	em = discord.Embed(title='verify', color=0x02ff06, description='Only ca used when joining server first time')
	em.add_field(name='***Sytax***', value='>verify')
	await ctx.send(embed=em)

@help.command()
async def _8ball(ctx):

	em = discord.Embed(title='8 ball Game', value='An classic 8 ball Game')
	em.add_field(name='***Sytax***', value='>8ball <question>')

	await ctx.send(embed=em)

#Donate Commands
@help.command()
async def sgive(ctx):

	em = discord.Embed(title='Sponsor Giveaway', color=0x02ff06, description='Want to Sponsor a Giveaway use this to make thing go smoother \n *make sure to keep thing ready give to the winner, or give them to Giveaway Manager* you add a message for Giveaway to post when stating a Giveaway')
	em.add_field(name='***Sytax***', value='>sgive <price> <winners number> <Recruitment like lvl 3+ etc or type none>')

	await ctx.send(embed=em)

@help.command()
async def sheist(ctx):

	em = discord.Embed(title='Sponsor Dank Memer Heist', color=0x02ff06, description='Want to Sponsor a dank heist use this to make thing go smoother \n *make your bank ready for heist or be ready to give money to Heist Manager*** you can add message aslo that will posted before stating the Heist')
	em.add_field(name='***Sytax***', value='>sheist <amount> <Recruitment>')

	await ctx.send(embed=em)

#mode Commands
@help.command()
async def ban(ctx):

	em = discord.Embed(title='Ban', color=0x02ff06, description='Ban The member from Server')
	em.add_field(name='***Sytax***', value='>ban <user_id/mention> <reason>')

	await ctx.send(embed=em)

@help.command()
async def unban(ctx):

	em = discord.Embed(title='Unban', color=0x02ff06, description='UnBan The member from Server')
	em.add_field(name='***Sytax***', value='>unban <user_id>')

	await ctx.send(embed=em)

@help.command()
async def kick(ctx):

	em = discord.Embed(title='Kick', color=0x02ff06, description='Kick member form server')
	em.add_field(name='***Sytax***', value='>kick <user_id/mention> <reason>')

	await ctx.send(embed=em)


@help.command()
async def purge(ctx):

	em = discord.Embed(title='purge', color=0x02ff06, description='Purge Number of the message in current Channels \n***default number is 5*** ')
	em.add_field(name='***Sytax***', value='>purge <number od the message to be purge>')

	await ctx.send(embed=em)
@help.command()
async def setnick(ctx):

	em = discord.Embed(title='Nick name', color=0x02ff06, description='Change mention member Nick name')
	em.add_field(name='***Sytax***', value='>setnick <user_id/mention> <Nick_name>')

	await ctx.send(embed=em)

#channle management
@help.command()
async def lock(ctx):

	em = discord.Embed(title='Lock The Channels', color=0x02ff06, description='Lock the mention channel,\n if channel id not given current channel get lock')
	em.add_field(name='***Sytax***', value='>lock <#channel> <@role.id>')

	await ctx.send(embed=em)

@help.command()
async def unlock(ctx):

	em = discord.Embed(title='Unlock The Channels', color=0x02ff06, description='Unlock the Lock Channel')
	em.add_field(name='***Sytax***', value='>unlock <#channel> <@role.id>')

	await ctx.send(embed=em)

@help.command()
async def slowmod(ctx):

	em = discord.Embed(title='Change The Channels slowmod', color=0x02ff06, description='Set slowmod in channel max 6 hour 0s = none')
	em.add_field(name='***Sytax***', value='>slowmod <slowmode time only seconds for now>')

	await ctx.send(embed=em)

@help.command()
async def hide(ctx):

	em = discord.Embed(title='Hide the Channel for Member', color=0x02ff06, description='Remove member ability to Viwe the Channel make it staff only channel')
	em.add_field(name='***Sytax***', value='>hide <#channel>')

	await ctx.send(embed=em)

@help.command()
async def unhide(ctx):

	em = discord.Embed(title='Unhide The Channel for Member', color=0x02ff06, description='give member ability to Viwe the Channel')
	em.add_field(name='***Sytax***', value='>unhide <channel>')

	await ctx.send(embed=em)

@help.command()
async def avatar(ctx):

	em = discord.Embed(title='Show mentioned Avatar', description='can be use full to check the serer Member Avatar')
	em.add_field(name='***Sytax***', value='>avatar/av <user_id & mention>')

	await ctx.send(embed=em)
#admins
@help.command()
async def activity(ctx):

	em = discord.Embed(title='Bot Playing activity', color=0x02ff06, description='Change Bot playing activity')
	em.add_field(name='***Sytax***', value='>activity <activity>')

	await ctx.send(embed=em)

@help.command()
async def status(ctx):

	em = discord.Embed(title='Channel Bot Status', color=0x02ff06, description='Change Bot Status')
	em.add_field(name='***Sytax***', value='>status <dnd/online/idle>')

	await ctx.send(embed=em)

@help.command()
async def unload(ctx):

	em = discord.Embed(title='unload the Category of the commands', color=0x02ff06, description='name of the Category 1.admins \n 2.mode \n 3.channel \n 4.donate \n 5.basics \n Note: Use the commands will be loged in Server Console')
	em.add_field(name='***Sytax***', value='>unload <category name> ')

	await ctx.send(embed=em)

@help.command()
async def load(ctx):

	em = discord.Embed(title='Load The unloaded Category of the commands', color=0x02ff06, description='name of the Category 1.admins \n 2.mode \n 3.channel \n 4.donate \n 5.basics \n Note: Use the commands will be loged in Server Console')
	em.add_field(name='***Sytax***', value='>load <category name>')

	await ctx.send(embed=em)

@help.command()
async def logout(ctx):

	em = discord.Embed(title='Make Bot go ofline ', color=0x02ff06, description='Use the commands will be loged in Server Console')
	em.add_field(name='***Sytax***', value='>loged')

	await ctx.send(embed=em)



client.run(f'ODE2Njk5MTY3ODI0MjgxNjIx.YD-wXw.CE18KDWlS2fvjyBDNw_fRvonw_s')

#ODE2Njk5MTY3ODI0MjgxNjIx.YD-wXw.ZwQEyvDMWayQJdFeA9AXXgOxcyw	

#<a:celeyay:821818380406882315>
#description=f'Head to [:golf:。server-map](https://discord.com/channels/785839283847954433/785861545820815380/804062363840937984) to checkout everything the server has to offer.\n \n ➻ Read our rules [here](https://discord.com/channels/785839283847954433/785841560918163501) \n ➻ Get your roles from [:sparkles:。self-roles](https://discord.com/channels/785839283847954433/785882615202316298/795729352062140537), and say Hi to everyone at [:speech_balloon:。general](https://discord.com/channels/785839283847954433/785847439579676672/817100365665009684)! \n \n ➻ To access specific sections, simply follow: \n ◉ [:frog:。dank-bifröst](https://discord.com/channels/785839283847954433/801394407521517578/812654537873162261) for Dank Memer Channels \n       ◉ [:dragon:。poke-bifröst](https://discord.com/channels/785839283847954433/802195590208421908/802538839838556170) for Pokémon Channels \n       ◉ [:game_die::。casino-bifrost](https://discord.com/channels/785839283847954433/804042634011738112/804051999879462982) for Casino Channels \n \n ➻ To get in touch with staff, simply raise a ticket from \n \n Once again, a warm welcome <:bunny_heart:821984967693303808> Have a great time![:love_letter:。server-support](https://discord.com/channels/785839283847954433/785901543349551104/815993563594358816)' )
