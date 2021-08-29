import discord
import datetime
import random
import asyncio

from discord.ext import commands
from discord.ext import tasks
from discord_components import DiscordComponents, Button, InteractionType, ButtonStyle


description = "Early Stage Economy game Things might get change"
class casino(commands.Cog, description=description):
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

	@commands.command(name="work", description="Simpal work command")
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.check_any(perm_check(), is_me())
	async def work(self, ctx):
		data = await self.bot.casino.find(ctx.author.id)
		if data is None:
			data = {'_id': ctx.author.id, 'cash': 0, 'vault': 0, 'total': 0}
		earning = random.randint(100, 1000)
		data['cash'] += earning
		embed = discord.Embed(description=f"{ctx.author} you have successfully Earned {earning}$")
		await self.bot.casino.upsert(data)
		await ctx.send(embed=embed)

	@commands.command(name="crime", description="Do some Bad thing change to get big or lost big")
	@commands.check_any(perm_check(), is_me())
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def crime(self, ctx):
		trinnger1 = random.randint(1, 100)
		trinnger2 = random.randint(1, 100)

		lost = random.randint(500, 2000)
		earn = random.randint(500, 2000)

		data = await self.bot.casino.find(ctx.author.id)
		if trinnger1 > trinnger2:
			fail_embed = discord.Embed(description=f"You were caught during the heist and you lost {lost}$", color=0xE74C3C)
			fail_embed.timestamp = datetime.datetime.utcnow()
			fail_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
			fail_embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
			await ctx.reply(embed=fail_embed, mention_author=False)

			data['cash'] -= lost
			if data['cash'] <= 0:
				data['cash'] = 0
			return await self.bot.casino.upsert(data)

		embed = discord.Embed(color=0x2ECC71, description=f"You successfully Stole the {earn} from your last heist")
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		await ctx.reply(embed=embed, mention_author=False)
		data['cash'] += earn

		await self.bot.casino.upsert(data)

	@commands.command(name="balance", description="Show your or someone else bal", aliases=['bal'])
	@commands.check_any(perm_check(), is_me())
	async def balance(self, ctx, user: discord.Member=None):
		user = user if user else ctx.author

		data = await self.bot.casino.find(user.id)
		if data is None:
			return await ctx.send("Your balance is None `use >work` to get started")
		embed = discord.Embed(title=f"{user.name}'s balance",color=user.color)
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		embed.add_field(name="Cash:", value=f"{data['cash']}")
		embed.add_field(name="vault:", value=f"{data['vault']}")
		embed.add_field(name="Total:", value=f"{data['cash'] + data['vault']}")

		await ctx.reply(embed=embed, mention_author=False)

	@commands.command(name="withdraw", description="Withdraw money from your vault.", aliases=['with'])
	@commands.check_any(perm_check(), is_me())
	async def withdraw(self, ctx, amount):
		data = await self.bot.casino.find(ctx.author.id)
		if data is None:
			return await ctx.send("Your balance is None `use >work` to get started")

		if str(amount.lower()) in ['all', 'max']:
			amount = data['vault']

		amount = int(amount)
		if amount > data['vault']:
			fail_embed = discord.Embed(color=0xE74C3C, description=f"<:deny:811570766818050100> | You can withdraw more than you total vault you currentry have {data['vault']}$")
			fail_embed.timestamp = datetime.datetime.utcnow()
			fail_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
			return await ctx.reply(embed=fail_embed, mention_author=False)
		data['vault'] -= amount
		data['cash'] += amount

		embed = discord.Embed(color=0x2ECC71, description=f"{ctx.author.mention} you have successfully withdraw {amount}$ from you vault now you left with {data['vault']}$ in vault")		
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		await ctx.reply(embed=embed, mention_author=False)
		await self.bot.casino.upsert(data)

	@commands.command(name="Deposit", description="Deposit money to your vault.", aliases=['dep'])
	@commands.check_any(perm_check(), is_me())
	async def Deposit(self, ctx, amount):
		data = await self.bot.casino.find(ctx.author.id)
		if data is None:
			return await ctx.send("Your balance is None `use >work` to get started")
		if str(amount.lower()) in ['all', 'max']:
			amount = data['cash']

		amount = int(amount)
		if data['cash'] < amount:
			fail_embed = discord.Embed(color=0xE74C3C, description=f"<:deny:811570766818050100> | You can Deposit more than you total cash you currentry have {data['cash']}$ in your hand")
			fail_embed.timestamp = datetime.datetime.utcnow()
			fail_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
			return await ctx.reply(embed=fail_embed, mention_author=False)

		data['vault'] += amount
		data['cash'] -= amount

		embed = discord.Embed(color=0x2ECC71, description=f"{ctx.author.mention} you have successfully Deposit {amount}$ from you cash now you have {data['vault']}$ in vault")		
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		await ctx.reply(embed=embed, mention_author=False)
		await self.bot.casino.upsert(data)

	@commands.command(name="reset-bal", description="Re-Set your balance", aliases=['reset'])
	@commands.check_any(perm_check(), is_me())
	async def reset(self, ctx):
		data = await self.bot.casino.find(ctx.author.id)
		if data is None:
			return await ctx.reply("You have never played this game how you can reset you balance without playing")
		embed = discord.Embed(color=0xE74C3C, description=f"{ctx.author.mention} Are you Sure You want to re set your balance?")
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
		buttons = [
			[	
				Button(style=ButtonStyle.red, label="No"),
				Button(style=ButtonStyle.green, label="yes")
			]
		]
		m = await ctx.reply(embed=embed, components=buttons)
		try:
			res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=15)
			await res.respond(type=6)
			if str(res.component.label.lower()) == "yes":
				data['cash'] = 0
				data['vault'] = 0
				await self.bot.casino.upsert(data)
				done_embed = discord.Embed(color=0x2ECC71, description=f"{ctx.author.mention} Your balance has been reseted")
				done_embed.timestamp = datetime.datetime.utcnow()
				done_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
				await m.edit(embed=done_embed, components=[])
			if str(res.component.label.lower()) == "no":
				done_embed = discord.Embed(color=0x2ECC71, description=f"{ctx.author.mention} Canceling the command\n**Reason**: Canceled by User")
				done_embed.timestamp = datetime.datetime.utcnow()
				done_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
				await m.edit(embed=done_embed, components=[])
		except asyncio.TimeoutError:
				done_embed = discord.Embed(color=0x2ECC71, description=f"{ctx.author.mention} Canceling the command\n**Reason**: TimeoutError")
				done_embed.timestamp = datetime.datetime.utcnow()
				done_embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
				await m.edit(embed=done_embed, components=[])

	@commands.command(name="add-money", description="add money to Member Account")
	@commands.check_any(perm_check(), is_me())
	async def add_money(self, ctx, user: discord.Member, amount: int):
		if amount <= 0: return await ctx.send("YOu Can't joke with someone by adding 0$ to there Account")

		data = await self.bot.casino.find(user.id)
		if data is None:
			data = {'_id': user.id, 'cash': 0, 'vault': 0}
		embed = discord.Embed(description=f"{ctx.author.mention} Where you want to add {user.mention} money", color=user.color)
		embed.timestamp = datetime.datetime.utcnow()
		embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
		buttons = [
			[
				Button(style=ButtonStyle.green, label="Vault"),
				Button(style=ButtonStyle.blue, label="Cash"),
				Button(style=ButtonStyle.red, label="Cancel")
			]
		]

		m = await ctx.reply(embed=embed, components=buttons)
		try:
			res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=15)
			await res.respond(type=6)
			if str(res.component.label.lower()) == "vault":
				data['vault'] += amount
				await self.bot.casino.upsert(data)

				embed = discord.Embed(description=f"{ctx.author.mention} You have successfully Add {amount} to {user.mention}'s {res.component.label.lower()}")
				embed.timestamp = datetime.datetime.utcnow()
				embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)

				return await m.edit(components=[], embed=embed)

			if str(res.component.label.lower()) == "cash":
				data['cash'] += amount
				await self.bot.casino.upsert(data)

				embed = discord.Embed(description=f"{ctx.author.mention} You have successfully Add {amount} to {user.mention}'s {res.component.label.lower()}")
				embed.timestamp = datetime.datetime.utcnow()
				embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)

				return await m.edit(components=[], embed=embed)

			if str(res.component.label.lower()) == "cancel":

				embed = discord.Embed(description=f"Canceling the command\n**Reason**: Canceled by Staff")
				embed.timestamp = datetime.datetime.utcnow()
				embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
				return await m.edit(embed=embed, components=[])

		except asyncio.TimeoutError:
			embed = discord.Embed(description="Canceling command\n**Reason: TimeoutError**")
			await m.edit(embed=embed, components=[])

	@commands.command(nmae="bet", description="Simpal bet command")
	@commands.check_any(is_me(), perm_check())
	async def bet(self, ctx, amount: int):
		data = await self.bot.casino.find(ctx.author.id)
		if data is None: return await ctx.reply("I think You need To work frist to Earn some to become poor")
			
		if data['cash'] < amount: return await ctx.send(f"You can bet more than you cash you currently have {data['cash']} in you hand")

		player = random.randint(1, 20)
		compter = random.randint(5, 20)

		if player > compter:
			data['cash'] += amount*2
			embed = discord.Embed(color=0x2ECC71,title="You won the bet",
				description=f"You bet was **{amount}**\nYour price is **{amount*2}**\nNow you have **{data['cash']}**")

			embed.timestamp = datetime.datetime.utcnow()
			embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)

			embed.add_field(name="Your Number", value=player)
			embed.add_field(name=f"{self.bot.user.name}", value=compter)

			await self.bot.casino.upsert(data)
			return await ctx.reply(embed=embed, mention_author=False)

		if player < compter:
			data['cash'] -= amount
			embed = discord.Embed(color=0xE74C3C,title="You lost the bet",
				description=f"You bet was **{amount}**\nNow you have **{data['cash']}**")

			embed.timestamp = datetime.datetime.utcnow()
			embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)

			embed.add_field(name="Your Number", value=player)
			embed.add_field(name=f"{self.bot.user.name}", value=compter)

			await self.bot.casino.upsert(data)
			return await ctx.reply(embed=embed, mention_author=False)

		if player == compter:
			data['cash'] - amount
			embed = discord.Embed(color=0xA84300,title="Your bet is tie",
				description=f"You bet was **{amount}**\nYou Cash is has't been charge")

			embed.timestamp = datetime.datetime.utcnow()
			embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)

			embed.add_field(name="Your Number", value=player)
			embed.add_field(name=f"{self.bot.user.name}", value=compter)

			await self.bot.casino.upsert(data)
			return await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(casino(bot))


