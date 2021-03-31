import discord
import typing 
from datetime import datetime
from discord.ext import commands


class Channels(commands.Cog):
    """docstring for Example"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Channels Cogs is Loaded')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(color=0xff0000, description=f'The {channel.name} is lock for {role.mention}')
        await channel.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):

        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is unlock for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(aliases=['sm'])
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, ctx, time: str = '0'):

        unit = ['h', 'H', 'm', 'M', 's', 'S']

        cd = 0
        if time[-1] in unit:
            unit = time[-1]
            cd = int(time[:-1])
            if unit == 'h' or unit == 'H':
                cd = cd * 60 * 60
            elif unit == 'm' or unit == 'M':
                cd = cd * 60
            else:
                cd = cd
        else:
            cd = int(time) if time else 0


        await ctx.message.delete()
        if cd > 21600:
            await ctx.send(f"Slowmode interval can't be greater than 6 hours.")
        elif cd == 0:
            await ctx.channel.edit(slowmode_delay=cd)
            await ctx.send(f"Slowmode has been removed!! 🎉")
        else:
            await ctx.channel.edit(slowmode_delay=cd)
            if unit == 'h' or unit == 'H':
                await ctx.send(f'Slowmode interval is now **{int(cd/3600)} hours**.')
            elif unit == 'm' or unit == 'M':
                await ctx.send(f'Slowmode interval is now **{int(cd/60)} mins**.')
            else:
                await ctx.send(f'Slowmode interval is now **{cd} secs**.')
       
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def hide(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        channel = channel if channel else ctx.channel
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Hidded for for {role.mention}')
        await ctx.send(embed=embed, delete_after=10)
        await ctx.message.delete()

        await ctx.send(embed=embed)


    @commands.command(aliases=['uhide'])
    @commands.has_permissions(ban_members=True)
    async def unhide(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        channel = channel if channel else ctx.channel
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Not Hidded for for {role.mention}')
        await ctx.send(embed=embed, delete_after=10)



 
def setup(bot):
    bot.add_cog(Channels(bot))
#role = discord.utils.get(ctx.guild.roles, name="")