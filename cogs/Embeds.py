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
        print(f"{self.__class__.__name__} Cog is loaded\n-----")

    @commands.command(name="embed", description="Commands to make an embed")
    @commands.check_any(is_me(), perm_check())
    async def embed(self, ctx, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        data = {'type': 'rich'}
        try:
            await ctx.send("Send Embed Titile if dont wan't title send `None`")
            title = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)

            await ctx.send("Send Embed description if don't description send `None`")
            description = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)

            await ctx.send("Send Embed footer if don't wan't footer send `None`")
            footer = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)            

            await ctx.send("Send Embed color like `2f3136` if don't wan't color send `None`")
            color = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=30)            

            if str(title.content.lower()) == 'none':
                pass
            else:
                data['title'] = title.content

            if str(description.content.lower()) == 'none':
                pass
            else:
                data['description'] = description.content

            if str(footer.content.lower()) == 'none':
                pass
            else:
                data['footer'] = {'text': f'{footer.content}'}

            if str(color.content.lower()) == 'none':
                pass
            else:
                color = int(color.content, 16)
                data['color'] = color

            embed = discord.Embed

            await ctx.send(embed=embed.from_dict(data))
            await ctx.send("Your Embed has been sent")

        except asyncio.TimeoutError:
            await ctx.send("TimeoutError try again later.")





def setup(bot):
    bot.add_cog(Embeds(bot))