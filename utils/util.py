import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import re
import discord
from discord.ext.buttons import Paginator

class Amari:
    def __init__(self):
        self.session = ClientSession()

    async def get_amari_rank(self, guild: int, user: discord.User):
        gid = guild
        username = user.name
        url = f"https://lb.amaribot.com/weekly.php?gID={gid}"

        async with self.session.request("GET", url) as response:
            text = await response.text()
        obj = BeautifulSoup(text, "html.parser")
        rank_list = obj.body.main.findAll("div")[2].div.find("table").findAll("tr")
        tag = None
        for tag in rank_list:
            if username in str(tag):
                break
        check = re.compile(
                r"<tr><td>(\d+)<\/td><td>({})<\/td><td>(\d+)<\/td><td>(\d+)<\/td><\/tr>".format(
                    re.escape(username)
                )
            )
        
        if not tag:
            return None
        match = re.match(check, str(tag))

        try:
            return int(match.group(4))
        except (TypeError, AttributeError):
            return 0

    async def get_weekly_rank(self, guild: int, user: discord.User):
        gid = guild
        username = user.name
        url = f"https://lb.amaribot.com/weekly.php?gID={gid}"

        async with self.session.request("GET", url) as response:
            text = await response.text()
        obj = BeautifulSoup(text, "html.parser")
        rank_list = obj.body.main.findAll("div")[2].div.find("table").findAll("tr")
        tag = None
        for tag in rank_list:
            if username in str(tag):
                break
        check = re.compile(
                r"<tr><td>(\d+)<\/td><td>({})<\/td><td>(\d+)<\/td><td>(\d+)<\/td><\/tr>".format(
                    re.escape(username)
                )
            )
        if not tag:
            return
        match = re.match(check, str(tag))

        try:
            return int(match.group(3))
        except (TypeError, AttributeError):
            return 0

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


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content