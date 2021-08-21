import datetime
import asyncio 
import re
import random
import discord
from discord.ext import commands, tasks
from copy import deepcopy
import datetime
from dateutil.relativedelta import relativedelta
from humanfriendly import format_timespan
from discord_slash import cog_ext, SlashContext, cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandPermissionType
from utils.util import Amari


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
guild_ids=[785839283847954433]

amari_api = Amari()
owner_perms = {
	785839283847954433:[
	create_permission(488614633670967307, SlashCommandPermissionType.USER, True),
	create_permission(785842380565774368, SlashCommandPermissionType.ROLE, True),
	]
}

mod_perms = {
	785839283847954433:[
	create_permission(488614633670967307, SlashCommandPermissionType.USER, True),
	create_permission(785842380565774368, SlashCommandPermissionType.ROLE, True),
	create_permission(803635405638991902, SlashCommandPermissionType.ROLE, True),
	create_permission(799037944735727636, SlashCommandPermissionType.ROLE, True),
	create_permission(785845265118265376, SlashCommandPermissionType.ROLE, True),
	create_permission(787259553225637889, SlashCommandPermissionType.ROLE, True),
	create_permission(843775369470672916, SlashCommandPermissionType.ROLE, True),
	create_permission(803230347575820289, SlashCommandPermissionType.ROLE, True)
	]
}


admin_perms = {
	785839283847954433: [
	create_permission(488614633670967307, SlashCommandPermissionType.USER, True),
	create_permission(785842380565774368, SlashCommandPermissionType.ROLE, True),
	create_permission(803635405638991902, SlashCommandPermissionType.ROLE, True),
	create_permission(799037944735727636, SlashCommandPermissionType.ROLE, True),
	create_permission(785845265118265376, SlashCommandPermissionType.ROLE, True),
	]
}
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
		self.start = False
	def cog_unload(self):
		self.giveaway_task.cancel()
	
	@tasks.loop(seconds=10)
	async def check_givaway(self):
		currentTime = datetime.datetime.now()
		giveaway = deepcopy(self.bot.giveaway)
		for key, value in giveaway.items():
			ftime = value['start_time'] + relativedelta(seconds=value['end_time'])

			if currentTime >= ftime and self.start == False:
				print(value)
				start = True
				guild = self.bot.get_guild(value['guild'])
				channel = guild.get_channel(value['channel'])
				message = await channel.fetch_message(value['_id'])
				data = await self.bot.give.find(message.id)
				host = guild.get_member(value['host'])

				winner_list = []
				entries = data['entries']
				users = await message.reactions[0].users().flatten()
				users.pop(users.index(guild.me))
				while True:
					if len(data['entries']) == 0: break
					member = random.choice(data['entries'])
					data['entries'].remove(member)
					member = guild.get_member(member)
					if member in users:
						winner_list.append(member.mention)
					if len(winner_list) == data['winners']:
							break

				if len(winner_list) < value['winners']:
					embeds = message.embeds
					for embed in embeds:
						edict = embed.to_dict()

					edict['title'] = f"{edict['title']} • Giveaway Has Endded"
					edict['color'] = 15158332
					await message.edit(embed=embed.from_dict(edict))
					small_embed = discord.Embed(description=f"No valid [entrants]({message.jump_url}), so winner not be determined!", color=0x2f3136)
					await message.reply(embed=small_embed)
					await self.bot.give.delete(message.id)
					try:
						self.start = False
						return self.bot.giveaway.pop((data['_id']))
					except KeyError:
						self.start = False
						return 

				if len(winner_list) >= value['winners']:
					embeds = message.embeds
					for embed in embeds:
						gdata = embed.to_dict()
					reply = ",".join(winner_list)
					small_embed = discord.Embed(description=f"Total Entries: [{len(entries)}]({message.jump_url})")
					await message.reply(
					f"**Giveaway Has Endded**\n<a:winners_emoji:867972307103141959>  **Prize**      <a:yellowrightarrow:801446308778344468> {gdata['title']}\n─────────────────────\n<a:pandaswag:801013818896941066>   **Host**      <a:yellowrightarrow:801446308778344468> {host.display_name}\n─────────────────────\n<a:winner:805380293757370369>  **Winner** <a:yellowrightarrow:801446308778344468> {reply}\n─────────────────────\n", embed=small_embed)

					gdata['title'] = f"{gdata['title']} • Giveaway Has Endded"
					gdata['color'] = 15158332
					field = {'name': "Winner!", 'value': ", ".join(winner_list), 'inline': False}
					try:
						gdata['fields'].append(field)
					except KeyError:
						gdata['fields'] = []
						gdata['fields'].append(field)
					await message.edit(embed=embed.from_dict(gdata))
					await self.bot.give.delete(message.id)
					try:
						self.start = False
						self.bot.giveaway.pop(message.id)
					except KeyError:
						self.start = False
						pass

	@check_givaway.before_loop
	async def before_check_givaway(self):
		await self.bot.wait_until_ready()
	
	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} has been loaded \n------")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if payload.emoji == "🎉": return 
		channel = self.bot.get_channel(payload.channel_id)
		guild = self.bot.get_guild(payload.guild_id)
		message = await channel.fetch_message(payload.message_id)
		bypass = False
		if message.author != self.bot.user:
			return
		try:
			user = await guild.fetch_member(payload.user_id)
		except:
			return

