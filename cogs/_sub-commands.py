import discord
from discord.ext import commands

# See channels.py for this being used on the bot


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


class Groups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.group(invoke_without_command=True)
    async def first(self, ctx):
        await ctx.send("This is the first command layer")

    @first.group(invoke_without_command=True)
    async def second(self, ctx, channelId=None):
        if channelId != None:
            channel = self.bot.get_channel(int(channelId))
            await channel.send(
                "Hey! This is a message from me the bot. Bet you didn't see who ran the command?",
                delete_after=15,
            )

    @second.command()
    async def third(self, ctx, channelId=None):
        await ctx.message.author.send("Hey! Did this come through clearly?")


def setup(bot):
    bot.add_cog(Groups(bot))
