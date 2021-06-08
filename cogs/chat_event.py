import asyncio
import datetime
import discord
import random
import json
from string_utils import shuffle , reverse
from discord.ext import commands
from utils.util import Pag

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
			"professional", "professor", "recognize", "relationship", "responsibility"]

description= "Random Chat events"
class Event(commands.Cog,  description=description):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	def is_me():
	    def predicate(ctx):
	        return ctx.message.author.id in [488614633670967307 , 301657045248114690]
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

	@commands.Cog.listener()
	async def on_message(self, message):

		if message.author.bot:
			return

		if message.author.id in self.bot.blacklist_user:
		    return

		trinnger1 = random.randint(0,550)
		trinnger2 = random.randint(530,1000)

		trinnger3 = random.randint(1,50)
		trinnger4 = random.randint(40,500)
		channel = message.channel

		if channel.id in self.bot.event_channel:

			if trinnger1 > trinnger2:
				word = random.choice(word_list)
				sword = shuffle(word)
				ssword = shuffle(sword)
				right_channel = self.bot.get_channel(846847052389941248)
				hint = slice(0,3)
				todo = await right_channel.send(word)
				embed = discord.Embed(
					description=f"Unscramble this word `{ssword}` Frist person To Answer it is winner\n\
					***Hint***: `{word[hint]}`",
					color=0x2ECC71)
				embed.set_footer(text="Still In Ealry Stage This Might Get Change")
				edit_emved = await channel.send("<:Event_start:846714727568637964>| Uncommon Event!",embed=embed)
				try:
					
					gword = await self.bot.wait_for("message", check=lambda x: x.channel.id == message.channel.id and x.content.lower() == word.lower(), timeout=15)

					winner_embed = discord.Embed(title="Event Has expired",
						description=f"{gword.author.mention} has successfully guessed the word!!!\n\
						Right word Was: `{word}`", color=0x3498DB)

					end_embed = discord.Embed(title="Event Has expired",
						description=f"Unscramble this word `{sword}` Frist person To Answer it is winner\n\
						Winner is the {gword.author.mention}",
						color=0xE74C3C)
					end_embed.set_footer(text="Still In Ealry Stage This Might Get Change")

					await edit_emved.edit(content="<:Event_end:846715951089057863>| Expired",embed=end_embed)
					await gword.reply(embed=winner_embed)
					await todo.delete()
					data = await self.bot.score.find(gword.author.id)

					if data is None:
						data = {"_id": gword.author.id, "score": 0}
					data["score"] += 1
					await self.bot.score.upsert(data)
				except asyncio.TimeoutError:

					fail_embed = discord.Embed(title="Event Has expired",
						description=f"Nobody is smart enough to get the correct answer,\nright word was `{word}`",
						color=0xE74C3C)
					fail_embed.set_footer(text="Still In Ealry Stage This Might Get Change")
					await todo.delete()
					await edit_emved.reply(content="<:Event_end:846715951089057863>| Expired", embed=fail_embed)

			elif trinnger3 > trinnger4:
				word = random.choice(word_list)
				sword = reverse(word)
				embed = discord.Embed(
					description=f"Type this word `{word}` in reverse, Frist person To Answer it is winner",
					color=0x2ECC71)
				embed.set_footer(text="Still In Ealry Stage This Might Get Change")
				edit_emved = await channel.send("<:Event_start:846714727568637964>| Uncommon Event!",embed=embed)
				try:
					gword = await self.bot.wait_for("message", check=lambda x: x.channel.id == message.channel.id and x.content.lower() == sword.lower(), timeout=20)
					winner_embed = discord.Embed(title="Event Has expired",
						description=f"{gword.author.mention} has successfully Type the word in reverse!!!", color=0x3498DB)
					embed.set_footer(text="Still In Ealry Stage This Might Get Change")

					end_embed = discord.Embed(title="Event Has expired",
						description=f"Type this word `{word}` in reverse, Frist person To Answer it is winner\n\
						Winner is the {gword.author.mention}",color=0xE74C3C)						
					await edit_emved.edit(content="<:Event_end:846715951089057863>| Expired",embed=end_embed)
					await gword.reply(embed=winner_embed)
					data = await self.bot.score.find(gword.author.id)

					if data is None:
						data = {"_id": gword.author.id, "score": 0}
					data["score"] += 1
					await self.bot.score.upsert(data)

				except asyncio.TimeoutError:
					fail_embed = discord.Embed(title="Event Has expired",
						description=f"Nobody is Fast enough to Type word in reverse,`",
						color=0xE74C3C)
					fail_embed.set_footer(text="Still In Ealry Stage This Might Get Change")
					await edit_emved.reply(content="<:Event_end:846715951089057863>| Expired", embed=fail_embed)					

	@commands.group(name="event", description="Server Chat events Info", invoke_without_command = True)
	async def event(self, ctx):
		embed = discord.Embed(title="Totoal Event Lists",
			description="1. Word Unscrambler\n\
			2.Type Word In revers")
		embed.set_footer(text="More Events Are Coming Stay Tune")
		await ctx.send(embed=embed)

	@event.command(name="add", description="Add Channe to Event Whitelist")
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636), is_me())
	async def add(self, ctx, traget: discord.TextChannel):
		data = await self.bot.event.find(ctx.guild.id)

		if data is None:
			data = {"_id": ctx.guild.id, "event_channels": []}

		data["event_channels"].append(traget.id)
		await self.bot.event.upsert(data)
		self.bot.event_channel.clear()

		channels = await self.bot.event.get_all()
		channel = json.dumps(channels[0]["event_channels"])
		self.bot.event_channel = json.loads(channel)

		await ctx.send(f"I have added `{traget.name}` in event Whitelist")

	@event.command(name="remove", description="Remove Channel from Whitelist")
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636), is_me())
	async def remove(self, ctx, traget: discord.TextChannel):
		data = await self.bot.event.find(ctx.guild.id)

		if data is None:
			return await ctx.send("YOu don't have any channel for the Event Setup Yet use `event add <chanenl>` to add one")
		data["event_channels"].remove(traget.id)
		await self.bot.event.upsert(data)
		self.bot.event_channel.clear()

		channels = await self.bot.event.get_all()
		channel = json.dumps(channels[0]["event_channels"])
		self.bot.event_channel = json.loads(channel)

		await ctx.send(f"I have Remove the `{traget.name}` from the Whitelist.")

	@event.command(name="list", description="List of Whitelist Channels")
	async def list(self, ctx):
		datas = await self.bot.event.find(ctx.guild.id)

		if datas is None:
			return await ctx.send("Server don't have any channel for the Event Setup Yet use `event add <chanenl>` to add one")
		embed = discord.Embed(title="Whitelist Channels", description="")
		try:
			i = 1
			for data in datas["event_channels"]:
				channel = self.bot.get_channel(data)
				embed.description += f"{i}.{channel.mention}\n"
				i += 1

		except:
			pass
		await ctx.send(embed=embed)

	@event.command(name="score", description="See Your or Other Score for Chat events")
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def score(self, ctx, member: discord.Member=None):
		if ctx.channel.id != 785849567518130176:
			return await ctx.send("please Use <#785849567518130176> for this command")
		member = member if member else ctx.author
		data = await self.bot.score.find(member.id)

		if data is None:
			embed = discord.Embed(description="User Score Is not Found Maybe he never won who know?",color=0xE67E22)
			return await ctx.send(embed=embed)
		#score = data["score"]
		embed = discord.Embed(description=f"The user {member.mention} Has Total: {data['score']}", color=0x2ECC71)
		await ctx.send(embed=embed)

	@event.command(name="leaderboard", description="Chat event leaderboard", aliases=["lb"])
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def leaderboard(self, ctx):
		if ctx.channel.id != 785849567518130176:
			return await ctx.send("please Use <#785849567518130176> for this command")
		scores = await self.bot.score.get_all()

		scores = sorted(scores, key=lambda x: x["score"], reverse=True)
		i = 1

		pages = []
		for data in scores:
			description = f"""
			{i}.Member: <@{data['_id']}>
			Total Score: {data['score']}
			"""
			i += 1
			pages.append(description)

		await Pag(
			title=f"Chat event leaderboard",
			colour=0xCE2029,
			entries=pages,
			length=5
		).start(ctx)

def setup(bot):
    bot.add_cog(Event(bot))