<<<<<<< Updated upstream
		if message.id in giveaway:
			data = await self.bot.give.find(message.id)
			config = await self.bot.config.find(guild.id)

			if data['r_req'] == None:
				for role_multi in config['role_multi']:
					role = discord.utils.get(guild.roles,id=role_multi['role_id'])
					if role in users.roles:
						i = 1
						while i <= role_multi['multi']:
							data['entries'].append(users.mention)
							i += 1
						return await self.bot.give.upsert(data)
				data['entries'].append(users.mention)
				return await self.bot.give.upsert(data)

=======
		if user.id == self.bot.user.id:
			return
		required = await self.bot.give.find(message.id)
		config = await self.bot.config.find(message.guild.id)
>>>>>>> Stashed changes

		if config['g_blacklist']:
			for role in config['g_blacklist']:
				role = discord.utils.get(guild.roles, id=role)
				if role in user.roles:
					try:
						embed = discord.Embed(title="Entry Decline",description=f"You have one the blacklist role `{role.name}` there for you cannot enter", color=0xE74C3C)
						await user.send(embed=embed)
						return await message.remove_reaction(payload.emoji, user)
					except discord.HTTPException:
						pass
					return await message.remove_reaction(payload.emoji, user)
		
		if config['g_bypass']:
		
			for role in config['g_bypass']:
<<<<<<< Updated upstream
				role = discord.utils.get(guild.roles, id=role)
				if role in users.roles:
					for role_multi in config['role_multi']:
						role = discord.utils.get(guild.roles,id=role_multi['role_id'])
						if role in users.roles:
							i = 1
							while i <= role_multi['multi']:
								data['entries'].append(users.mention)
								i += 1
							return await self.bot.give.upsert(data)
					data['entries'].append(users.mention)
					return await self.bot.give.upsert(data)

			r_role = discord.utils.get(guild.roles, id=data['r_req'])

			if r_role in users.roles:
				for role_multi in config['role_multi']:
					role = discord.utils.get(guild.roles,id=role_multi['role_id'])
					if role in users.roles:
						i = 1
						while i <= role_multi['multi']:
							data['entries'].append(users.mention)
							i += 1
						return await self.bot.give.upsert(data)

				data['entries'].append(users.mention)
				return await self.bot.give.upsert(data)

			b_role = discord.utils.get(guild.roles, id=data['b_role'])
			if b_role == None:
				try:
					await message.remove_reaction(payload.emoji, users)
					embed = discord.Embed(title="Entry Decline",description=f"You need `{r_role.name}` to Enter this [giveaway]({message.jump_url})", color=0xE74C3C)
					await users.send(embed=embed)
				except discord.HTTPException:
					return
			if type(b_role) == discord.Role:
				if role in users.roles:
					i = 1
					while i <= role_multi['multi']:
						data['entries'].append(users.mention)
						i += 1
					return await self.bot.give.upsert(data)
				data['entries'].append(users.mention)
				return await self.bot.give.upsert(data)
=======
				bypass_role = discord.utils.get(guild.roles, id=role)
				if bypass_role in user.roles:
					bypass = True
