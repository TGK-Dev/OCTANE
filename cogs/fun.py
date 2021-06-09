import asyncio
import datetime
import discord
import eight_ball
import random
import re
from string_utils import shuffle
#-----------------------------

from aiohttp import ClientSession
from discord.ext import commands
from discord.ext import commands
from discord.ext import tasks


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
description= "Fun commands"

class TimeConverter(commands.Converter,):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class fun(commands.Cog,  description=description):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	def is_me():
	    def predicate(ctx):
	        return ctx.message.author.id in [488614633670967307]
	    return commands.check(predicate)

	def perm_check():
		async def predicate(ctx):
			mod_role = [785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916]
			for mod in mod_role:
				role = discord.utils.get(ctx.guild.roles, id=mod)
				if role in ctx.author.roles:
					permissions = await ctx.bot.config.find(role.id)
					check = permissions['perm']
					return (ctx.command.name in check)
		return commands.check(predicate)


	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.command(name="dadjoke", description="Send a dad Joke", usage="" ,aliases=["djoke"])
	#@commands.has_any_role(799037944735727636)
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def dadjoke(self, ctx):
		url = "https://dad-jokes.p.rapidapi.com/random/jokes"

		headers = {
		    'x-rapidapi-host': "dad-jokes.p.rapidapi.com",
		    'x-rapidapi-key': self.bot.joke_api_key
		}

		async with ClientSession() as session:
			async with session.get(url, headers=headers) as response:
				r = await response.json()
				r = r["body"][0]
				await ctx.send(f"**{r['setup']}**\n\n||{r['punchline']}||")

	@commands.command(name="Guess The Number", description="Guess the Number Game",aliases=["gn"])
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def guess_number(self, ctx, channel: discord.TextChannel, number: int ,time: TimeConverter, *,price=None):
		if number >= 10000:
			return await ctx.send("You can't set the max number same or bigger than `10000`")

		channel = channel if channel else ctx.channel
		price = price if price else "None"

		await ctx.send("Now Enter the role name or id / type None for no req you have 30s")
		try:
			message = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)
			if message.content.lower() == "none":
				role = ctx.guild.default_role
			else:
				role = await commands.RoleConverter().convert(ctx, message.content)
		except asyncio.TimeoutError:
			return await ctx.send("TimeoutError Try Again later")

		start_message = discord.Embed(title=":tada: Guess The Number", color=0xffd700)
		start_message.add_field(name="How to Play:",
			value=f"<a:yellowrightarrow:801446308778344468> You have to guess the number between 1 to {number}.\n<a:yellowrightarrow:801446308778344468> First to guess the correct number wins, you have unlimited guesses.\n<a:yellowrightarrow:801446308778344468> `{role.name}` role is required to participate in the event.\n<a:yellowrightarrow:801446308778344468> Prize of the event is {price}")
		start_message.set_footer(text="Developed and Owned by Jay & utki007")
		await channel.send(embed=start_message)
		right_number = random.randint(1, number)
		right_number = str(right_number)
		try:
			embed = discord.Embed(description=f"Right Number is `{right_number}`")
			await ctx.author.send(embed=embed)
		except discord.HTTPException:
			pass

		timer = await ctx.send("`Starting in 11s`")
		i = 10

		while i > 0:
			await timer.edit(content=f"`Starting in {i}s`")
			await asyncio.sleep(0.5)
			i = i - 1
			if i == 0:
				break
				
		start_embed2 = discord.Embed(description="Game Started", color=0xff700)
		await timer.delete()
		await channel.send(embed=start_embed2)
		overwrite = channel.overwrites_for(role)
		overwrite.send_messages = True

		await channel.set_permissions(role, overwrite=overwrite)
		try:
			winner = await self.bot.wait_for("message", check= lambda m: message.channel.id == channel.id and m.content == right_number, timeout=time)
			overwrite = channel.overwrites_for(role)
			if role == ctx.guild.default_role:
				overwrite.send_messages = False
			else:
				overwrite.send_messages = None
			await channel.set_permissions(role, overwrite=overwrite)

			done_embed = discord.Embed(title=f":tada: Congratulations, {winner.author.display_name}!",
				description="The number you guessed was right! The game has ended and the channel locked, thanks for playing!",
				color=0x11806A)

			done_embed.add_field(name="Correct Number:", value=right_number)
			done_embed.add_field(name="Winner:", value=winner.author.mention)
			done_embed.set_footer(text="Developed and Owned by Jay & utki007", icon_url="https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024")

			await winner.reply(f"{winner.author.mention}", embed=done_embed)

			dm_embed = discord.Embed(description=f"{winner.author.name}\n{winner.author.id} Is Winner")
			await ctx.author.send(embed=dm_embed)
		except asyncio.TimeoutError:
			overwrite = channel.overwrites_for(role)			
			if role == ctx.guild.default_role:
				overwrite.send_messages = False
			else:
				overwrite.send_messages = None

			await channel.set_permissions(role, overwrite=overwrite)

			lose_embed = discord.Embed(title="Time's up",
				description=f"Well Played but unfortunately None can guess the Currect Number\n Right Number was {right_number}",
				color=0xE74C3C)
			await channel.send(embed=lose_embed)

def setup(bot):
	bot.add_cog(fun(bot))