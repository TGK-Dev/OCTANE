from discord.ext import commands
import discord
import asyncio

description= "An Commands To edit / Create Embeds"
class Embeds(commands.Cog, description=description):
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

    @commands.command(name="embed", description="Create An Embed")
    @commands.check_any(perm_check(), is_me())
    async def embed(self, ctx, channel: discord.TextChannel=None):
    	channel = channel if channel else ctx.channel
    	data = {'type': 'rich'}
    	try:
    		msg = await ctx.send("Send Embeds title don't want title type `None`")
    		title = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)
    		if str(title.content.lower()) == "none":
    			await msg.delete()
    			print(f'None print | {data}')
    		else:
	    		data['title'] = title.content
	    		await msg.delete()
	    		print(f'Not None print | {data}')
    		

    		msg = await ctx.send("Send Embeds description")
    		description = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)

    		data['description'] = description.content
    		await msg.delete()
    		

    		msg = await ctx.send("Send Embeds Color Hex Code like `2f3136`")
    		color = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)
    		color = int(color.content, 16)

    		data['color'] = color
    		await msg.delete()
    		

    		embed = discord.Embed()

    		await channel.send(embed=embed.from_dict(data))
    		print(data)
    	except asyncio.TimeoutError:
    		await ctx.send("TimeoutError Try Again later")




def setup(bot):
    bot.add_cog(Embeds(bot))

