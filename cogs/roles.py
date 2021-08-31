import asyncio
import datetime
import discord

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
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # geting All Info mantions
    @commands.command(name="roleinfo", description="Give Infomation Abouth Role", usage="[Role]")
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
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

    # getting Mutual Pings
    @commands.command(name="mping", description="Mutual Pings for tow role", usage="[role 1] [role 2]",)
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def mping(self, ctx, role1: discord.Role, role2: discord.Role):
        pings1 = role1.members
        pings2 = role2.members

        if role1 == role2:
            return await ctx.send("you can't use same role for mutual pings")

        embed = discord.Embed(title="Mutual Pings", color=0xF1C40F,
                              description=f"Showing Mutual pings for the two Role\n1.Role {role1.mention} total members: {len(pings1)}\n2.Role{role2.mention} total members: {len(pings2)}\n\n**Unique Members are: {int(len(pings1) + len(pings2) - len(comman_ping(pings1, pings2)))}**")  # (comman_ping(pings1, pings2))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(roles(bot))


"""
 @commands.command(name="temprole", description="add the Temp role to user", usage="[member] [role.id]")
    @commands.has_any_role(785842380565774368, 799037944735727636, 785845265118265376)
    async def temprole(self, ctx, member: discord.Member, role: discord.Role, *, time: TimeConverter=None):
        await ctx.message.delete()
        
        data = {
            '_id': member.id,
            'temp_role': role.name,
            'temp_roledAt': datetime.datetime.now(),
            'temp_roleDuration': time,
            'temptedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.temp_roles.upsert(data)
        self.bot.temp_roled_users[member.id] = data

        await member.add_roles(role)

        if time and time < 30:
            await asyncio.sleep(time)

            if role in member.role:
                await member.remove_roles(role)

            await self.bot.temp_roles.delete(member.id)
            try:
                self.bot.temp_roled_users.pop(member.id)
            except  KeyError:
                pass
"""
"""
Taskks 
"""
"""
        self.temp_role_task = self.check_current_temp_roles.start()

        def cog_unload(self):
            self.temp_role_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_temp_roles(self):
        currentTime = datetime.datetime.now()
        temp_roles = deepcopy(self.bot.temp_roled_users)
        for key, value in temp_roles.items():
            if value['temp_roleDuration'] is None:
                continue

            untemp_roleTime = value['temp_roledAt'] + relativedelta(seconds=value['temp_roleDuration'])

            if currentTime >= untemp_roleTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name=f"{value['temp_role']}")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Untemp_roled: {member.display_name}")

                await self.bot.temp_roles.delete(member.id)
                try:
                    self.bot.temp_roled_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_temp_roles.before_loop
    async def before_check_current_temp_roles(self):
        await self.bot.wait_until_ready()
"""
