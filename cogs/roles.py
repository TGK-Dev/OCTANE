import re
import datetime
from copy import deepcopy
from discord.ext.buttons import Paginator
import asyncio
import discord
from discord.ext import commands, tasks
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

class roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="roleinfo", description="members with this role", usage="[role.id]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def roleinfo(self, ctx, role: discord.Role=None):
        def fomat_time(time):
          return time.strftime('%d-%B-%Y %I:%m %p')

        role_color = role.color
        embed = discord.Embed(title=f"Role Infomation for {role.name}", color=role_color)
        embed.add_field(name=f"Name:", value=f"{role.name}")
        embed.add_field(name=f"Members:", value=f"{len(role.members)}", inline=False)
        embed.add_field(name=f"Created At", value=fomat_time(role.created_at))
        embed.add_field(name=f"color", value=f"{role.color}", inline=False)
        embed.set_footer(text=f"ID {role.id}")

        await ctx.send(embed=embed, delete_after=60)

    @commands.command(name="role", description="add Role fored user", usage="[member][role]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376)
    async def role(self, ctx, member:discord.Member, role: discord.Role):
        roles = member.roles
        await ctx.message.delete()
        if role in roles:
            await member.remove_roles(role)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed {role} from {member}")
            await ctx.send(embed=embed)
        else:
            await member.add_roles(role)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Added {role} from {member}")
            await ctx.send(embed=embed)

   

    @commands.command(name="Pings", description="Give numbers of some the pings roles", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def pings(self, ctx):
        await ctx.message.delete()

        heist = discord.utils.get(ctx.guild.roles, id=804068344612913163 )
        partner_heist = discord.utils.get(ctx.guild.roles, id=804069957528584212)
        giveaway = discord.utils.get(ctx.guild.roles, id=800685251276963861)
        othere_heist = discord.utils.get(ctx.guild.roles, id=806795854475165736)
        danker = discord.utils.get(ctx.guild.roles, id=801392998465404958)
        partnership = discord.utils.get(ctx.guild.roles, id=797448080223109120)

        embed = discord.Embed(title=f"Showing some pings counts",
            description=f"{heist.mention} = {len(heist.members)}\n-----\n{partner_heist.mention} = {len(partner_heist.members)}\n-----\n{othere_heist.mention} = {len(othere_heist.members)}\n-----\n{danker.mention} = {len(danker.members)}\n-----\n{partnership.mention} = {len(partnership.members)}\n-----\n{giveaway.mention} = {len(giveaway.members)}", color=0x06f79e)

        await ctx.send(embed=embed, delete_after=60)


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
