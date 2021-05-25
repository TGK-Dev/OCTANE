import asyncio
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
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option

guild_ids = [797920317871357972, 785839283847954433]

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
description= "Fun commands"
word_list =  ["hello", "Game", "pizzaz", "queazy", "puzzle", "Excuse", 
			"marbles", "amber", "actually", "address", "administration", "admit", 
			"analysis", "anything", "authority", "available", "beautiful", "beyond",
			"building", "campaign", "candidate", "certainly", "collection", "commercial",
			"community", "conference", "Congress", "Democrat", "democratic", "development",
			"difference", "discussion", "disease", "economic", "economy", "education", "employee",
			"environment", "environmental", "everybody", "everyone", "experience", "financial", "generation",
			"government", "important", "improve", "improve", "interesting", "international", "knowledge", 
			"machine", "magazine", "management", "movement", "operation", "opportunity", "organization",
			"participant", "particularly", "performance", "population", "president", "production", 
			"professional", "professor", "recognize", "relationship", "responsibility",]

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

	def check_owner(ctx):
		return ctx.author.bot == 488614633670967307 or 301657045248114690

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.command(name="8ball", description="old School 8ball game", usage="[question]")
	@commands.cooldown(2, 60, commands.BucketType.user)
	async def ball(self, ctx, *, question):
		await ctx.send(bot.ball.response(question))	

	@commands.command(name="dadjoke", description="Send a dad Joke", usage="" ,aliases=["djoke"])
	@commands.check(check_owner)
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

	@commands.command(name="Guess The Number", description="Guess the Number Game", usage="[max] [time] [price] ", aliases=["gn"])
	@commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916)
	async def guess_number(self, ctx, maxn , time: TimeConverter=None, *,price=None):
		if maxn > 10000:
			return await ctx.send("you can't big number then 10000")

		right_num = random.randint(1, maxn)
		price = price if price else "None"
		time = time if time else 3600
		game_channel =  self.bot.get_channel(835138688668401675)
		right_backup = self.bot.get_channel(834847353436373012)


		await ctx.send("Please Enter required role or Type None to set it no requiment")
		try:
			message = await self.bot.wait_for("message", check= lambda m: m.channel.id == game_channel.id, timeout=60)
			if message.content.lower() == "none":
				role = ctx.guild.default_role
			else:				
				role = await commands.RoleConverter().convert(ctx, message.content)

		except asyncio.TimeoutError:
			return await ctx.send("Time Out Please Try Again")



		start_em = discord.Embed(title=":tada: Guess The Number")
		start_em.add_field(name="How to Play:",
			value=f"· I've thought of a number between 1 and {maxn}.\n· First person to guess the number wins!\n· You have UNLIMITED guesses.\n·You Must have {role.mention} To Enter\n·You have {int((time/60)/60)}hour to Guess the right Number\n· Starting game in 10 seconds\n·The Price of this round is `{price}`")
		start_em.set_footer(text="Developed and Owned by Jay & utki007")
		await game_channel.send(embed=start_em)
		
		try:
			await ctx.author.send(f" The Currect Number Is `{right_num}`")
		except discord.HTTPException:
			await right_backup.send(right_num)

		await asyncio.sleep(7)
		mess1 = await ctx.send("`Starting IN 3`")

		await mess1.edit(content="`Starting IN 2`")
		await asyncio.sleep(1)

		await mess1.edit(content="`Starting IN 1`")
		await asyncio.sleep(1)
		await mess1.delete()
		
		sem = discord.Embed(description="Game Started", color=0xF1C40F)
		await ctx.send(embed=sem)

		overwrite = game_channel.overwrites_for(role)
		overwrite.send_messages = True
		await game_channel.set_permissions(role, overwrite=overwrite)

		try:
			message = await self.bot.wait_for("message", check= lambda m: m.content.startswith(f"{right_num}") and m.channel.id == game_channel.id, timeout=time)
			done_overwrite = game_channel.overwrites_for(role)
			done_overwrite.send_messages = False

			await game_channel.set_permissions(role, overwrite=done_overwrite)

			done_embed = discord.Embed(title=f":tada: Congratulations, {message.author.display_name}!",
				description="The number you guessed was right! The game has ended and the channel locked, thanks for playing!",
				color=0x11806A)

			done_embed.add_field(name="Correct Number:", value=right_num)
			done_embed.add_field(name="Winner:", value=message.author.mention)
			done_embed.set_footer(text="Developed and Owned by Jay & utki007")

			await message.reply(f"{message.author.mention}", embed=done_embed)

			await ctx.author.send(f"`{message.author.name}\n{message.author.id}`\n Is guessed correct Number")
	
		except asyncio.TimeoutError:

			fail_overwrite = game_channel.overwrites_for(role)
			fail_overwrite.send_messages = False
			await game_channel.set_permissions(role, overwrite=fail_overwrite)
			
			lose_embed = discord.Embed(title="Time's up",
				description="Well Played but unfortunately None can guess the Currect Number",
				color=0xE74C3C)
			await game_channel.send(embed=lose_embed)

	@cog_ext.cog_slash(name="Guess_Number",
		description="Guess the Number Game",
		guild_ids=guild_ids,
		options=[
			create_option(
				name="maxn",
				description="max Range of the Guesses",
				option_type=4,
				required=True
			),
			create_option(
				name="time",
				description="Time limit of the game",
				option_type=3,
				required=True
			),
			create_option(
				name="price",
				description="Winner Price",
				option_type=3,
				required=False
			),
			create_option(
				name="role",
				description="required Role for Game",
				option_type=8,
				required=False
			)

		]
	)
	@commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376)
	async def Guess_Number(self, ctx, maxn=None, time=None, price=None, role=None):
		if maxn > 10000:
			return await ctx.send("you can't big number then 10000")

		role = role if role else ctx.guild.default_role
		time = await TimeConverter().convert(ctx, time)
		right_num = random.randint(1, maxn)
		price = price if price else "None"
		time = time if time else 3600
		game_channel =  self.bot.get_channel(835138688668401675)
		right_backup = self.bot.get_channel(834847353436373012)

		start_em = discord.Embed(title=":tada: Guess The Number")
		start_em.add_field(name="How to Play:",
			value=f"· I've thought of a number between 1 and {maxn}.\n· First person to guess the number wins!\n· You have UNLIMITED guesses.\n·You Must have {role.mention} To Enter\n·You have {int((time/60)/60)}hour to Guess the right Number\n· Starting game in 10 seconds\n·The Price of this round is `{price}`")
		start_em.set_footer(text="Developed and Owned by Jay & utki007")
		await game_channel.send(embed=start_em)
		
		try:
			await ctx.author.send(f" The Currect Number Is `{right_num}`")
		except discord.HTTPException:
			await right_backup.send(right_num)

		await asyncio.sleep(10)
		
		sem = discord.Embed(description="Game Started", color=0xF1C40F)
		await game_channel.send(embed=sem)

		overwrite = game_channel.overwrites_for(role)
		overwrite.send_messages = True
		await game_channel.set_permissions(role, overwrite=overwrite)

		try:
			message = await self.bot.wait_for("message", check= lambda m: m.content.startswith(f"{right_num}") and m.channel.id == game_channel.id, timeout=time)
			done_overwrite = game_channel.overwrites_for(role)
			done_overwrite.send_messages = False

			await game_channel.set_permissions(role, overwrite=done_overwrite)

			done_embed = discord.Embed(title=f":tada: Congratulations, {message.author.display_name}!",
				description="The number you guessed was right! The game has ended and the channel locked, thanks for playing!",
				color=0x11806A)

			done_embed.add_field(name="Correct Number:", value=right_num)
			done_embed.add_field(name="Winner:", value=message.author.mention)
			done_embed.set_footer(text="Developed and Owned by Jay & utki007")

			await message.reply(f"{message.author.mention}", embed=done_embed)

			await ctx.author.send(f"`{message.author.name}\n{message.author.id}`\n Is guessed correct Number")
	
		except asyncio.TimeoutError:

			fail_overwrite = game_channel.overwrites_for(role)
			fail_overwrite.send_messages = False
			await game_channel.set_permissions(role, overwrite=fail_overwrite)
			
			lose_embed = discord.Embed(title="Time's up",
				description="Well Played but unfortunately None can guess the Currect Number",
				color=0xE74C3C)
			await game_channel.send(embed=lose_embed)



	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		trinnger1 = random.randint(500,550)
		trinnger2 = random.randint(500,1000)
		channel = message.channel

		if channel.id in [785847439579676672, 785873318158008330, 789867479887249410, 792246185238069249]


			if trinnger1 > trinnger2:
				word = random.choice(word_list)
				sword = shuffle(word)
				ssword = shuffle(sword)
				print(word)
				embed = discord.Embed(
					description=f"Unscramble this word `{ssword}` Frist person To Answer it is winner",
					color=0x2ECC71)
				embed.set_footer(text="Still In Ealry Stage This Might Get Change")
				edit_emved = await channel.send("<:Event_start:846714727568637964>| Uncommon Event!",embed=embed)
				try:
					
					gword = await self.bot.wait_for("message", check=lambda x: x.channel.id == message.channel.id and x.content.lower() == word.lower(), timeout=15)

					winner_embed = discord.Embed(title="We Have an Winner",
						description=f"{gword.author.mention} Was Right no dout your smart Right Word is `{word}`", color=0x3498DB)

					end_embed = discord.Embed(title="Event Has expired",
						description=f"Unscramble this word `{sword}` Frist person To Answer it is winner\n\
						Winner is the {gword.author.mention}",
						color=0xE74C3C)
					end_embed.set_footer(text="Still In Ealry Stage This Might Get Change")

					await edit_emved.edit(content="<:Event_end:846715951089057863>| Expired",embed=end_embed)
					await gword.reply(embed=winner_embed)
				except asyncio.TimeoutError:

					fail_embed = discord.Embed(title="Event Has expired",
						description=f"Unscramble this word `{sword}` Frist person To Answer it is winner\n\
						no is smart enough to Get Right Word Better Luck next time",
						color=0xE74C3C)
					fail_embed.set_footer(text="Still In Ealry Stage This Might Get Change")
					await edit_emved.edit(content="<:Event_end:846715951089057863>| Expired", embed=fail_embed)

