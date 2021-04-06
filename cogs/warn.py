import re
import discord
import datetime

from discord.ext import commands
from discord.ext.buttons import Paginator
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


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



class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(name="Warn", description="Gives an Warnings to user", usage="[member] [warn]")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await ctx.message.delete()
        if member.id in [ctx.author.id, self.bot.user.id]:
            return await ctx.send("You cannot warn yourself or the bot!")
        

        
        current_warn_count = len(
            await self.bot.warns.find_many_by_custom(
                {
                    "user_id": member.id,
                    "guild_id": member.guild.id
                }
            )
        ) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}
        
        await self.bot.warns.upsert_custom(warn_filter, warn_data)  
            
        try:
            await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count}**")
            await ctx.send(embed=em)
        except discord.HTTPException:
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been Warned I couldn't DM them.| Warnings Count {current_warn_count}**")
            await ctx.send(embed=emb)
        
        log_channel = self.bot.get_channel(803687264110247987)

        embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
        embed.add_field(name="User", value=f"{member.name}", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
        embed.add_field(name="threshold Action", value="None")
        embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

        await log_channel.send(embed=embed)

    @commands.command(name="Warnings", description="Show All Warnings for User", usage="[member]")
    @commands.has_permissions(manage_messages=True)
    async def Warnings(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)
        
        if not bool(warns):
            return await ctx.send(f"Couldn't find any warns for: `{member.display_name}`")
        
        warns = sorted(warns, key=lambda x: x["number"])
        
        pages = []
        for warn in warns:
            description = f"""
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
            length=1
        ).start(ctx)


def setup(bot):
    bot.add_cog(Warns(bot))
"""
        embed = discord.Embed(
            title="You are being warned:",
            description=f"__**Reason**__:\n{reason}",
            colour=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Warn: {current_warn_count}")
"""


"""
if current_warn_count == 5:

            data = {
                '_id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': 1140,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }

            await self.bot.mutes.upsert(data)
            self.bot.muted_users[member.id] = data

            await member.add_roles(role)

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Frist threshold Reached Muted You have been muted for 1 Day")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Frist threshold Reached Muted User for 1 Day **")
                await ctx.send(embed=em)
                
                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Day")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Frist threshold Reached Muted User for 1 Day |Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Day")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

        elif current_warn_count == 10:

            data = {
                '_id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': 10080,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }

            await self.bot.mutes.upsert(data)
            self.bot.muted_users[member.id] = data

            await member.add_roles(role)

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Second threshold Reached Muted YOu have been for muted 1 Week")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Second threshold Reached Muted User for 1 Week **")
                await ctx.send(embed=em)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Week")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Second threshold Reached Muted User for 1 Day |Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Week")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


        elif current_warn_count == 15:
            
            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Third threshold Reached You have Been Kicked")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Third threshold Reached user Has Been Kicked **")
                await ctx.send(embed=em)
                await ctx.guild.kick(user=member, reason=f"15 Warnings Reached")
                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Kicked")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Third threshold Reached user Has Been Kicked | Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)
                await ctx.guild.kick(user=member, reason=f"15 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Kicked")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

        elif current_warn_count == 20:

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Third threshold Reached user Has Been Banned **")
                await ctx.send(embed=em)
                await ctx.guild.ban(user=member, reason=f"20 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Banned")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)
                
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Third threshold Reached user Has Been Banned | Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)
                await ctx.guild.ban(user=member, reason=f"20 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Banned")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)
        
        else:  
            
            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count}**")
                await ctx.send(embed=em)
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been Warned I couldn't DM them.| Warnings Count {current_warn_count}**")
                await ctx.send(embed=emb)
"""