import discord
import datetime
from copy import deepcopy
from discord.ext import commands

class Afk(commands.Cog, description="An Afk commands"):
	def __init__ (self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} is ready")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		afks = deepcopy(self.bot.afk_user)
		
		if message.author.id in afks:

			try:
			    self.bot.afk_user.pop(message.author.id)
			except KeyError:
			    pass#🔓

			await message.reply("your AFK stats has been Removed")
			data = await self.bot.afk.find(message.author.id)
			try:
				await message.author.edit(nick=f"{data['last_name']}")
			except:
				return await self.bot.afk.delete(message.author.id)
		

		if type(message.reference) == None:
			pass
		else:
			try:
				msg = await message.channel.fetch_message(int(message.reference.message_id))
				for key, value in afks.items():
					user = await message.guild.fetch_member(value['_id'])
					if msg.author.id == user.id:
						time = round(value['time'].timestamp())
						return await message.reply(f"{user.display_name} is afk {value['message']} -<t:{time}:R> <t:{time}:f>", mention_author=False)
			except:
				pass
		if len(message.mentions) == 0:
			return
		else:
			for key, value in afks.items():
				user = await message.guild.fetch_member(value['_id'])
				if user in message.mentions:
					time = round(value['time'].timestamp())
					await message.reply(f"User is afk {value['message']} -<t:{time}:R> <t:{time}:f>", mention_author=False)
		
	@commands.command(name="afk", description="set your stats afk with this command")
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916, 818129661325869058))
	@commands.cooldown(1, 300, commands.BucketType.user)
	async def afk(self, ctx, message=None):
		message = message if message else "⠀"
		data = {'_id': ctx.author.id,
				'message': message,
				'last_name': ctx.author.display_name,
				'time': datetime.datetime.now()}
		try:
			await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
		except:
			pass
		await ctx.send("I have set your stats as afk")
		await self.bot.afk.upsert(data)
		self.bot.afk_user[ctx.author.id] = data

def setup(bot):
	bot.add_cog(Afk(bot))
    
