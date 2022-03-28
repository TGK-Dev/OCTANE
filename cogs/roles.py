import asyncio
import datetime
import discord
from utils.checks import checks
from discord.ext import commands

description = "Role Mangement Commands"

def comman_ping(role1, role2):
    ping1 = set(role1)
    ping2 = set(role2)

    if len(ping1.intersection(ping2)) > 0:
        return(ping1.intersection(ping2))
    else:
        return("no common elements")


def fomat_time(time):
    return time.strftime('%d-%B-%Y %I:%m %p')

class roles(commands.Cog,  description=description):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # geting All Info mantions
    @commands.command(name="roleinfo", description="Give Infomation Abouth Role", usage="[Role]")
    @commands.check_any(checks.can_use())
    async def roleinfo(self, ctx, *, role: discord.Role = None):
        if role == None:
            return await ctx.send("Looks like you forget to add role")

        if role == int:

            role = discord.utils.get(ctx.guild.roles, id=role)
        else:
            role = discord.utils.get(ctx.guild.roles, name=f"{role}")

        await ctx.message.delete()

        role_color = role.color
        embed = discord.Embed(title=f"Role Infomation for {role.name}", color=role_color,
                              description=f"**Name**: {role.name}\n**Role ID**: {role.id}\n**Created At**:{fomat_time(role.created_at)}\n**Role color**: {role.color}\n**Tatol Members**:{len(role.members)}\n**hoist**: {role.hoist}\n**Mentionable** {role.mentionable}")
        await ctx.send(embed=embed, delete_after=60)

    # Added Roel/Remove to any User
    @commands.command(name="role", description="add/Remove role from user", usage="[member][role]")
    @commands.check_any(checks.can_use())
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        if role == None:
            return await ctx.send("Looks like you forget to add role")

        if role == int:

            role = discord.utils.get(ctx.guild.roles, id=role)
        else:
            role = discord.utils.get(ctx.guild.roles, name=f"{role}")

        if role >= ctx.author.top_role:
            return await ctx.send("You can't You cannot do this action due to role hierarchy.")

        roles = member.roles
        await ctx.message.delete()
        if role in roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                description=f"<:allow:819194696874197004> | {role} Removed from {member}")
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(
                description=f"<:allow:819194696874197004> | {role} Added to {member}")
            await ctx.send(embed=embed)

    # some Important roles members count

    @commands.command(name="Pings", description="Members count of some Roles", usage="")
    @commands.check_any(checks.can_use())
    async def pings(self, ctx):
        await ctx.message.delete()

        heist = discord.utils.get(ctx.guild.roles, id=804068344612913163)
        partner_heist = discord.utils.get(
            ctx.guild.roles, id=804069957528584212)
        othere_heist = discord.utils.get(
            ctx.guild.roles, id=806795854475165736)
        danker = discord.utils.get(ctx.guild.roles, id=801392998465404958)
        partnership = discord.utils.get(ctx.guild.roles, id=797448080223109120)

        embed = discord.Embed(title=f"Showing some pings counts",
                              description=f"{heist.mention} = {len(heist.members)}\n-----\n{partner_heist.mention} = {len(partner_heist.members)}\n-----\n{othere_heist.mention} = {len(othere_heist.members)}\n-----\n{danker.mention} = {len(danker.members)}\n-----\n{partnership.mention} = {len(partnership.members)}", color=0x06f79e)

        await ctx.send(embed=embed, delete_after=60)


def setup(bot):
    bot.add_cog(roles(bot))