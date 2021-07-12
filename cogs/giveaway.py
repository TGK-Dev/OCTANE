import datetime
import asyncio 
import re
import random
import discord
from discord.ext import commands, tasks
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from humanfriendly import format_timespan
from discord_slash import cog_ext, SlashContext, cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandPermissionType


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
guild_ids=[785839283847954433]
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
				if message == None:
					await self.bot.give.delete(value['_id'])
					try:
					    return self.bot.giveaway.pop((value['_id']))
					except KeyError:
					    return

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
					gdata['fields'].append(field)
					await message.edit(embed=embed.from_dict(gdata))
					await message.reply("No valid entrants, so a winner not be determined!")

					await self.bot.give.delete((value['_id']))
					try:
					    return self.bot.giveaway.pop((value['_id']))
					except KeyError:
					    return

				if len(users) < value['winners']:
					embeds = message.embeds
					for embed in embeds:
						gdata = embed.to_dict()

					gdata['fields'] = []
					field = {'name': "No valid entrants!", 'value': "so a winner could not be determined!", 'inline': False}
					gdata['fields'].append(field)
					await message.edit(embed=embed.from_dict(gdata))
					await message.reply("No valid entrants, so a winner not be determined!")

					await self.bot.give.delete((value['_id']))
					try:
						return self.bot.giveaway.pop((value['_id']))
					except KeyError:
						return

				winner_list = []
				while True:
					member = random.choice(users)
					if type(member) == discord.Member:
						users.pop(users.index(member))
						winner_list.append(member.mention)
					else:
						pass
					if len(winner_list) == value['winners']:
						break

				embeds = message.embeds
				for embed in embeds:
					gdata = embed.to_dict()
				gdata['fields'] = []
				field = {'name': "Winner!", 'value': ", ".join(winner_list), 'inline': False}
				gdata['fields'].append(field)
				gdata['color'] = 15158332
				await message.edit(embed=embed.from_dict(gdata))
				reply = ",".join(winner_list)
				await message.reply(f"{reply} have successfully Won the {gdata['title']}")
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

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		giveaway = deepcopy(self.bot.giveaway)
		guild = self.bot.get_guild(payload.guild_id)
		channel = self.bot.get_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		try:
			users = await guild.fetch_member(payload.user_id)
		except discord.NotFound:
			return
		if users.id == self.bot.user.id or users == None:
			return

		if message.id in giveaway:
			data = await self.bot.give.find(message.id)
			config = await self.bot.config.find(guild.id)

			if data['r_req'] == None:
				return

			blacklist = []
			for role in config['g_blacklist']:
				role = discord.utils.get(guild.roles, id=role)
				blacklist.append(role)

			for role in blacklist:
				if role in users.roles:
					try:
						await message.remove_reaction(payload.emoji, users)
						embed= discord.Embed(title="Entry Decline",description=f"You have one the blacklist role `{role.name}` there for you cannot enter", color=0xE74C3C)
						return await users.send(embed=embed)
					except discord.HTTPException:
						return
			else:
				r_role = discord.utils.get(guild.roles, id=data['r_req'])
				b_role = discord.utils.get(guild.roles, id=data['b_role'])
				if b_role == None:
					pass
			if b_role in users.roles:
				return
			elif r_role in users.roles:
				return
			else:

				bypass = []
				for role in config['g_bypass']:
					role = discord.utils.get(guild.roles, id=role)
					bypass.append(role)

				for role in bypass:
					if role in users.roles:
						return

				try:
					await message.remove_reaction(payload.emoji, users)
					embed= discord.Embed(title="Entry Decline",description=f"You need `{r_role.name}` to Enter this [giveaway]({message.jump_url})", color=0xE74C3C)
					await users.send(embed=embed)
				except discord.HTTPException:
					pass
					
	@cog_ext.cog_slash(name="gstart",description="an giveaway commands", guild_ids=guild_ids,
		options=[
				create_option(name="time", description="how long giveaway should last", option_type=3, required=True),
				create_option(name="price", description="price of the giveaway", option_type=3, required=True),
				create_option(name="winners", description="numbers of the winners", option_type=4, required=True),
				create_option(name="r_req", description="required role to Event the giveaway",option_type=8, required=False),
				create_option(name="b_role", description="bypass role to bypass the required role",option_type=8, required=False)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889, 803230347575820289))
	async def gstart(self, ctx, time, price, winners,r_req=None, b_role=None):
		time = await TimeConverter().convert(ctx, time)
		r_req = r_req if r_req else None
		b_role = b_role if b_role else None
		descript = ""
		if r_req == None:
			descript = f'React this message to Enter!\nEnds: **{format_timespan(time)}**\nHosted by: {ctx.author.mention}'
		else:
			if b_role == None:
				descript = f'React this message to Enter!\nEnds: **{format_timespan(time)}**\nRequired Role: {r_req.mention}\nHosted by: {ctx.author.mention}'
			else:
				descript = f'React this message to Enter!\nEnds: **{format_timespan(time)}**\nRequired Role: {r_req.mention}\nBypass Role: {b_role.mention}\nHosted by: {ctx.author.mention}'
		embed = discord.Embed(title=price, color=0x3498DB, description=descript)
		embed.timestamp = (datetime.datetime.utcnow() + datetime.timedelta(seconds=time))
		embed.set_footer(text=f"Winners: {winners} | Ends At")
		#await ctx.message.delete()
		mesg = await ctx.send(embed=embed)
		data = {"_id": mesg.id,
				"guild": ctx.guild.id,
				"channel": ctx.channel.id,
				"host": ctx.author.id,
				"winners": winners,
				"end_time": time,
				"start_time": datetime.datetime.now()
				}
		try:
			data['r_req'] = r_req.id
		except:
			data['r_req'] = None

		try:
			data['b_role'] = b_role.id
		except:
			data['b_role'] = None

		await self.bot.give.upsert(data)
		self.bot.giveaway[mesg.id] = data
		await mesg.add_reaction("🎉")
		

	@cog_ext.cog_slash(name="gend", description="Focre end an giveaway", guild_ids=guild_ids,
		options=[
				create_option(name="message_id", description="message id of the giveaway", required=True, option_type=3)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889, 803230347575820289))
	async def gend(self, ctx, message_id):
		message_id = int(message_id)
		channel = ctx.channel
		message = await channel.fetch_message(message_id)
		data = await self.bot.give.find(message.id)
		if data is None:
			return await ctx.send(f"Error NO giveaway found with {message_id} Please Check your id")
		users = await message.reactions[0].users().flatten()
		users.pop(users.index(ctx.guild.me))
		#users.pop(users.index(host))
		if len(users) == 0:
			embeds = message.embeds
			for embed in embeds:
				gdata = embed.to_dict()

			gdata['fields'] = []
			field = {'name': "No valid entrants!", 'value': "so a winner could not be determined!", 'inline': False}
			gdata['fields'].append(field)
			await message.edit(embed=embed.from_dict(gdata))
			await ctx.send("No valid entrants, so a winner not be determined!")

			await self.bot.give.delete_by_id(message.id)
			try:
			    return self.bot.giveaway.pop((data['_id']))
			except KeyError:
			    return

			if len(users) < value['winners']:
				embeds = message.embeds
				for embed in embeds:
					gdata = embed.to_dict()

				gdata['fields'] = []
				field = {'name': "No valid entrants!", 'value': "so a winner could not be determined!", 'inline': False}
				gdata['fields'].append(field)
				await message.edit(embed=embed.from_dict(gdata))
				await ctx.send("No valid entrants, so a winner not be determined!")

				await self.bot.give.delete((data['_id']))
				try:
					return self.bot.giveaway.pop((data['_id']))
				except KeyError:
					return

		winner_list = []
		while True:
			member = random.choice(users)
			users.pop(users.index(member))
			winner_list.append(member.mention)
			if len(winner_list) == value['winners']:
				break

		embeds = message.embeds
		for embed in embeds:
			gdata = embed.to_dict()
		gdata['fields'] = []
		field = {'name': "Winner!", 'value': f", ".join(winner_list), 'inline': False}
		gdata['fields'].append(field)
		gdata['color'] = 15158332
		reply = ",".join(winner_list)
		await message.edit(embed=embed.from_dict(gdata))
		await ctx.send(f"{reply} you have successfully Won the {gdata['title']}")
		await self.bot.give.delete_by_id(message.id)			
		try:
			return self.bot.giveaway.pop((message.id))
		except KeyError:
			return

	@cog_ext.cog_slash(name="greroll", description="Reroll and giveaway for new winners",guild_ids=guild_ids,
		options=[
			create_option(name="message_id", description="message id of the giveaway", required=True, option_type=3),
			create_option(name="winners", description="numbers of winners", required=True, option_type=4)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889, 803230347575820289))
	async def greroll(self, ctx, message_id, winners: int):
		message_id = int(message_id)
		channel = ctx.channel
		message = await channel.fetch_message(message_id)
		if message.author.id != self.bot.user.id:
			return await ctx.send("That message is not an giveaway")
		users = await message.reactions[0].users().flatten()
		users.pop(users.index(ctx.guild.me))
		if len(users) == 0:
			return await ctx.send("No winner found as there no reactions")
		if len(users) < winners:
			return await ctx.send(f"no winners found as there no reactions to meet {winners} requirment")

		winner_list = []
		while True:
			member = random.choice(users)
			users.pop(users.index(member))
			winner_list.append(member.mention)
			if len(winner_list) == winners:
				break

		embeds = message.embeds
		for embed in embeds:
			gdata = embed.to_dict()
		gdata['fields'] = []
		field = {'name': "Winner!", 'value': f", ".join(winner_list), 'inline': False}
		gdata['fields'].append(field)
		gdata['color'] = 15158332
		reply = ",".join(winner_list)
		await message.edit(embed=embed.from_dict(gdata))
		await ctx.send(f"{reply} you have successfully Won the {gdata['title']}")

	@cog_ext.cog_slash(name="gdelete", description="Delete an giveaway", guild_ids=guild_ids,
		options=[
				create_option(name="message_id", description="message id of the giveaway message", required=True, option_type=3)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889, 803230347575820289))
	async def gdelete(self, ctx, message_id):
		message_id = int(message_id)
		data = await self.bot.give.find(message_id)
		if data is None: return await ctx.send("please Check message id")
		channel = self.bot.get_channel(data['channel'])
		message = await channel.fetch_message(data['_id'])
		await message.delete()
		await ctx.send("Your giveaway Has been delete")
		await self.bot.give.delete(message_id)
		try:
			self.bot.giveaway.pop(data['_id'])
		except KeyError:
			pass

	@cog_ext.cog_slash(name="gblacklist", description="Blacklit an role from giveaway it's an global blacklist",guild_ids=guild_ids,
		options=[
				create_option(name="role", description="Select role to blacklist it", required=True, option_type=8)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889))
	async def gblacklist(self, ctx, role):
		data = await self.bot.config.find(ctx.guild.id)
		if data is None: return await ctx.send("Your Server config was not found please run config First")
		if role.id in data['g_blacklist']:
			data['g_blacklist'].remove(role.id)
			return await ctx.send(f"{role.mention} Has been Removed from blacklist ", hidden=True)
		else:	
			data['g_blacklist'].append(role.id)
		await self.bot.config.upsert(data)
		await ctx.send(f"{role.mention} Has added to Blacklist", hidden=True)

	@cog_ext.cog_slash(name="gbypass", description="make and role to bpyass all global giveaway",guild_ids=guild_ids,
		options=[
				create_option(name="role", description="Select role make it bypass", required=True, option_type=8)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 787259553225637889))
	async def gbypass(self, ctx, role):
		data = await self.bot.config.find(ctx.guild.id)
		if data is None: return await ctx.send("Your Server config was not found please run config First")
		if role.id in data['g_bypass']:
			data['g_bypass'].remove(role.id)
			return await ctx.send(f"{role.mention} Has been Removed from the Bypass list", hidden=True)
		data['g_bypass'].append(role.id)
		await self.bot.config.upsert(data)
		await ctx.send(f"{role.mention} is added to bypass list", hidden=True)

	@cog_ext.cog_slash(name="bypasslist", description="Send the Bypass role list", guild_ids=guild_ids)
	async def bypasslist(self, ctx):
		data = await self.bot.config.find(ctx.guild.id)
		lists = []
		for role in data['g_bypass']:
			role = discord.utils.get(ctx.guild.roles, id=role)
			lists.append(role.mention)

		embed = discord.Embed(title="Bypass Role list", description=", ".join(lists), color=0x2f3136)

		await ctx.send(embed=embed)

	@cog_ext.cog_slash(name="blacklist", description="Send the blacklist role list", guild_ids=guild_ids)
	async def blacklistl(self, ctx):
		data = await self.bot.config.find(ctx.guild.id)
		lists = []
		for role in data['g_blacklist']:
			role = discord.utils.get(ctx.guild.roles, id=role)
			lists.append(role.mention)

		embed = discord.Embed(title="blacklist Role list", description=", ".join(lists), color=0x2f3136)
		await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(giveaway(bot))