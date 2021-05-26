import asyncio
import datetime
import discord
import re

from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from discord.ext.buttons import Paginator
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_commands import create_option

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
guild_ids = [797920317871357972, 785839283847954433]

description = "Slash Commands"

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

class Slash(commands.Cog, description=description):
	"""docstring for Sla"""
	def __init__(self, bot):
		self.bot = bot

	def is_me():
	    def predicate(ctx):
	        return ctx.author.id == 488614633670967307
	    return commands.check(predicate)

	@commands.Cog.listener()
	async def on_ready(self):
	    print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	#############################
	#							#
	#							#
	#		Mod commands		#
	#							#
	#							#
	#############################

	@cog_ext.cog_slash(name="Status",
		description="Change Bot Status to online & Dnd & idle",
		guild_ids=guild_ids,
		options=[
		create_option(
			name="arg",
			description="Status options",
			option_type=3,
			required=True,
			choices=[
				create_choice(
						name="dnd",
						value="dnd",
					),
				create_choice(
						name="online",
						value="online",
					),
				create_choice(
						name="idle",
						value="idle",
					)
				]
			)
		]
	)				
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902), is_me())
	async def status(self,ctx, arg):
	    if arg.lower() == 'dnd':
	        await self.bot.change_presence(status=discord.Status.dnd)
	        await ctx.send('Bot status is Updated',hidden=True)
	    elif arg.lower() == 'online':
	        await self.bot.change_presence(status=discord.Status.online)
	        await ctx.send('Bot status is Updated',hidden=True)
	    elif arg.lower() == 'idle' :
	        await self.bot.change_presence(status=discord.Status.idle)
	        await ctx.send('Bot status is Updated',hidden=True)
	    else: 
	    	return 

	@cog_ext.cog_slash(name="mute",
	    description="Mute User for x time",
	    guild_ids=guild_ids,
	    options=[
	        create_option(
	            name="member",
	            description="mention or enter user id",
	            option_type=6,
	            required=True
	            ),
	        create_option(
	            name="time",
	            description="Time for The Mute",
	            option_type=3,
	            required=False
	            ),
	        create_option(
	            name="reason",
	            description="Reason Of the Mute",
	            option_type=3,
	            required=False
	            )
	        ]
	    )
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def Mute(self, ctx, member: str, time: str, *,reason=None):
	    time = await TimeConverter().convert(ctx, time)
	    reason = reason if reason else "N/A"
	    role = discord.utils.get(ctx.guild.roles, name="Muted")
	    if not role:
	        await ctx.send("No muted role was found! Please create one called `Muted`")
	        return

	    try:
	        if self.bot.muted_users[member.id]:
	            await ctx.send("This user is already muted")
	            return
	    except KeyError:
	        pass

	    data = {
	        '_id': member.id,
	        'mutedAt': datetime.datetime.now(),
	        'muteDuration': time or None,
	        'mutedBy': ctx.author.id,
	        'guildId': ctx.guild.id,
	    }
	    await self.bot.mutes.upsert(data)
	    self.bot.muted_users[member.id] = data

	    await member.add_roles(role)

	    try:
	        em = discord.Embed(color=0x06f79e, description=f" **{member.name}** Has been Muted")
	        await member.send(f"You Have Muted for {reason}")
	        await ctx.send(embed=em, hidden=True)            
	    except discord.HTTPException:
	        emb = discord.Embed(color=0x06f79e, description=f"The User **{member.name}** Muted I couldn't DM them.**")
	        await ctx.send(embed=emb, hidden=True)
	        
	    log_channel = self.bot.get_channel(803687264110247987)
	    embed = discord.Embed(title=f"Muted | {member.name}", inline=True)
	    embed.add_field(name="User", value=f"{member.mention}", inline=True)
	    embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=True)
	    embed.add_field(name="Reason", value=f"{reason}", inline=True)
	    embed.add_field(name="Time", value=f"{time}", inline=True)
	    embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

	    await log_channel.send(embed=embed)

	    if time and time < 300:
	        await asyncio.sleep(time)

	        if role in member.roles:
	            await member.remove_roles(role)
	            await ctx.send(f"Unmuted `{member.display_name}`")

	        await self.bot.mutes.delete(member.id)
	        try:
	            self.bot.muted_users.pop(member.id)
	        except KeyError:
	            pass


	@cog_ext.cog_slash(
	    name='unmute',
	    description="Unmuted a member!",
	    guild_ids=guild_ids,
	    options=[
	    create_option(
	        name="member",
	        description="Mention / id Member to be Unmuted",
	        option_type=6,
	        required=True)])
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def unmute(self, ctx, member: discord.Member):
	    role = discord.utils.get(ctx.guild.roles, name="Muted")
	    if not role:
	        await ctx.send("No muted role was found! Please create one called `Muted`")
	        return

	    await self.bot.mutes.delete(member.id)
	    try:
	        self.bot.muted_users.pop(member.id)
	    except KeyError:
	        pass

	    if role not in member.roles:
	        await ctx.send("This member is not muted.")
	        return

	    await member.remove_roles(role)

	    log_channel = self.bot.get_channel(803687264110247987)

	    em = discord.Embed(color=0x06f79e, description=f" **{member.name}** Has been Unmuted")
	    await ctx.send(embed=em)
	    #await log_channel.send(embed=embed)

	@cog_ext.cog_slash(name="kick",
	    description="Kick Member from guild",
	    guild_ids=guild_ids,
	    options=[
	        create_option(
	            name="member",
	            description="mention or enter user id",
	            option_type=6,
	            required=True
	            ),
	        create_option(
	            name="reason",
	            description="Reason Of the Kick",
	            option_type=3,
	            required=False
	            )
	        ]
	    )
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def kick(self, ctx, member: str, reason=None):
		reason = reason if reason else "N/A"
		if member.top_role >= ctx.author.top_role:
			return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")

		try:
			await member.send(f"You Have Been kicked")
			await ctx.guild.kick(user=member, reason=reason)
			em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been kicked")
			await ctx.send(embed=em)
		except discord.HTTPException:
			await ctx.guild.kick(user=member, reason=reason)
			emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been kicked I couldn't DM them.**")
			await ctx.send(embed=emb)

		log_channel = self.bot.get_channel(803687264110247987)

		embed = discord.Embed(title=f"kicked | {member.name}")
		embed.add_field(name="User", value=f"{member.name}", inline=False)
		embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
		embed.add_field(name="Reason", value=f"{reason}", inline=False)
		embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

		await log_channel.send(embed=embed)

	@cog_ext.cog_slash(name="whois", 
		description="Give all Infomation about user",
		guild_ids=guild_ids,
		options=[
		create_option(
			name="member",
			description="mention or enter user id",
			option_type=6,
			required=True)
		]
	)
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def whois(self, ctx, member: str):
		def fomat_time(time):
			return time.strftime('%d-%B-%Y %I:%m %p')

		usercolor = member.color


		embed = discord.Embed(title=f'{member.name}', color=usercolor)
		embed.set_thumbnail(url=member.avatar_url)
		embed.add_field(name='Account Name:', value=f'{member.name}', inline=False)
		embed.add_field(name='Created at:', value=fomat_time(member.created_at))
		embed.add_field(name='Joined at', value=fomat_time(member.joined_at))
		embed.add_field(name='Account Status', value=str(member.status).title())
		embed.add_field(name='Account Activity', value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

		hsorted_roles = sorted([role for role in member.roles[-2:]], key=lambda x: x.position, reverse=True)


		embed.add_field(name='Top Role:', value=', '.join(role.mention for role in hsorted_roles), inline=False)
		embed.add_field(name='Number of Roles', value=f"{len(member.roles) -1 }")
		embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar_url)
		await ctx.send(embed=embed, hidden=True)

	@cog_ext.cog_slash(
		name="blacklist",
		description="blacklist user from the bot",
		guild_ids=guild_ids,
		options=[
			create_option(
			name="user",
			description="Mention / Give id of the User to blacklist",
			required=True,
			option_type=6
			)])
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376), is_me())
	async def blacklist(self, ctx, user: str):
		user = user if user else ctx.author
		if user.id in [self.bot.user.id, ctx.author.id,488614633670967307, 488614633670967307]:
			return await ctx.send("Hey, you cannot blacklist yourself / bot/ Owner")

		blacklist = {'_id': user.id}

		await self.bot.blacklist.upsert(blacklist)

		current_blacklist_user = await self.bot.blacklist.get_all()
		for blacklisted_user in current_blacklist_user:
			self.bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

		embed = discord.Embed(description=f"The User {user.mention} is now blacklisted")
		try:
			await user.send("you Have been blacklist from using me")
			await user.send("<a:bye:842697189159206932>")
		except discord.HTTPException:
			pass
		await ctx.send(embed=embed, hidden=False)

	@cog_ext.cog_slash(
		name="unblacklist",
		description="Unblacklist a user from the bot",
		guild_ids=guild_ids,
		options=[
			create_option(
				name="user",
				description="Mention / Give id of the User to Unblacklist",
				option_type=6,
				required=True
			)
		])
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636), is_me())
	async def unblacklist(self, ctx, user: discord.Member):
		blacklist = {'_id': user.id}

		await self.bot.blacklist.delete_by_custom(blacklist)

		current_blacklist_user = await self.bot.blacklist.get_all()
		for blacklisted_user in current_blacklist_user:
			self.bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

		try:
			self.bot.blacklist_user.pop(user.id)
		except KeyError:
			pass

		embed = discord.Embed(description=f"The User {user.mention} is now unblacklisted")
		await ctx.send(embed=embed)

	@cog_ext.cog_slash(name="warn",
		description="Gives an Warnings to user",
		guild_ids=guild_ids,
		options=[
	        create_option(
	            name="member",
	            description="mention or enter user id",
	            option_type=6,
	            required=True
	            ),
	        create_option(
	            name="reason",
	            description="User Warning",
	            option_type=3,
	            required=True
	            )
	        ]
	    )
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916), is_me())
	async def warn(self, ctx, member: str, reason: str):
	    if member.id in [self.bot.user.id, 488614633670967307, 301657045248114690]:
	        return await ctx.send("You cannot warn bot or it's Creater because they are way too cool to be warned")

	    if member.id == ctx.author.id:
	        return await ctx.send("You cannot warn your self")
	    

	    
	    current_warn_count = len(
	        await self.bot.warns.find_many_by_custom(
	            {
	                "user_id": member.id,
	                "guild_id": member.guild.id
	            }
	        )
	    ) + 1
	    
	    warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
	    warn_data = {"reason": reason, "timestamp": datetime.datetime.now(), "warned_by": ctx.author.id}
	    
	    await self.bot.warns.upsert_custom(warn_filter, warn_data)  
	        
	    try:
	        await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
	        em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count}**")
	        await ctx.send(embed=em)
	    except discord.HTTPException:
	        emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been Warned I couldn't DM them.| Warnings Count {current_warn_count}**")
	        await ctx.send(embed=emb)
	    
	    try:
	        log_channel = self.bot.get_channel(803687264110247987)

	        embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
	        embed.add_field(name="User", value=f"{member.name}", inline=False)
	        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
	        embed.add_field(name="Reason", value=f"{reason}", inline=False)
	        embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
	        embed.add_field(name="threshold Action", value="None")
	        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

	        await log_channel.send(embed=embed)
	    except:
	        pass
	@cog_ext.cog_slash(name="warnings", description="Gives an Warnings to user",
		options=[
			create_option(
				name="member",
				description="User Warning id",
				option_type=3,
				required=True)
		])
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889), is_me())
	async def warnings(self, ctx, member: str):
		warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
		warns = await self.bot.warns.find_many_by_custom(warn_filter)

		if not bool(warns):
			return await ctx.send(f"Couldn't find any warns for: `{member.display_name}`")

		warns = sorted(warns, key=lambda x: x["number"])

		pages = []
		for warn in warns:
			description = f"""
			Warn id: `{warn['_id']}`
			Warn Number: `{warn['number']}`
			Warn Reason: `{warn['reason']}`
			Warned By: <@{warn['warned_by']}>
			Warn Time: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
			"""
			pages.append(description)

		await Pag(
			title=f"Warns for `{member.display_name}`",
			colour=0xCE2029,
			entries=pages,
			length=2
		).start(ctx)

	@cog_ext.cog_slash(name="ban", description="Ban user From guild,",
	    guild_ids=guild_ids,
	    options=[
	        create_option(
	            name="user",
	            description="User you want to ban",
	            option_type=6,
	            required=True
	            ),
	        create_option(
	            name="time",
	            description="Duration Of the ban",
	            option_type=3,
	            required=False,
	            ),
	        create_option(
	            name="reason",
	            description="Reason of the ban",
	            required=False,
	            option_type=3
	            )
	        ]
	    ) 
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916), is_me())
	async def ban(self, ctx, member: discord.User, time: TimeConverter=None, *, reason=None):
		await ctx.message.delete()
		try:
			user = member.name.lower()
			user = await commands.MemberConverter().convert(ctx, user)
			if user.top_role >= ctx.author.top_role:
				return await ctx.send("You can't You cannot do this action on this user due to role hierarchy.")
		except:
			pass

		if time == None:

			try:
				await member.send(f"You Have Been Banned | {reason}")
				await ctx.guild.ban(user=member, reason=reason)
				em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been Banned || {reason}")
				await ctx.send(embed=em)
			except discord.HTTPException:
				await ctx.guild.ban(user=member, reason=reason)
				emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name}** Has Been Banned || {reason}")
				await ctx.send(embed=emb)
		else:


			try:
				await member.send(f"You Have Been Banned | {reason}")
				await ctx.guild.ban(user=member, reason=reason)
				em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name}** Has been Banned || {reason}")
				await ctx.send(embed=em)
			except discord.HTTPException:
				await ctx.guild.ban(user=member, reason=reason)
				emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name}** Has Been Banned || {reason}")
				await ctx.send(embed=emb)

			data = {
				'_id': member.id,
				'BannedAt': datetime.datetime.now(),
				'BanDuration': time or None,
				'BanedBy': ctx.author.id,
				'guildId': ctx.guild.id,
			}
			await self.bot.bans.upsert(data)
			self.bot.ban_users[member.id] = data


			log_channel = self.bot.get_channel(827245906331566180)


		embed = discord.Embed(title=f"Banned | {member.name}")
		embed.add_field(name="User", value=f"{member.name}")
		embed.add_field(name="Moderator", value=f"{ctx.author.mention}")
		embed.add_field(name="Reason", value=f"{reason}", inline=False)

		embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

		await log_channel.send(embed=embed)


	@cog_ext.cog_slash(
    	name="role",
    	description="Add or remove role from user",
    	guild_ids=guild_ids,
    	options=[
    		create_option(
    			name="member",
    			description="Member your want to add & remove role",
    			required=True,
    			option_type=6
    			),
    		create_option(
    			name="role",
    			description="Role you want to add & remove ",
    			required=True,
    			option_type=8
    			)
    		]
    	)
	@commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916), is_me())
	async def role(self, ctx, member:discord.Member, *,role: discord.Role):
		if role >= ctx.author.top_role:
			return await ctx.send("You can't You cannot do this action due to role hierarchy.")

		roles = member.roles

		if role in roles:
			await member.remove_roles(role)
			embed = discord.Embed(description=f"<:allow:819194696874197004> | {role} Removed from {member}")
			await ctx.send(embed=embed)
		else:
			await member.add_roles(role)
			embed = discord.Embed(description=f"<:allow:819194696874197004> | {role} Added to {member}")
			await ctx.send(embed=embed)




		

def setup(bot):
    bot.add_cog(Slash(bot))



