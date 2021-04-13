import random

import discord
from discord.ext import commands
from discord.ext.buttons import Paginator

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
    @commands.has_permissions(manage_messages=True)
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

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def new(self, ctx):
        await ctx.send("Invalid sub-command passed.")

    @new.command(
        name="category",
        description="Create a new category",
        usage="<role> <Category name>",
    )
    async def category(self, ctx, role: discord.Role, *, name):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        category = await ctx.guild.create_category(name=name, overwrites=overwrites)
        await ctx.send(f"Hey dude, I made {category.name} for ya!")

    @new.command(
        name="channel",
        description="Create a new channel",
        usage="<role> <channel name>",
    )
    async def channel(self, ctx, role: discord.Role, *, name):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await ctx.guild.create_text_channel(
            name=name,
            overwrites=overwrites,
            category=self.bot.get_channel(707945693582590005),
        )
        await ctx.send(f"Hey dude, I made {channel.name} for ya!")

    @commands.group(name="category", description="Delete a category/channel", usage="help", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx):
        await ctx.send("Invalid sub-command passed")

    @delete.command(
        name="category", description="Delete a category", usage="delete <category> [reason]"
    )
    @our_custom_check()
    async def _category(self, ctx, category: discord.CategoryChannel, *, reason=None):
        await category.delete(reason=reason)
        await ctx.send(f"hey! I deleted {category.name} for you")

    @delete.command(
        name="channel", description="Delete a channel", usage="delete <channel> [reason]"
    )
    @our_custom_check()
    async def _channel(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        channel = channel or ctx.channel
        await channel.delete(reason=reason)
        await ctx.send(f"hey! I deleted {category.name} for you")


    @commands.command(name="lock", description="Lock the given channel For mentioned Role", usage="[channel] [Role]",)
    @commands.has_permissions(manage_messages=True)
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

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
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


    @commands.command(name="Hide", description="Hide Channels For mentioned Role", usage="[channel] [role]")
    @commands.has_permissions(ban_members=True)
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
    @commands.has_permissions(ban_members=True)
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

    #tickets Fixes 

    @commands.command(name="adduser", description="add User to the channel", usage="[member] [channel]")
    @commands.has_permissions(manage_messages=True)
    async def adduser(self, ctx, member: discord.User=None, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        if member == ctx.author:
            await ctx.send("you use command on your self")

        overwrite = channel.overwrites_for(member)
        overwrite.view_channel = True
        overwrite.send_messages = True

        await channel.set_permissions(member, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06,
            description=f"The User {member.mention} Is added to the Channel"
            )
        await ctx.send(embed=embed)


    @commands.command(name="removeuser", description="Remove User to the channel", usage="[member] [channel]")
    @commands.has_permissions(manage_messages=True)
    async def removeuser(self, ctx, member:discord.Member, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        if member == ctx.author:
            await ctx.send("you use command on your self")

        overwrite = channel.overwrites_for(member)
        overwrite.view_channel = False
        overwrite.send_messages = False

        await channel.set_permissions(member, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06,
            description=f"The User {member.mention} Is Remove from the Channel"
            )
        await ctx.send(embed=embed)

    @commands.command(name="addrole", description="add User to the channel", usage="[member] [channel]")
    @commands.has_permissions(manage_messages=True)
    async def addrole(self, ctx, role: discord.Role, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        if role == None or ctx.guild.default_role:
            await ctx.send("you need to enter role mention/id or u can't add this role")

        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        overwrite.send_messages = True

        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06,
            description=f"The Role {role.mention} Is added to the Channel"
            )
        await ctx.send(embed=embed)

    @commands.command(name="removerole", description="Remove User to the channel", usage="[Role.id/mention] [channel]", aliases=["removr"])
    @commands.has_permissions(manage_messages=True)
    async def removerole(self, ctx, role:discord.Role, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        if role == None:
            await ctx.send("you need to enter role mention/id")

        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        overwrite.send_messages = False

        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x02ff06,
            description=f"The Role {role.mention} Is Remove from the Channel"
            )
        await ctx.send(embed=embed)

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