import discord
import random
from aiohttp import ClientSession 
from discord.ext import commands
from discord.ext.buttons import Paginator

cheer_list = ['https://cdn.discordapp.com/attachments/825085572808048640/825086103123918878/FGnTsOugrHn.gif', 'https://cdn.discordapp.com/attachments/825085572808048640/825086103529979904/RxZpYpAYJ3S.gif', 'https://cdn.discordapp.com/attachments/825085572808048640/825086106877820928/PhckNRB7QlR.gif', 'https://cdn.discordapp.com/attachments/825085572808048640/825086107829141564/EQNFb9whFfW.gif', 'https://cdn.discordapp.com/attachments/825085572808048640/825086107829141564/EQNFb9whFfW.gif']
happy_list = ['https://cdn.discordapp.com/attachments/825086950889357373/825086978835218454/vzF17VYrPnJ.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825086979206376147/jiKEIBTnjD8.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825086979206376147/jlZpVohMlQa.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825086977706688552/bBjyBBELm-y.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825086981729812530/gxf9q_J_cO9.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825226397915021342/NxqXZcKfohG.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825226837021163551/KurxTAF4lLC.gif', 'https://cdn.discordapp.com/attachments/825086950889357373/825227060029030471/U9yDrzJv-cJ.gif']
thunbs_list = ['https://cdn.discordapp.com/attachments/825087463378649169/825087545117114428/KO8VOU02f4-.gif', 'https://cdn.discordapp.com/attachments/825087463378649169/825087550913249342/fysDqwRixlI.gif', 'https://cdn.discordapp.com/attachments/825087463378649169/825087550505877534/NGrmO-BitWI.gif', 'https://cdn.discordapp.com/attachments/825087463378649169/825087553102282752/JicNupwQbjN.gif', 'https://cdn.discordapp.com/attachments/825087463378649169/827428544875462667/bcUJc-TazUJ.gif'] 
bonk_list = ['https://cdn.discordapp.com/attachments/825088594573262928/825088734050517061/mkwc7O8ZbdB.gif', 'https://cdn.discordapp.com/attachments/825088594573262928/825088737930510366/Kbh7TKv_gir.gif', 'https://cdn.discordapp.com/attachments/825088594573262928/825088737502953522/UA_ULTCRDnh.gif', 'https://cdn.discordapp.com/attachments/825088594573262928/825088738765832202/XUoBwk4i-pX.gif', 'https://cdn.discordapp.com/attachments/825088594573262928/825088741550850118/DgQQNMoFa2W.gif']
dab_list = ['https://cdn.discordapp.com/attachments/825089243449393224/825089272804802610/WoW56DDk6sx.gif', 'https://cdn.discordapp.com/attachments/825089243449393224/825089268543520829/LfEFQkN8f3g.gif']
sleep_list = ['https://cdn.discordapp.com/attachments/825089635524149278/825089676611420230/4RgVOSz5aDX.gif', 'https://cdn.discordapp.com/attachments/825089635524149278/825089682127716372/AqDf2tllzQ_.gif','https://cdn.discordapp.com/attachments/825089635524149278/825089682257477672/v81QZhuK9G-.png', 'https://cdn.discordapp.com/attachments/825089635524149278/825089682231656508/kDKvD-sDHPG.gif']
yes_list = ['https://cdn.discordapp.com/attachments/825090204741402705/825090217118793748/gFjtj3vpGxp.gif', 'https://cdn.discordapp.com/attachments/825090204741402705/825090221405241404/TpKXb_mcU46.gif', 'https://cdn.discordapp.com/attachments/825090204741402705/825090222207139850/Pl9Xv5xpd5W.gif', 'https://cdn.discordapp.com/attachments/825090204741402705/825090223523627058/GT7m_OOiKji.gif', 'https://cdn.discordapp.com/attachments/825090204741402705/825090227944947762/1xk2GzYv_Xf.gif']
angry_list = ['https://cdn.discordapp.com/attachments/825091988046348308/825092015154659379/dX3CcmGpLwb.gif', 'https://cdn.discordapp.com/attachments/825091988046348308/825092013673283584/JV3tNhf_e7Z.gif', 'https://cdn.discordapp.com/attachments/825091988046348308/825092012218646528/HoAGtevPyXp.gif', 'https://cdn.discordapp.com/attachments/825091988046348308/825092010662428713/Gdz8hUHVnBh.gif']
cry_list = ['https://cdn.discordapp.com/attachments/825090653729456169/825090684099887184/YHFftYClBP-.gif', 'https://cdn.discordapp.com/attachments/825090653729456169/825090683928313926/t4i74GvRfnJ.gif', 'https://cdn.discordapp.com/attachments/825090653729456169/825090683765260388/3i9SyGnxMvL.gif', 'https://cdn.discordapp.com/attachments/825090653729456169/825090689800208384/g3fGIw70ZeB.gif', 'https://cdn.discordapp.com/attachments/825090653729456169/825090691684106270/nDchF0vJs3M.gif']
sad_list = ['https://cdn.discordapp.com/attachments/825091183234908200/825091270028034048/6NCYiaXakn5.gif', 'https://cdn.discordapp.com/attachments/825091183234908200/825091268970807346/1MPH4xL6wyM.gif', 'https://cdn.discordapp.com/attachments/825091183234908200/825091261806542889/zmRtMflCtAV.gif', 'https://cdn.discordapp.com/attachments/825091183234908200/825091258409811978/KYl87iM4Vbz.gif', 'https://cdn.discordapp.com/attachments/825091183234908200/825091255499096104/sLLhw_KTXzW.gif']
kill_list = ['https://cdn.discordapp.com/attachments/827524405315633163/827524453806243841/YIy0BmMjANn.gif', 'https://cdn.discordapp.com/attachments/827524405315633163/827524448075644939/Xufk1gBs8pl.gif', 'https://cdn.discordapp.com/attachments/827524405315633163/827524448126369802/bOtF4EdBbDJ.gif', 'https://cdn.discordapp.com/attachments/827524405315633163/827524444679438346/HaqpyGK874b.gif', 'https://cdn.discordapp.com/attachments/827524405315633163/827524445228367882/uOlyiKmmUhS.gif']
no_kill = ['https://cdn.discordapp.com/attachments/827527230401806366/827527260771844116/jz7xK5wHTUi.gif', 'https://cdn.discordapp.com/attachments/827527230401806366/827527267122151424/awPIyhKLM5T.gif']
responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "||Yes|| - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful.", "My reply is no.", "Why don't we partner", "Well i know but Won't Tell", "Why you like this type of question","No.", "||No|| - definitely.", "If you don't know about this how did you pass the School", "You Stupid", "I have doubt that your human or ....", "Your genius||Not Jk||", "Your genius ||JK||", "oh no you , not you again!", "why should i even tell you that?", "you are so dumb duh!", "Bruh"]



