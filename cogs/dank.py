import random
import asyncio
import discord
from discord.ext import commands
from discord.ext.buttons import Paginator

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

class dank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def our_custom_check():
        async def predicate(ctx):
            return ctx.guild is not None \
                and ctx.author.guild_permissions.manage_channels \
                and ctx.me.guild_permissions.manage_channels
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="dankdown",
        description="Use this commands when dank is down",
        usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def dankdown(self, ctx):
        async with ctx.typing():
            role = ctx.guild.default_role

            dank_1 = self.bot.get_channel(799364834927968336)
            dank_2 = self.bot.get_channel(799378297855279125)
            dank_pre = self.bot.get_channel(812724720675061770)
            dank_vip = self.bot.get_channel(822409174271918120)

            override_dank_1 = dank_1.overwrites_for(role)
            override_dank_1.send_messages = False

            override_dank_2 = dank_2.overwrites_for(role)
            override_dank_2.send_messages = False

            override_dank_pre = dank_pre.overwrites_for(role)
            override_dank_pre.send_messages = False

            override_dank_vip = dank_vip.overwrites_for(role)
            override_dank_vip.send_messages = False

            await dank_1.set_permissions(role, overwrite=override_dank_1)
            await dank_2.set_permissions(role, overwrite=override_dank_2)
            await dank_pre.set_permissions(role, overwrite=override_dank_pre)
            await dank_vip.set_permissions(role, overwrite=override_dank_vip)

            embed = discord.Embed(
                title="Dank is Down",
                color=0xff0000,
                description="The Dank memer is Down in mean time head to the <#785847439579676672> and chat with other"
            )

            await dank_1.send(embed=embed)
            await dank_2.send(embed=embed)
            await dank_pre.send(embed=embed)
            await dank_vip.send(embed=embed)

        await ctx.send("Dank is LockedUp")


    @commands.command(
        name="dankup",
        description="Use this commands when dank is Comes Back",
        usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def dankup(self, ctx):
        async with ctx.typing():
            role = ctx.guild.default_role

            dank_1 = self.bot.get_channel(799364834927968336)
            dank_2 = self.bot.get_channel(799378297855279125)
            dank_pre = self.bot.get_channel(812724720675061770)
            dank_vip = self.bot.get_channel(822409174271918120)

            override_dank_1 = dank_1.overwrites_for(role)
            override_dank_1.send_messages = None

            override_dank_2 = dank_2.overwrites_for(role)
            override_dank_2.send_messages = None

            override_dank_pre = dank_pre.overwrites_for(role)
            override_dank_pre.send_messages = None

            override_dank_vip = dank_vip.overwrites_for(role)
            override_dank_vip.send_messages = None

            await dank_1.set_permissions(role, overwrite=override_dank_1)
            await dank_2.set_permissions(role, overwrite=override_dank_2)
            await dank_pre.set_permissions(role, overwrite=override_dank_pre)
            await dank_vip.set_permissions(role, overwrite=override_dank_vip)
        
            await dank_1.purge(limit=1)
            await dank_2.purge(limit=1)
            await dank_pre.purge(limit=1)
            await dank_vip.purge(limit=1)

            embed = discord.Embed(
                title="Dank is Back",
                color=0xff0000,
                description="The Dank memer is Back to Grinding"
            )

            await dank_1.send(embed=embed)
            await dank_2.send(embed=embed)
            await dank_pre.send(embed=embed)
            await dank_vip.send(embed=embed)

        await ctx.send("Dank is unlocked")
#Hesits Settings 
    

    @commands.command(name="Heist", description="Setup an Heist",usage="[host] [ammout] [starter] [req role] ")
    async def hesit(self, ctx, host: discord.Member, ammout, starter: discord.Member=None,req_role: discord.Role=None):
        starter = starter if starter else ctx.author
        starter_role = discord.utils.get(ctx.guild.roles, name="Hest Starter")
        channel = ctx.channel
        req_role = req_role if req_role else ctx.guild.default_role

        embed = discord.Embed(title="Heist!",
            description=f"{host.mention} will be hosting a heist!")
        embed.add_field(name="Checklist", value=f"- disable passive mode ``(pls settings passive disable)``\n- withdraw 2,000 coins ``(pls with 2000)``\n- you must have the {req_role.mention} role to join")
        await ctx.send(embed=embed)


        await starter.add_roles(starter_role)
        await ctx.send(f"**{host.display_name}**")
        await ctx.send(" <a:60s:831979067107573780> Searching for heist in this channel")
        try:

            await self.bot.wait_for("message", check=lambda m: m.content.startswith(f"**{host.display_name}**"), timeout=60)

            await channel.set_permissions(req_role, send_messages=True)

            await ctx.send(f"unlocked channel for ``{req_role.name}``")
            await asyncio.sleep(5)
            await starter.remove_roles(starter_role)

            try:
                await self.bot.wait_for("message", check=lambda m: m.author.id == 488614633670967307 and m.content.startswith("Time is up to join"), timeout=240)
                await ctx.channel.edit(sync_permissions=True)
                await ctx.send("channel Lock bceause Time's Up")

            except asyncio.TimeoutError:

                await ctx.channel.edit(sync_permissions=True)
                await ctx.send("channel Lock bceause Time's Up")
        except asyncio.TimeoutError:
            await ctx.send("No hesit Found Please Try Again")

        



def setup(bot):
    bot.add_cog(dank(bot))
