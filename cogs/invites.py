import DiscordUtils
import datetime
import discord

from discord.ext import commands
from utils.util import Pag

guild_ids = [797920317871357972, 785839283847954433]
# Requires: pip install DiscordUtils


def fomat_time(time):
    return time.strftime('%d-%B-%Y %I:%m %p')


description = "Invites Systems"


class Invites(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636,
                        785845265118265376, 787259553225637889, 843775369470672916]
            for mod in mod_role:
                role = discord.utils.get(ctx.guild.roles, id=mod)
                if role in ctx.author.roles:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
                    return (ctx.command.name in check)
        return commands.check(predicate)

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
        inviter = await self.tracker.fetch_inviter(member)
        if inviter is None:
            return
        data = await self.bot.invites.find(inviter.id)

        if data is None:
            data = {"_id": inviter.id, "count": 0, "userInvited": []}

        data["count"] += 1
        data["userInvited"].append(member.id)
        await self.bot.invites.upsert(data)

        channel = self.bot.get_channel(829008100555489301)
        embed = discord.Embed(timestamp=member.joined_at)
        embed.add_field(name=f"Member Information:",
                        value=f"Name: {member.name}\n Member ID:\n {member.id}\nCreated at:\n{fomat_time(member.created_at)}")
        embed.add_field(name=f"Invited Information",
                        value=f"Name: {inviter.name}\nInviter ID:{inviter.id}\nInviter account created at\n{fomat_time(inviter.created_at)}\nInvites: {data['count']}", inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=member.guild.name,
                         icon_url=member.guild.icon.url)
        await channel.send(embed=embed)

    @commands.command(name="invites", description="Show user total Invites", usage="[Member]")
    async def invites(self, ctx, member: discord.Member = None):
        member = member if member else ctx.author

        invites_filter = {"_id": member.id}

        invites = await self.bot.invites.find_many_by_custom(invites_filter)

        if not bool(invites):
            return await ctx.send(f"There is no Invites for the {member.name}")

        for invite in invites:
            count = (invite['count'])
            mcolor = member.color
            embed = discord.Embed(
                description=f"The User {member.name} Has `{count}` Invites", color=mcolor, timestamp=datetime.datetime.now())

            await ctx.send(embed=embed)

    @commands.command(name="inviter", description="Find out who invited who")
    @commands.check_any(perm_check(), is_me())
    async def inviter(self, ctx, member: discord.Member):

        invites_filter = {"userInvited": member.id}

        data = await self.bot.invites.find_by_custom(invites_filter)

        if not bool(data):
            return await ctx.send("I failed to find vaild Entry in DataBase")

        embed = discord.Embed(
            color=0x2f3136, description=f"{member.mention} Was invited by <@{data['_id']}>")
        await ctx.send(embed=embed)

    @commands.command(name='ilb', description="invites leaderboard")
    async def ilb(self, ctx):
        invites = await self.bot.invites.get_all()

        invites = sorted(invites, key=lambda x: x["count"], reverse=True)
        i = 1
        pages = []
        for invite in invites:
            description = f"""
            {i}.Member: <@{invite['_id']}>
            Toal Inivits: {invite['count']}
            """
            i += 1
            pages.append(description)

        await Pag(
            title=f"Inivits leaderboard",
            colour=0xCE2029,
            entries=pages,
            length=5
        ).start(ctx)


def setup(bot):
    bot.add_cog(Invites(bot))