class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


async def GetMessage(
    bot, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return
    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs n stuff
     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
        - timeout (int) : Timeout for wait_for
    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
    or
     - False (bool) : If a timeout occurs
    """
    embed = discord.Embed(title=f"{contentOne}", description=f"{contentTwo}",)
    sent = await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False


class fun(commands.Cog):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.command(name="Cheer", description="send cheer full gif", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def cheer(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author
		usercolor = ctx.author.color
		rc = random.choice(cheer_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is cheering")
			em.set_image(url=rc)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is cheering for **{member.name}**")
			emm.set_image(url=rc)
			await ctx.reply(embed=emm, delete_after=60)

	@commands.command(name="Happy", description="Send happy gif", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def happy(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author
		usercolor = ctx.author.color
		rh = random.choice(happy_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is happy")
			em.set_image(url=rh)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{member.name}** Made **{ctx.author.name}**")
			emm.set_image(url=rh)
			await ctx.send(embed=emm, delete_after=60)

	@commands.command(name="Thumbsup", description="send thumbsup gif", usage="[optional: member]", aliases=['thunbs up'])
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def thumbsup(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author
		usercolor = ctx.author.color
		rhh = random.choice(thunbs_list)
		if member == ctx.author:

			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is giving a thumbsup")
			em.set_image(url=rhh)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is giving **{member.name}** a thumbsup")
			emm.set_image(url=rhh)
			await ctx.send(embed=emm, delete_after=60)

	@commands.command(name="Bonk", description="Bonk Some one's Head", usage="[member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def bonk(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author
		usercolor = ctx.author.color
		rb = random.choice(bonk_list)
		if member == ctx.author:
			await ctx.send("You can't bonk your self")
		else:
			emm = discord.Embed(color=usercolor, description=f"**{member.name}** got their head bonked by **{ctx.author}**")
			emm.set_image(url=rb)
			await ctx.message.send(embed=emm, delete_after=60)

	@commands.command(name="Dab", description="send Dab gif", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def dab(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author

		usercolor = ctx.author.color
		rd = random.choice(dab_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is dabbing")
			em.set_image(url=rd)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is dabbing With **{member.name}**")
			emm.set_image(url=rd)
			await ctx.send(embed=emm, delete_after=60)

	@commands.command(name="Sleep", description="send Sleepy gif", usage="")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def sleep(self, ctx):
		await ctx.message.delete()
		usercolor = ctx.author.color
		rs = random.choice(sleep_list)
		em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is Sleepy")
		em.set_image(url=rs)

		await ctx.message.send(embed=em, delete_after=60)

	@commands.command(name="Yes", description="send Yes gif", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def yes(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		member = member if member else ctx.author
		usercolor = ctx.author.color
		ry = random.choice(yes_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** Agrees")
			em.set_image(url=ry)
			await ctx.send(embed=em, delete_after=60)
		else:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** agrees with **{member.name}**")
			em.set_image(url=ry)
			await ctx.send(embed=em, delete_after=60)


	@commands.command(name="Cry", description="Send Crying Gif", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def cry(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		usercolor = ctx.author.color
		member = member if member else ctx.	author
		rcc = random.choice(cry_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is crying")
			em.set_image(url=rcc)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{member.name}** Made **{ctx.author.name}** cry")
			emm.set_image(url=rcc)
			await ctx.send(embed=emm, delete_after=60)

	@commands.command(name="Sad", description="send Sad gif", usage="[optional: member] ")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def sad(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		usercolor = ctx.author.color
		member = member if member else ctx.author
		sl = random.choice(sad_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is crying")
			em.set_image(url=sl)
			await ctx.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{member.name}** Made **{ctx.author.name}** Sad")
			emm.set_image(url=sl)
			await ctx.send(embed=emm, delete_after=60)

	@commands.command(name="Angry", description="Send Angry list", usage="[optional: member]")
	@commands.cooldown(3, 60, commands.BucketType.user)
	async def angry(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		usercolor = ctx.author.color
		member = member if member else ctx.author
		ra = random.choice(angry_list)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is Angry")
			em.set_image(url=ra)
			await ctx.message.send(embed=em, delete_after=60)
		else:
			emm = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is raging at **{member.name}**")
			emm.set_image(url=ra)
			await ctx.message.send(embed=emm, delete_after=60)

	@commands.command(name="kill", description="Kill some one it's Only For Joke ", usage="[member]")
	@commands.cooldown(3, 30, commands.BucketType.user)
	async def kill(self, ctx, member: discord.Member=None):
		await ctx.message.delete()
		usercolor = ctx.author.color
		member = member if member else ctx.author
		kill = random.choice(kill_list)
		Nkill	= random.choice(no_kill)
		if member == ctx.author:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is staying alive... *pouts*")
			em.set_image(url=Nkill)
			await ctx.send(embed=em, delete_after=60)
		else:
			em = discord.Embed(color=usercolor, description=f"**{ctx.author.name}** is murdering **{member.name}**")
			em.set_image(url=kill)
			await ctx.send(embed=em, delete_after=60)

	@commands.command(name="8Ball", description="Ask you question to bot", usage="[question]", aliases=['8b'])
	@commands.cooldown(3, 30, commands.BucketType.user)
	async def _8ball(self, ctx, *, question):
		await ctx.reply(f'Question: {question}\nAnswer: {random.choice(responses)}')

	@commands.command(name="dadjoke", description="Send a dad Joke", usage="" ,aliases=["djoke"])
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



def setup(bot):
	bot.add_cog(fun(bot))
