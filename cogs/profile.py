import discord
from discord.ext import commands
import aiohttp
from PIL import Image, ImageChops, ImageDraw, ImageFont
from functools import partial
from io import BytesIO
from typing import Union
from amari import AmariClient
import math
from datetime import timezone
import datetime
from discord import app_commands

def get_time(time: datetime.datetime):
    now = datetime.datetime.now(timezone.utc)
    new_time = now - time
    year = new_time.days // 365
    month = (new_time.days - year * 365) // 30
    if new_time.days <= 0:
        return f"Today"
    elif new_time.days <= 30:
        return f"{new_time.days} days ago"
    elif year < 1 and month > 1:
        return f"{month} Months Ago"
    else:
        return f"{year} Year Ago"

def get_status(member: discord.Member, moneydata: dict= None):
    owner_role = discord.utils.get(member.guild.roles, id=785842380565774368)
    staff_role = discord.utils.get(member.guild.roles, id=818129661325869058)
    og_role = discord.utils.get(member.guild.roles, id=931072410365607946)
    grinder = discord.utils.get(member.guild.roles, id=836228842397106176)
    if owner_role in member.roles:
        return "King"
    elif  member.guild_permissions.administrator:
        return "Chief"
    elif member.guild_permissions.manage_messages and member.guild_permissions.ban_members:
        return "Moderator"
    elif member.guild_permissions.manage_messages and not member.guild_permissions.ban_members:
        return "Ministers"
    elif staff_role in member.roles:
        return "Ministers"
    elif grinder in member.roles:
        return "Grinder"
    elif moneydata != None and moneydata['bal'] > 25000000:
        return "Treasury"
    elif og_role in member.roles:
        return "Loyal member"
    else:
        return "Member"
    
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

def is_me(interaction: discord.Interaction):
    return interaction.user.id in [488614633670967307, 301657045248114690]
    
class ImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.Amari_api = AmariClient(self.bot.Amari_token)

    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.command(name="profile", description="Display user profile")
    @app_commands.guilds(discord.Object(785839283847954433))
    @app_commands.describe(member="The user you want to display profile of")
    async def profile(self, interaction: discord.Interaction, member: discord.Member=None):
        await interaction.response.defer(thinking=True)
        member = member if member else interaction.user
        if member.bot:
            return await interaction.response.send_message("Stop Staking us", ephemeral=True)
        Id =str(member.id)

        name = f"{member.name[:16]}.." if len(member.name) > 16 else f"{member.name}#{member.discriminator}"
        if member.name == member.display_name:
            nick = None
        else:
            nick = f"AKA - {member.display_name[:16]}.." if len(member.display_name) > 16 else f"{member.display_name}"

        leveldata = await self.Amari_api.fetch_user(interaction.guild.id, member.id)
        level = str(leveldata.level)
        moneydata = await self.bot.money.find(member.id)

        if not moneydata:
            money = "0"
        else:
            money = str(f"{millify(moneydata['bal'])}")

        created_at = get_time(member.created_at)
        joined_at = get_time(member.joined_at)
        status = get_status(member, moneydata)

        base = Image.open("assets/base.png").convert("RGBA")
        background = Image.open("assets/bg.png").convert("RGBA")

        if not member.avatar:
            pfp = member.default_avatar.with_format("png")
        else:
            pfp = member.avatar.with_format("png")
        pfp = pfp.with_size(256)
        data = BytesIO(await pfp.read())
        pfp = Image.open(data).convert("RGBA")

        draw = ImageDraw.Draw(base)
        pfp = circle(pfp, (215, 215))
        font = ImageFont.truetype("assets/nunito-regular.ttf", size=38)
        akafont = ImageFont.truetype("assets/nunito-regular.ttf", size=30)
        subfont = ImageFont.truetype("assets/nunito-regular.ttf", size=25)

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
            await interaction.followup.send(file=discord.File(buffer, "profile.png"))

# setup function so this can be loaded as an extension
async def setup(bot: commands.Bot):
    await bot.add_cog(ImageCog(bot))