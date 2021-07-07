import datetime
import discord
import re
import random
from typing import Union
from humanfriendly import format_timespan
from discord.ext import commands
import asyncio
from discord_slash import cog_ext, SlashContext, cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandPermissionType

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

description="Some slash commands form the modreation Cog but as slash /"
guild_ids=[785839283847954433]
class slash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} has been loaded")

	@cog_ext.cog_slash(name="stest",description="An test commands",guild_ids=guild_ids,
		options=[
				create_option(
					name="user",
					description="Select You that need to be ban",
					option_type=6,
					required=True
				)
			]
		)
	@commands.check_any(commands.has_any_role(785842380565774368,803635405638991902,799037944735727636,785845265118265376,787259553225637889,843775369470672916), commands.is_owner())
	async def ttest(self , ctx: SlashContext, user):
		await ctx.send("Hello", hidden=True)
		

	@cog_ext.cog_slash(name="ban", description="Ban user From the Server", guild_ids=guild_ids,
		options=[
				create_option(
					name="user",
					description="Select You that need to be ban",
					option_type=6,
					required=True
				),
				create_option(
					name="reason",
					description="Tell why you want to ban that user",
					option_type=3,
					required=True,
				),
				create_option(
					name="time",
					description="How much time they need to ban exp: 1h | 4d etc",
					option_type=3,
					required=False
				)
			]
		)
	@commands.check_any(commands.has_any_role(785842380565774368,803635405638991902,799037944735727636,785845265118265376,787259553225637889), commands.is_owner())
	async def ban(self , ctx: SlashContext, user, reason:str, time: TimeConverter=None):
		time = time if time else None
		try:
			if user.top_role >= ctx.author.top_role:
				return await ctx.send("You cannot do this action on this user due to role hierarchy.")
		except:
			user = int(user)
			user = await self.bot.fetch_user(int(user))

		if time ==None:
			try:
				await user.send(f"You have been Banned from {ctx.guild.name} for {reason}")
			except discord.HTTPException:
				pass

			await ctx.guild.ban(user, reason=reason, delete_message_days=0)

			em = discord.Embed(color=0x06f79e, description=f"**{user.name}** Has been Banned for {reason}")
			await ctx.send(embed=em)

			log_channel = self.bot.get_channel(855784930494775296)
			data = await self.bot.config.find(ctx.guild.id)
			log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
			    description=f" **Offender**: {user} | {user.mention} \n**Reason**: {reason}\n **Moderator**: {ctx.author} {ctx.author.mention}", color=0xE74C3C)
			log_embed.set_thumbnail(url=user.avatar_url)
			log_embed.timestamp = datetime.datetime.utcnow()
			log_embed.set_footer(text=f"ID: {user.id}")

			await log_channel.send(embed=log_embed)
			data["case"] += 1
			
			return await self.bot.config.upsert(data)

		time = await TimeConverter().convert(ctx, time)
		data = {
		    '_id': user.id,
		    'BannedAt': datetime.datetime.now(),
		    'BanDuration': time or None,
		    'BanedBy': ctx.author.id,
		    'guildId': ctx.guild.id,
		}
		await self.bot.bans.upsert(data)
		self.bot.ban_users[user.id] = data
		time = format_timespan(time)

		try:
			await user.send(f"You Have Been Banned from {ctx.guild}\nTime: {time}\nReason: {reason}")
		except:
			pass

		await ctx.guild.ban(user, reason=reason, delete_message_days=0)

		em = discord.Embed(color=0x06f79e, description=f"**{user.mention}** Has been Banned for {reason}")
		await ctx.send(embed=em)

		case = await self.bot.config.find(ctx.guild.id)
		log_channel = self.bot.get_channel(855784930494775296)

		log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {case['case']}",
		    description=f" **Offender**: {user} | {user.mention} \n**Reason**: {reason}\n **Duration**: {time}\n **Moderator**: {ctx.author} {ctx.author.mention}", color=0xE74C3C)
		log_embed.set_thumbnail(url=user.avatar_url)
		log_embed.set_footer(text=f"ID: {user.id}")
		log_embed.timestamp = datetime.datetime.utcnow()
		await log_channel.send(embed=log_embed)

		case["case"] += 1
		await self.bot.config.upsert(case)

	@cog_ext.cog_slash(name="kick", description="Kick someone from the guild",
		guild_ids=guild_ids,
		options=[
				create_option(
						name="user",
						description="Select which user need to kicked",
						option_type=6,
						required=True,
					),
				create_option(
					name="reason",
					description="Why your kicking that user",
					option_type=3,
					required=True,
					)
			]
		)
	@commands.check_any(commands.has_any_role(785842380565774368,803635405638991902,799037944735727636,785845265118265376,787259553225637889,843775369470672916), commands.is_owner())
	async def kick(self, ctx: SlashContext, user, reason):
		if user.top_role >= ctx.author.top_role: return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")

		try:
			await user.send(f"You Have Been kicked from {ctx.guild} for {reason}")
		except:
			pass

		await ctx.guild.kick(user=user, reason=reason)
		emb = discord.Embed(color=0x06f79e, description=f"**{user.name}** Has Been kicked for {reason}")

		await ctx.send(embed=emb)

		log_channel = self.bot.get_channel(855784930494775296)
		data = await self.bot.config.find(ctx.guild.id)
		log_embed = discord.Embed(title=f"👢 Kick | Case ID: {data['case']}",
		    description=f" **Offender**: {user} | {user.mention}\n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}\n **Reason**: {reason}.", color=0xE74C3C)
		log_embed.set_thumbnail(url=user.avatar_url)
		log_embed.timestamp = datetime.datetime.utcnow()
		await log_channel.send(embed=log_embed)

		data["case"] += 1
		await self.bot.config.upsert(data)
	@cog_ext.cog_slash(name="mute", description="Mute someone for x time", guild_ids=guild_ids,
		options=[
			create_option(name="user", description="Select which User You want to Mute" , option_type=6, required=True),
			create_option(name="reason", description="Enter reason for the mute" , option_type=3, required=True),
			create_option(name="time", description="The time you want to mute user", option_type=3, required=False)
		]
	)
	@commands.check_any(commands.has_any_role(785842380565774368,803635405638991902,799037944735727636,785845265118265376,787259553225637889,843775369470672916), commands.is_owner())
	async def mute(self, ctx: SlashContext, user, reason, time=None):
		role = discord.utils.get(ctx.guild.roles, name="Muted")
		if not role:
		    await ctx.send("No muted role was found! Please create one called `Muted`")
		    return

		try:
			if self.bot.muted_users[user.id]:
				await ctx.send("This user is already muted")
			return
		except KeyError:
			pass

		if time ==None:
			await user.add_roles(role)
			try:
				await user.send(f"You Have Been muted in {ctx.guild}\nTime: N/A, Reason: {reason}")
			except:
				pass

			em = discord.Embed(color=0x06f79e, description=f"**{user.name}** Has been Muted for {reason}")
			await ctx.send(embed=em)

			data = await self.bot.config.find(ctx.guild.id)
			log_channel = self.bot.get_channel(855784930494775296)

			log_embed = discord.Embed(title=f"🔇 Mute | Case ID: {data['case']}",
				description=f" **Offender**: {user} | {user.mention}\n **Reason**: {reason}\n **Duration**: None \n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}",
				color=0x706e6d)
			log_embed.set_thumbnail(url=user.avatar_url)
			log_embed.timestamp = datetime.datetime.utcnow()
			log_embed.set_footer(text=f"ID: {user.id}")

			await log_channel.send(embed=log_embed)

			data["case"] += 1
			return await self.bot.config.upsert(data)

		time = await TimeConverter().convert(ctx, time)

		data = {
			'_id': user.id,
			'mutedAt': datetime.datetime.now(),
			'muteDuration': time or None,
			'mutedBy': ctx.author.id,
			'guildId': ctx.guild.id,
		}
		await self.bot.mutes.upsert(data)
		self.bot.muted_users[user.id] = data

		await user.add_roles(role)

		time = format_timespan(time)

		try:
		    await user.send(f"You Have Muted in {ctx.guild.name}\n**Reason**:{reason}\nDuration: {time}")
		    
		except discord.HTTPException:
		    pass
		em = discord.Embed(color=0x06f79e, description=f"**{user.display_name}** Has been Muted for {reason}**")
		await ctx.send(embed=em)


		case = await self.bot.config.find(ctx.guild.id)
		log_channel = self.bot.get_channel(855784930494775296)

		log_embed = discord.Embed(title=f"🔇 Mute | Case ID: {case['case']}",
		    description=f" **Offender**: {user.name} | {user.mention}\n **Reason**: {reason}\n **Duration**: {time} \n **Moderator**: {ctx.author.display_name} | {ctx.author.mention}",
		    color=0x706e6d)
		log_embed.set_thumbnail(url=user.avatar_url)
		log_embed.timestamp = datetime.datetime.utcnow()
		log_embed.set_footer(text=f"ID: {user.id}")

		await log_channel.send(embed=log_embed)

		case["case"] += 1
		await self.bot.config.upsert(case)

	@cog_ext.cog_slash(name="Unmute", description="Unmute an User", guild_ids=guild_ids,
		options=[
				create_option(name="user", description="Select which User need be Unmuted", option_type=6, required=True),
				create_option(name="reason", description="reason why your unmuting user early", option_type=3, required=False)
			]
		)
	@commands.check_any(commands.has_any_role(785842380565774368,803635405638991902,799037944735727636,785845265118265376,787259553225637889,843775369470672916), commands.is_owner())
	async def unmute(self, ctx:SlashContext, user, reason):
		role = discord.utils.get(ctx.guild.roles, name="Muted")
		if not role:
		    await ctx.send("No muted role was found! Please create one called `Muted`")
		    return
		reason = reason if reason else "N/A"
		await self.bot.mutes.delete(user.id)
		try:
			self.bot.muted_users.pop(user.id)
		except KeyError:
			pass

		if role not in user.roles:
			await ctx.send("This user is not muted.")
			return

		await user.remove_roles(role)
		embed = discord.Embed(description=f"{user} Has been Unmuted",color=0x2ECC71)
		await ctx.send(embed=embed)

		log_channel = self.bot.get_channel(855784930494775296)
		data = await self.bot.config.find(ctx.guild.id)
		log_embed = discord.Embed(title=f"🔊 UnMute | Case ID: {data['case']}",
			description=f" **Offender**: {user.name} | {user.mention} \n**Reason**: {reason}\n**Moderator**: {ctx.author.display_name} {ctx.author.mention}", color=0x2ECC71)
		log_embed.set_thumbnail(url=user.avatar_url)
		log_embed.timestamp = datetime.datetime.utcnow()
		log_embed.set_footer(text=f"ID: {user.id}")

		await log_channel.send(embed=log_embed)

		data["case"] += 1
		await self.bot.config.upsert(data)

def setup(bot):
	bot.add_cog(slash(bot))

