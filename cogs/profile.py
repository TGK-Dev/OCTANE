# basic dependencies
import discord
from discord.ext import commands

# aiohttp should be installed if discord.py is
import aiohttp

# PIL can be installed through
# `pip install -U Pillow`
from PIL import Image, ImageChops, ImageDraw, ImageFont

# partial lets us prepare a new function with args for run_in_executor
from functools import partial

# BytesIO allows us to convert bytes into a file-like byte stream.
from io import BytesIO

# this just allows for nice function annotation, and stops my IDE from complaining.
from typing import Union
from amari import AmariClient
import math
from datetime import timezone
import datetime
def circle(pfp, size = (215, 215)):

    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")

    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

def millify(n):
    n = float(n)
    millnames = ['',' Thousand',' Million',' Billion',' Trillion']
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

class ImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.Amari_api = AmariClient(self.bot.Amri_token)

    @commands.command(name="profile", description="Display user profile")
    #@commands.check_any(is_me())
    async def profile(self, ctx, member: discord.Member=None):
        print("start")
        member = member if member else ctx.author

        Id, status =str(member.id), str(member.status)

        name = f"{member.name[:16]}.." if len(member.name) > 16 else f"{member.name}#{member.discriminator}"
        if member.name == member.display_name:
            nick = None
        else:
            nick = f"{member.display_name[:16]}.." if len(member.display_name) > 16 else f"{member.display_name}"

        join = member.joined_at
        created = member.created_at
        now = datetime.datetime.now(timezone.utc)
        join_d = now - join
        year = join_d.days //365
        month = (join_d.days - year * 365) // 30

        if year < 1 and month > 1:
            joined_at = f"{month} Months Ago"
        elif year < 1 and month < 1:
            joined_at = f"{join_d.days} Days Ago"
        else:
            joined_at = f"{year} Year Ago"
        
        created_d = now - created
        year = created_d.days //365
        month = (created_d.days - year * 365) // 30

        if year < 1 and month > 1:
            created_at = f"{month} Months Ago"
        elif year < 1 and month < 1:
            created_at = f"{created_d.days} Days Ago"
        else:
            created_at = f"{year} Year Ago"

        
        

        leveldata = await self.Amari_api.fetch_user(ctx.guild.id, member.id)
        level = str(leveldata.level)
        moneydata = await self.bot.money.find(member.id)
        if not moneydata:
            money = "0"
        else:
            money = str(millify(moneydata['bal']))

        base = Image.open("base.png").convert("RGBA")
        background = Image.open("bg.png").convert("RGBA")

        pfp = member.avatar.with_format("png")
        pfp = pfp.with_size(256)
        data = BytesIO(await pfp.read())
        pfp = Image.open(data).convert("RGBA")

        draw = ImageDraw.Draw(base)
        pfp = circle(pfp, (215, 215))
        font = ImageFont.truetype("nunito-regular.ttf", size=38)
        akafont = ImageFont.truetype("nunito-regular.ttf", size=30)
        subfont = ImageFont.truetype("nunito-regular.ttf", size=25)

        draw.text((280, 240), name, font=font)
        if nick:
            draw.text((270, 315), nick, font=akafont)
        draw.text((65, 490), Id, font=subfont)
        draw.text((405, 490), status, font=subfont)
        draw.text((65, 635), str(money), font=subfont)
        draw.text((405, 635), str(level), font=subfont)
        draw.text((65, 770), created_at, font=subfont)
        draw.text((405, 770), joined_at, font=subfont)
        base.paste(pfp, (56, 158), pfp)
        background.paste(base, (0, 0), base)

        with BytesIO() as buffer:
            background.save(buffer, "png")
            buffer.seek(0)
            await ctx.send(file=discord.File(buffer, "profile.png"))

# setup function so this can be loaded as an extension
async def setup(bot: commands.Bot):
    await bot.add_cog(ImageCog(bot))