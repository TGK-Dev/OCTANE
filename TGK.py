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




client.run(f'ODE2Njk5MTY3ODI0MjgxNjIx.YD-wXw.CE18KDWlS2fvjyBDNw_fRvonw_s')

#ODE2Njk5MTY3ODI0MjgxNjIx.YD-wXw.ZwQEyvDMWayQJdFeA9AXXgOxcyw	

#<a:celeyay:821818380406882315>
#description=f'Head to [:golf:。server-map](https://discord.com/channels/785839283847954433/785861545820815380/804062363840937984) to checkout everything the server has to offer.\n \n ➻ Read our rules [here](https://discord.com/channels/785839283847954433/785841560918163501) \n ➻ Get your roles from [:sparkles:。self-roles](https://discord.com/channels/785839283847954433/785882615202316298/795729352062140537), and say Hi to everyone at [:speech_balloon:。general](https://discord.com/channels/785839283847954433/785847439579676672/817100365665009684)! \n \n ➻ To access specific sections, simply follow: \n ◉ [:frog:。dank-bifröst](https://discord.com/channels/785839283847954433/801394407521517578/812654537873162261) for Dank Memer Channels \n       ◉ [:dragon:。poke-bifröst](https://discord.com/channels/785839283847954433/802195590208421908/802538839838556170) for Pokémon Channels \n       ◉ [:game_die::。casino-bifrost](https://discord.com/channels/785839283847954433/804042634011738112/804051999879462982) for Casino Channels \n \n ➻ To get in touch with staff, simply raise a ticket from \n \n Once again, a warm welcome <:bunny_heart:821984967693303808> Have a great time![:love_letter:。server-support](https://discord.com/channels/785839283847954433/785901543349551104/815993563594358816)' )
