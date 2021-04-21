import discord
import DiscordUtils
import datetime
from discord.ext import commands
from discord.ext.buttons import Paginator

# Requires: pip install DiscordUtils

def fomat_time(time):
    return time.strftime('%d-%B-%Y %I:%m %p')


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



class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
        data = await self.bot.invites.find(inviter.id)
        
        if data is None:
            data = {"_id": inviter.id, "count": 0, "userInvited": []}

        data["count"] += 1
        data["userInvited"].append(member.id)
        await self.bot.invites.upsert(data)

        channel =  self.bot.get_channel(829008100555489301)
        embed = discord.Embed(timestamp=member.joined_at)
        embed.add_field(name=f"Member Information:", value=f"Name: {member.name}\n Member ID:\n {member.id}\nCreated at:\n{fomat_time(member.created_at)}")
        embed.add_field(name=f"Invited Information", value=f"Name: {inviter.name}\nInviter ID:{inviter.id}\nInviter account created at\n{fomat_time(inviter.created_at)}\nInvites: {data['count']}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        await channel.send(embed=embed)

    @commands.command(name="invites", description="Show user total Invites", usage="[Member]")
    async def invites(self, ctx ,member: discord.Member=None):
        member = member if member else ctx.author

        invites_filter = {"_id": member.id}

        invites = await self.bot.invites.find_many_by_custom(invites_filter)

        if not bool(invites):
            return await ctx.send(f"There is no Invites for the {member.name}")

        for invite in invites:
            count = (invite['count'])
            mcolor = member.color
            embed = discord.Embed(description=f"The User {member.name} Has `{count}` Invites", color=mcolor, timestamp=datetime.datetime.now())

            await ctx.send(embed=embed)
    @commands.command(name="inviter", description="find who Invited given user", usage="[member]")
    async def inviter(self, ctx, member: discord.Member):

        invites_filter = {"userInvited": member.id}

        invites = await self.bot.invites.find_many_by_custom(invites_filter)

        if not bool(invites):
            return await ctx.send("I failed to find vaild Entry in DataBase")

        for invite in invites:
            invier = (invite['_id'])
            mcolor = member.color
            embed = discord.Embed(description=f"The {member.mention} Is invited by <@{invier}>", timestamp=datetime.datetime.now())

            await ctx.send(embed=embed)





def setup(bot):
    bot.add_cog(Invites(bot))