>>>>>>> Stashed changes

		if required['r_req'] and bypass == False:
			rrole = discord.utils.get(guild.roles, id=required['r_req'])
			if rrole in user.roles:
				pass
			else:
				if required['b_role']:
					role = discord.utils.get(guild.roles, id=required['b_role'])
					if role in user.roles:
						pass
					else:
						embed = discord.Embed(title="Entery Decline:",
							description=f"your entriy for this [Giveaway]({message.jump_url}) has been decline\nReason: You don't have Required Role `{rrole.name}`",color=0xE74C3C)
						embed.timestamp = datetime.datetime.utcnow()
						embed.set_footer(text=guild.name,icon_url=guild.icon_url)
						try:
							await user.send(embed=embed)
						except discord.HTTPException:
							pass
						await message.remove_reaction(payload.emoji, user)
				else:
					embed = discord.Embed(title="Entery Decline:",
						description=f"your entriy for this [Giveaway]({message.jump_url}) has been decline\nReason: You don't have Required Role `{rrole.name}`",color=0xE74C3C)
					embed.timestamp = datetime.datetime.utcnow()
					embed.set_footer(text=guild.name,icon_url=guild.icon_url)
					try:
						await user.send(embed=embed)
					except discord.HTTPException:
						pass
					return await message.remove_reaction(payload.emoji, user)

		if required['amari_level'] and bypass == False:
			user_level = await amari_api.get_amari_rank(user.guild.id, user)
			if user_level < required['amari_level']:
				if required['b_role']:
					role = discord.utils.get(guild.roles, id=required['b_role'])
					if role in user.roles:
						pass
					else:
						embed = discord.Embed(title="Entery Decline:",
							description=f"Your Entery for this [Giveaway]({message.jump_url}) has been decline\nReason:You don't have enough amari level your short {required['amari_level'] - user_level}  Level enter", color=0xE74C3C)
						embed.timestamp = datetime.datetime.utcnow()
						embed.set_footer(text=guild.name,icon_url=guild.icon_url)
						try:
							await user.send(embed=embed)
						except discord.HTTPException:
							pass
						return await message.remove_reaction(payload.emoji, user)
				else:
					embed = discord.Embed(title="Entery Decline:",
						description=f"Your Entery for this [Giveaway]({message.jump_url}) has been decline\nReason:You don't have enough amari level your short {required['amari_level'] - user_level}  Level enter", color=0xE74C3C)
					embed.timestamp = datetime.datetime.utcnow()
					embed.set_footer(text=guild.name,icon_url=guild.icon_url)
					try:
						await user.send(embed=embed)
					except discord.HTTPException:
						pass
					return await message.remove_reaction(payload.emoji, user)

		if required['weekly_amari'] and bypass == False:
			user_level = await amari_api.get_weekly_rank(user.guild.id, user)
			if user_level < required['weekly_amari']:
				if required['b_role']:
					role = discord.utils.get(guild.roles, id=required['b_role'])
					if role in user.roles:
						pass
					else:
						embed = discord.Embed(title="Entery Decline:",
							description=f"Your Entery for this [Giveaway]({message.jump_url}) has been decline\nReason:You don't have enough weekly amari you still need {required['weekly_amari'] - user_level} To enter", color=0xE74C3C)
						embed.timestamp = datetime.datetime.utcnow()
						embed.set_footer(text=guild.name,icon_url=guild.icon_url)
						try:
							await user.send(embed=embed)
						except discord.HTTPException:
							pass
						return await message.remove_reaction(payload.emoji, user)
				else:
					embed = discord.Embed(title="Entery Decline:",
						description=f"Your Entery for this [Giveaway]({message.jump_url}) has been decline\nReason:You don't have enough weekly amari you still need {required['weekly_amari'] - user_level} To enter", color=0xE74C3C)
					embed.timestamp = datetime.datetime.utcnow()
					embed.set_footer(text=guild.name,icon_url=guild.icon_url)
					try:
						await user.send(embed=embed)
					except discord.HTTPException:
						pass
					return await message.remove_reaction(payload.emoji, user)

		for role_multi in config['role_multi']:
			role = discord.utils.get(guild.roles, id=role_multi['role_id'])
			if role in user.roles:
				i = 0
				while True:
					required['entries'].append(user.id)
					i += 1
					
					if i == role_multi['multi']:
						await self.bot.give.upsert(required)
						self.bot.giveaway[message.id] = required

		required['entries'].append(user.id)
		await self.bot.give.upsert(required)
		self.bot.giveaway[message.id] = required
	

	@cog_ext.cog_slash(name="gstart",description="an giveaway commands", guild_ids=guild_ids, default_permission=False, permissions=mod_perms,
		options=[
				create_option(name="time", description="how long giveaway should last", option_type=3, required=True),
				create_option(name="price", description="price of the giveaway", option_type=3, required=True),
				create_option(name="winners", description="numbers of the winners", option_type=4, required=True),
				create_option(name="r_req", description="required role to Event the giveaway",option_type=8, required=False),
				create_option(name="b_role", description="bypass role to bypass the required role",option_type=8, required=False),
				create_option(name="amari_level", description="set required amari level",option_type=4, required=False),
				create_option(name="weekly_amari", description="set giveaway weekly amari",option_type=4, required=False),
				create_option(name="ping", description="Ping an role", option_type=8, required=False)
			]
		)
	async def gstart(self, ctx, time, price, winners,r_req=None, b_role=None, amari_level: int=None, weekly_amari: int=None, ping:discord.Role=None):
		time = await TimeConverter().convert(ctx, time)
		if time < 15:
			return await ctx.send("Giveaway time needed to be longer than 15 seconds")
		end_time = datetime.datetime.now() + datetime.timedelta(seconds=time)
		end_time = round(end_time.timestamp())
		r_req = r_req if r_req else None
		b_role = b_role if b_role else None
		amari_level = amari_level if amari_level else None
		weekly_amari = weekly_amari if weekly_amari else None

		embed_dict = {'type': 'rich', 'title': price, 'color': 10370047,
		'description': f"React this message to Enter!\nEnds: <t:{end_time}:R> (<t:{end_time}:F>)\nHosted By: {ctx.author.mention}", 'fields': []}
		if r_req == None:
			feild = {'name': "Role Requirements", 'inline':False}
			if b_role == None:
				pass
			else:
				feild['value'] = f"Bypass Role: {b_role.mention}"
				embed_dict['fields'].append(feild)
		else:
			feild = {'name': "Role Requirements:", 'inline':False}
			if b_role == None:
				feild['value'] = f"Required Role: {r_req.mention}"
				embed_dict['fields'].append(feild)
			else:
				feild['value'] = f"Required Role: {r_req.mention}\nBypass Role: {b_role.mention}"
				embed_dict['fields'].append(feild)

		feild = {'name': "Amari Requirements", 'inline': False}
		if amari_level != None and weekly_amari == None:
			feild['value'] = f"Required Amari Level: {amari_level}"
		if amari_level == None and weekly_amari != None:
			feild['value'] = f"Weekly Amari: {weekly_amari}"

		if amari_level != None and weekly_amari != None:
			feild['value'] = f"Amari Level: {amari_level}\nWeekly Amari: {weekly_amari}"
		if amari_level == None and weekly_amari == None:
			pass
		else:
			embed_dict['fields'].append(feild)

		embed = discord.Embed()
		msg = await ctx.send(embed=embed.from_dict(embed_dict))

		data = {"_id": msg.id,
				"guild": ctx.guild.id,
				"channel": ctx.channel.id,
				"host": ctx.author.id,
				"winners": winners,
				"entries": [],
				"end_time": time,
				"start_time": datetime.datetime.now(),
				"weekly_amari": weekly_amari,
				"amari_level": amari_level
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
		self.bot.giveaway[msg.id] = data
		await msg.add_reaction("🎉")
		if ping == None:
			pass
		else:
			await ctx.channel.send(ping.mention)

	@cog_ext.cog_slash(name="gend", description="Focre end an giveaway", guild_ids=guild_ids,default_permission=False, permissions=mod_perms,
		options=[
				create_option(name="message_id", description="message id of the giveaway", required=True, option_type=3)
			]
		)
	async def gend(self, ctx, message_id):
		message_id = int(message_id)
		data = await self.bot.give.find(message_id)
		if data is None:
			return await ctx.send(f"Error NO giveaway found with {message_id} Please Check your id")
		channel = self.bot.get_channel(data['channel'])
		message = await channel.fetch_message(data['_id'])
		if message is None:
			return await ctx.send("The Giveaway message has been deleted")

		users = await message.reactions[0].users().flatten()
		users.pop(users.index(ctx.guild.me))
		entries = await message.reactions[0].users().flatten()
		entries.pop(entries.index(ctx.guild.me))
		#users.pop(users.index(host))

		if len(users) == 0:
			embeds = message.embeds
			for embed in embeds:
				edict = embed.to_dict()

			edict['fields'] = []
			edict['title'] = f"{edict['title']} • Giveaway Has Endded"
			edict['color'] = 15158332
			field = {'name': "No valid entrants!", 'value': "so winner could not be determined!", 'inline': False}
			edict['fields'].append(field)
			await ctx.send("No valid entrants, so winner not be determined!", hidden=True)
			await message.edit(embed=embed.from_dict(edict))
			small_embed = discord.Embed(description=f"No valid [entrants]({message.jump_url}), so winner not be determined!", color=0x2f3136)
			await message.reply(embed=small_embed, hidden=False)

			await self.bot.give.delete((data['_id']))
			try:
				return self.bot.giveaway.remove((data['_id']))
			except KeyError:
						return

		if len(users) < data['winners']:
			embeds = message.embeds
			for embed in embeds:
				edict = embed.to_dict()

			edict['fields'] = []
			edict['title'] = f"{edict['title']} • Giveaway Has Endded"
			edict['color'] = 15158332
			field = {'name': "No valid entrants!", 'value': "so winner could not be determined!", 'inline': False}
			edict['fields'].append(field)
			await ctx.send("No valid entrants, so winner not be determined!", hidden=True)
			await message.edit(embed=embed.from_dict(edict))
			small_embed = discord.Embed(description=f"No valid [entrants]({message.jump_url}), so winner not be determined!", color=0x2f3136)
			await message.reply(embed=small_embed, hidden=False)

			await self.bot.give.delete(data['_id'])
			try:
				return self.bot.giveaway.remove((data['_id']))
			except KeyError:
				return

			winner_list = []
			entries = data['entries']
			users = await message.reactions[0].users().flatten()
			users.pop(users.index(ctx.guild.me))
			while True:
				member = random.choice(data['entries'])
				data['entries'].remove(member)
				member = await guild.get_member(member)
				if member in users:
					winner_list.append(member)
				if len(winner_list) == data['winners']:
						break

		embeds = message.embeds
		for embed in embeds:
			gdata = embed.to_dict()
		reply = ",".join(winner_list)
		small_embed = discord.Embed(description=f"Total Entries: [{len(entries)}]({message.jump_url})")
		host = await message.guild.fetch_member(data['host'])
		await message.reply(
			f"**Giveaway Has Endded**\n<a:winners_emoji:867972307103141959>  **Prize**      <a:yellowrightarrow:801446308778344468> {gdata['title']}\n─────────────────────\n<a:pandaswag:801013818896941066>   **Host**      <a:yellowrightarrow:801446308778344468> {host.display_name}\n─────────────────────\n<a:winner:805380293757370369>  **Winner** <a:yellowrightarrow:801446308778344468> {reply}\n─────────────────────\n", embed=small_embed)

		gdata['title'] = f"{gdata['title']} • Giveaway Has Endded"
		gdata['color'] = 15158332
		field = {'name': "Winner!", 'value': ", ".join(winner_list), 'inline': False}
		gdata['fields'].append(field)

		await ctx.send(f"The winners are {reply}", hidden=True)
		await message.edit(embed=embed.from_dict(gdata))

		await self.bot.give.delete_by_id(message.id)            
		try:
			return self.bot.giveaway.pop(message.id)
		except KeyError:
			return

	@cog_ext.cog_slash(name="greroll", description="Reroll and giveaway for new winners",guild_ids=guild_ids,default_permission=False, permissions=mod_perms,
		options=[
			create_option(name="message_id", description="message id of the giveaway", required=True, option_type=3),
			create_option(name="winners", description="numbers of winners", required=True, option_type=4),
			create_option(name="channel", description="channel of giveaway message", required=False, option_type=7),
			]
		)
	async def greroll(self, ctx, message_id, winners: int, channel=None,):
		message_id = int(message_id)
		channel = channel if channel else ctx.channel
		message = await channel.fetch_message(message_id)

		if message.author.id != self.bot.user.id:
			return await ctx.send("That message is not an giveaway")

		users = await message.reactions[0].users().flatten()
		users.pop(users.index(ctx.guild.me))
		entries = await message.reactions[0].users().flatten()
		entries.pop(entries.index(ctx.guild.me))

		if len(users) == 0:
			return await ctx.send("No winner found as there no reactions")
		if len(users) < winners:
			return await ctx.send(f"no winners found as there no reactions to meet {winners} requirment")

		winner_list = []
		while True:
			member = random.choice(users)
			if type(member) == discord.Member:
				users.pop(users.index(member))
				winner_list.append(member.mention)
			else:
				pass
			if len(winner_list) == winners:
				break

		embeds = message.embeds
		for embed in embeds:
			gdata = embed.to_dict()
		reply = ",".join(winner_list)

		gdata['fields'] = []
		gdata['color'] = 15158332
		field = {'name': "Winner!", 'value': ", ".join(winner_list), 'inline': False}
		gdata['fields'].append(field)

		await ctx.send(f"**Price**: {gdata['title']}\n**Winners**: {reply}\n**Total Entries**: {len(entries)}", hidden=False)
		await message.edit(embed=embed.from_dict(gdata))

	@cog_ext.cog_slash(name="gdelete", description="Delete an giveaway", guild_ids=guild_ids,default_permission=False, permissions=mod_perms,
		options=[
				create_option(name="message_id", description="message id of the giveaway message", required=True, option_type=3)
			]
		)
	@commands.check_any(commands.is_owner(), commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376,787259553225637889, 803230347575820289))
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

	@cog_ext.cog_slash(name="gblacklist", description="Blacklit an role from giveaway it's an global blacklist",guild_ids=guild_ids,default_permission=False, permissions=admin_perms,
		options=[
				create_option(name="role", description="Select role to blacklist it", required=True, option_type=8)
			]
		)
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

	@cog_ext.cog_slash(name="gbypass", description="make and role to bpyass all global giveaway",guild_ids=guild_ids, default_permission=False, permissions=admin_perms,
		options=[
				create_option(name="role", description="Select role make it bypass", required=True, option_type=8)
			]
		)
	async def gbypass(self, ctx, role: discord.role):
		data = await self.bot.config.find(ctx.guild.id)
		if data is None: return await ctx.send("Your Server config was not found please run config First")
		if role.id in data['g_bypass']:
			data['g_bypass'].remove(role.id)
			await ctx.send(f"{role.mention} Has been Removed from the Bypass list", hidden=True)
			return await self.bot.config.upsert(data)
		await self.bot.config.upsert(data)
		await ctx.send(f"{role.mention} is added to bypass list", hidden=True)

	@cog_ext.cog_slash(name="bypasslist", description="Send the Bypass role list", guild_ids=guild_ids,default_permission=False, permissions=mod_perms)
	async def bypasslist(self, ctx):
		data = await self.bot.config.find(ctx.guild.id)
		lists = []
		for role in data['g_bypass']:
			role = discord.utils.get(ctx.guild.roles, id=role)
			lists.append(role.mention)

		embed = discord.Embed(title="Bypass Role list", description=", ".join(lists), color=0x2f3136)

		await ctx.send(embed=embed, hidden=False)

	@cog_ext.cog_slash(name="blacklist", description="Send the blacklist role list", guild_ids=guild_ids, default_permission=False, permissions=mod_perms)
	async def blacklistl(self, ctx):
		data = await self.bot.config.find(ctx.guild.id)
		lists = []
		for role in data['g_blacklist']:
			role = discord.utils.get(ctx.guild.roles, id=role)
			lists.append(role.mention)

		embed = discord.Embed(title="blacklist Role list", description=", ".join(lists), color=0x2f3136)
		await ctx.send(embed=embed)

	@cog_ext.cog_slash(name="setmulti", description="Set role multi for giveaways", guild_ids=guild_ids,default_permission=False, permissions=admin_perms,
		options=[
			create_option(name="role", description="Select Role for multi",option_type=8, required=True),
			create_option(name="multi", description="Enter multi for the rolem", option_type=4, required=True)
		])
	async def role_multi(self, ctx: SlashContext, role:discord.Role, multi: int):
		data = await self.bot.config.find(ctx.guild.id)
		for roles in data['role_multi']:
			if role.id == roles['role_id']:
				data['role_multi'].remove(roles)

		multis = {'role_id': role.id, 'multi': multi}
		data['role_multi'].append(multis)
		data['role_multi'] = sorted(data['role_multi'],key=lambda x: x['multi'], reverse=True)
		await self.bot.config.upsert(data)
		embed = discord.Embed(title="Role Multi Update",color=0x2f3136,
			description=f"Role :{role.mention}\nRole Multiplier: {multi}")
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
		await ctx.send(embed=embed)

	@cog_ext.cog_slash(name="multis", description="Show server role multiplier", guild_ids=guild_ids)
	async def multis(self, ctx):
		data = await self.bot.config.find(ctx.guild.id)
		if data is None or len(data['role_multi']) == 0: return await ctx.send("No multis Founds", hidden=True)
		embed = discord.Embed(title="Server Role Multiplier", color=0x2f3136, description="")
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
		i = 1
		for roles in data['role_multi']:
			role = discord.utils.get(ctx.guild.roles, id=roles['role_id'])
			embed.description += f"{i}.Role: {role.mention}\n Multiplier: {roles['multi']}\n\n"
			i += 1
		await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(giveaway(bot))
