import random

import discord
from discord.ext import commands
from discord.ext.buttons import Paginator


class txt_manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def our_custom_check():
        async def predicate(ctx):
            return ctx.guild is not None \
                and ctx.author.guild_permissions.manage_channels \
                and ctx.me.guild_permissions.manage_channels
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name="channelstats",
        aliases=["cs"],
        description="Sends a nice fancy embed with some channel stats",
        usage="[channel]",
    )
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def channelstats(self, ctx):
        channel = ctx.channel

        embed = discord.Embed(
            title=f"Stats for **{channel.name}**",
            description=f"{'Category: {}'.format(channel.category.name) if channel.category else 'This channel is not in a category'}",
            color=random.choice(self.bot.color_list),
        )
        embed.add_field(name="Channel Guild", value=ctx.guild.name, inline=False)
        embed.add_field(name="Channel Id", value=channel.id, inline=False)
        embed.add_field(
            name="Channel Topic",
            value=f"{channel.topic if channel.topic else 'No topic.'}",
            inline=False,
        )
        embed.add_field(name="Channel Position", value=channel.position, inline=False)
        embed.add_field(
            name="Channel Slowmode Delay", value=channel.slowmode_delay, inline=False
        )
        embed.add_field(name="Channel is nsfw?", value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Channel is news?", value=channel.is_news(), inline=False)
        embed.add_field(
            name="Channel Creation Time", value=channel.created_at, inline=False
        )
        embed.add_field(
            name="Channel Permissions Synced",
            value=channel.permissions_synced,
            inline=False,
        )
        embed.add_field(name="Channel Hash", value=hash(channel), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="lock", description="Lock the given channel For mentioned Role", usage="[channel] [Role]",)
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def lock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):

        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is Lock for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="unlock", description="UnLock the given channel For mentioned Role", usage="[channel] [Role]",)
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def unlock(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):

        channel = channel if channel else ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x02ff06, description=f'The {channel.name} is unlock for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
    @commands.has_any_role(785842380565774368, 799037944735727636, 785845265118265376, 787259553225637889)
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


    @commands.command(name="Hide", description="Hide Channels For mentioned Role", usage="[channel] [role]")
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def hide(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        channel = channel if channel else ctx.channel
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Hidded for for {role.name}')
        await ctx.send(embed=embed, delete_after=10)
        


    @commands.command(name="Unhide", description="Unhide Channels For mentioned Role", usage="[channel] [role]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376)
    async def unhide(self, ctx, channel: discord.TextChannel = None, role: discord.Role = None):
        channel = channel if channel else ctx.channel
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Visibal for for {role.name}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Sync", description="Sync Channels permissions", usage="[channel]")
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def sync(self, ctx, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        await channel.edit(sync_permissions=True)
        await ctx.send("permissions are Synced", delete_after=15)



def setup(bot):
    bot.add_cog(txt_manage(bot))


"""
@commands.command(name="lockdown", description="Put Server in lockdown", usage="")
    @commands.has_permissions(ban_members=True)
    async def lockdown(self, ctx, *,reason=None):
        role = ctx.guild.default_role
        permissions = discord.PermissionOverwrite()
        PermissionOverwrite.update(send_messages = False)

        await role.edit(reason=reason, permissions=permissions)
        await ctx.send("Server LOck")

    @commands.command(name="server_unlock", description="Unlock Server from lockdown", usage="")
    @commands.has_permissions(ban_members=True)
    async def server_unlock(self, ctx, *,reason= None):
        role = ctx.guild.default_role
        permissions = discord.PermissionOverwrite()
        PermissionOverwrite.update(send_messages = True)

        await role.edit(reason=reason, permissions=permissions)

        await ctx.send("Server UnLock")
"""