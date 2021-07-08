import datetime
import asyncio 
import re
import random
import discord
from discord.ext import commands, tasks
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from humanfriendly import format_timespan


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

class TimeConverter(commands.Converter):
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

class giveaway(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.giveaway_task = self.check_givaway.start()

	def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307 , 301657045248114690]
        return commands.check(predicate)


	@tasks.loop(seconds=5)
	async def check_givaway(self):
		currentTime = datetime.datetime.now()
		gives = deepcopy(self.bot.giveaway)
		for key, value in gives.items():

			ftime = value['start_time'] + relativedelta(seconds=value['end_time'])

			if currentTime >= ftime:
				channel = self.bot.get_channel(value['channel'])
				guild = self.bot.get_guild(value['guild'])
				message = await channel.fetch_message(value['_id'])
				host = await guild.fetch_member(value['host'])
				users = await message.reactions[0].users().flatten()
				users.pop(users.index(guild.me))
				#users.pop(users.index(host))
				if len(users) == 0:
					embeds = message.embeds
					for embed in embeds:
						gdata = embed.to_dict()

					gdata['fields'] = []
					field = {'name': "No valid entrants!", 'value': "so a winner could not be determined!", 'inline': False}
					gdata['fields'].append(fields)
					await message.edit(embed=embed.from_dict(gdata))
					await message.reply("No valid entrants, so a winner not be determined!")

					await self.bot.free.delete(message.id)
					try:
					    return self.bot.giveaway.pop(message)
					except KeyError:
					    return

				winner = random.choice(users)
				embeds = message.embeds
				for embed in embeds:
					gdata = embed.to_dict()
				gdata['fields'] = []
				field = {'name': "Winner!", 'value': f"<@{winner.id}>", 'inline': False}
				gdata['fields'].append(field)
				gdata['color'] = 15158332
				await message.edit(embed=embed.from_dict(gdata))
				await message.reply(f"{winner.mention} you have successfully Won the {gdata['title']}")
				await self.bot.give.delete_by_id(message.id)			
				try:
				    return self.bot.giveaway.pop((value['_id']))
				except KeyError:
				    return

	@check_givaway.before_loop
	async def before_check_givaway(self):
		await self.bot.wait_until_ready()

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} has been loaded \n------")


	@commands.command(name="giveaway", description="giveaway commands Testing")
	@commands.check_any(is_me())
	async def giveaway(self, ctx, time:TimeConverter, *,price):
		embed = discord.Embed(title=price, color=0x3498DB,
			description=f"React this message to Enter!\nEnds: {format_timespan(time)})\nHosted by: {ctx.author.mention}")
		await ctx.message.delete()
		mesg = await ctx.send(embed=embed)
		data = {"_id": mesg.id,
				"guild": ctx.guild.id,
				"channel": ctx.channel.id,
				"end_time": time,
				"host": ctx.author.id,
				"start_time": datetime.datetime.now()
				}
		await self.bot.give.upsert(data)
		self.bot.giveaway[mesg.id] = data
		await mesg.add_reaction("🎉")

def setup(bot):
    bot.add_cog(giveaway(bot))

