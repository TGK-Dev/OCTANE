import DiscordUtils
import datetime
import discord
import os
from discord.ext import commands
from utils.checks import Commands_Checks, Dynamic_cooldown
from discord import app_commands

def fomat_time(time):
    return time.strftime('%d-%B-%Y %I:%m %p')

description = "Invites Systems"


class Invites(commands.Cog, name="Invites",description=description):
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
        if member.guild.id != 785839283847954433:
            return
        inviter = await self.tracker.fetch_inviter(member)
        if inviter is None:
            return
        data = await self.bot.invites.find(inviter.id)

        if data is None:
            data = {"_id": inviter.id, "count": 0, "userInvited": []}

        data["count"] += 1
        data["userInvited"].append(member.id)
        await self.bot.invites.upsert(data)

    @app_commands.command(name="invites", description="Show the invites of a user")
    @app_commands.guilds(785839283847954433)
    @app_commands.checks.dynamic_cooldown(Dynamic_cooldown.is_me)   
    @app_commands.describe(member="The member you want to check the invites of")
    async def invites(self, interaction: discord.Interaction, member: discord.Member=None):
        member = member if member else interaction.author
        await interaction.response.defer(thinking=True)
        invites_filter = {"_id": member.id}

        invites = await self.bot.invites.find(invites_filter)

        if not invites:
            return await interaction.followup.send(f"There is no Invites for the {member.name}")

        count = (invites['count'])
        mcolor = member.color
        embed = discord.Embed(
            description=f"The User {member.name} Has `{count}` Invites", color=mcolor, timestamp=datetime.datetime.now())

        await interaction.followup.send(embed=embed)

    @commands.command(name="inviter", description="Find out who invited who")
    @commands.check_any(Commands_Checks.is_me(), Commands_Checks.is_owner(), Commands_Checks.can_use())
    async def inviter(self, ctx, member: discord.Member):

        invites_filter = {"userInvited": member.id}

        data = await self.bot.invites.find_by_custom(invites_filter)

        if not bool(data):
            return await ctx.send("I failed to find vaild Entry in DataBase")

        embed = discord.Embed(
            color=0x2f3136, description=f"{member.mention} Was invited by <@{data['_id']}>")
        await ctx.send(embed=embed)
    
    @commands.command()
    async def invited(self, ctx, user: discord.Member):
        data = await self.bot.invites.find_by_custom({'_id': user.id})
        if not data: return await ctx.send("No data Found")

        invited_users = list(set(data['userInvited']))

        if len(invited_users) <= 10:
            
            embed = discord.Embed(description="")
            for i in invited_users:
                embed.description += f"{int(i)}\n"
            return await ctx.send(f"here is list of all user invited by {user.mention}", embed=embed)
        
        with open("ids_list.txt", "w") as file:
            for i in invited_users: 
                file.write(f"{int(i)}\n")
        
        with open("ids_list.txt", "rb") as file:
            await ctx.send(f"Here is list of all user invited by {user.mention}", file=discord.File(file, f"Users Invited by {user.name}| {user.id}.txt"))
        os.remove("ids_list.txt")

async def setup(bot):
    await bot.add_cog(Invites(bot))