def setup(bot):
	bot.add_cog(fun(bot))

"""
@commands.Cog.listener()
async def on_message(self, message):
	trinnger1 = random.randint(1,100)
	trinnger2 = random.randint(1,100)

	print(f"trinnger1 = {trinnger1}")
	print(f"trinnger2 = {trinnger2}")
	print(f"{int(trinnger2/trinnger1)}")

	if message.author.bot:
		return

	if int(trinnger2/trinnger1) == 0:

		embed = discord.Embed(title="Random Chat event", 
			description="server Is getting Raided type ` ban ` to ban them",
			color=0x2ECC71)

		await message.channel.send(embed=embed)
		try:
			win_mess = await self.bot.wait_for("message", check= lambda m: m.content.startswith("ban") or m.content.startswith("Ban"), timeout=15)
			win_embed = discord.Embed(title="Random Chat event",
				description=f"All Raider are now Banned Thanks to {win_mess.author.mention}",
				color=0xE74C3C)

			await win_mess.channel.send("Event is Over", embed=win_embed)

		except asyncio.TimeoutError:
			
			lose_embed = discord.Embed(title="Random Chat Event",
				description="Server is Now Raided",
				color=0xE74C3C)

			await message.channel.send(embed=embed)

	elif int(trinnger2/trinnger1) == 5:

		embed = discord.Embed(title="Random Chat event", 
			description="React this message with :thumbsup: Frist is The Winner",
			color=0x2ECC71)

		rect_mess = await message.channel.send(embed=embed)
		try:
			reaction,  = await self.bot.wait_for("reaction_add", check= lambda reaction: reaction.RawReactionActionEvent.message_id == rect_mess.id and reaction.emoji == '👍', timeout=15)
			win_embed = discord.Embed(title="Random Chat event",
				description=f"the <@{reaction.user_id}> is Fast As Fast",
				color=0xE74C3C)

			await win_mess.channel.send("Event is Over", embed=win_embed)

		except asyncio.TimeoutError:
			
			lose_embed = discord.Embed(title="Random Chat Event",
				description="Server is Now Raided",
				color=0xE74C3C)

			await message.channel.send(embed=embed)
"""