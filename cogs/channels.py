import asyncio
import discord
import random
import re
import datetime

from discord.ext import commands
from discord.ui import view

from humanfriendly import format_timespan

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Channel Management Commands"


class Confirm(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.value = False
        self.ctx = ctx

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("it's not your Buttons", ephemeral=True)
        else:
            return True


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


class channel(commands.Cog, description=description):
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

    @commands.command(name="lock", description="Lock the given channel For mentioned Role", usage="[Role]", aliases=['l'])
    @commands.check_any(perm_check(), is_me())
    async def lock(self, ctx, *, role: discord.Role = None):

        channel = ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x2f3136, description=f'<:allow:819194696874197004> | Locked {channel.mention} for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="unlock", description="Unlock the given channel For mentioned Role", usage="[Role]", aliases=['ul'])
    @commands.check_any(perm_check(), is_me())
    async def unlock(self, ctx, *, role: discord.Role = None):

        channel = ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(
            color=0x2f3136, description=f'<:allow:819194696874197004> | Unlocked {channel.mention} for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
    @commands.check_any(perm_check(), is_me())
    async def slowmode(self, ctx, time: TimeConverter = None):
        await ctx.message.delete()
        channel = ctx.channel

        if time is None or time == 0:
            time = 0
            await ctx.channel.edit(slowmode_delay=time)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed slowmode from {channel.mention}",
                                  color=0x2f3136)
            return await ctx.send(embed=embed)

        if time >= 21600:
            return await ctx.send(f"Slowmode interval can't be greater than 6 hours.", delete_after=30)

        await ctx.channel.edit(slowmode_delay=time)

        embed = discord.Embed(description=f"<:allow:819194696874197004> | Set {channel.mention} slowmode to {format_timespan(time)}",
                              color=0x2f3136)
        await ctx.send(embed=embed)

    @commands.command(name="Hide", description="Hide Channels For mentioned Role", usage="[role]")
    @commands.check_any(perm_check(), is_me())
    async def hide(self, ctx, role: discord.Role = None):
        channel = ctx.channel
        role = role if role else discord.utils.get(
            ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = False
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.mention} is now hidden for{role.mention}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Unhide", description="Unhide Channels For mentioned Role", usage="[role]")
    @commands.check_any(perm_check(), is_me())
    async def unhide(self, ctx, role: discord.Role = None):
        channel = ctx.channel
        role = role if role else discord.utils.get(
            ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Visibal for for {role.name}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Sync", description="Sync Channels permissions to it's Category", usage="[channel]")
    @commands.check_any(perm_check(), is_me())
    async def sync(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel else ctx.channel

        await channel.edit(sync_permissions=True)
        await ctx.send("permissions are Synced", delete_after=15)

    @commands.group(name="lockdown", description="Put server in Lock", invoke_without_command=True)
    @commands.check_any(perm_check(), is_me())
    async def lockdown(self, ctx):
        msg = await ctx.send("Are you Sure Want to lock Server", view=Confirm(ctx))
        await view.wait()
        if view.value:
            channels = await self.bot.config.find(ctx.guild.id)
            role = ctx.guild.default_role

            for channel in channels["lockdown_channels"]:
                channel = self.bot.get_channel(channel)
                overwrite = channel.overwrites_for(role)
                overwrite.send_messages = False
                await channel.set_permissions(role, overwrite=overwrite)
                embed = discord.Embed(
                    title="Server Lockdown", description="You are **Not Muted**. The server is currently under maintenance. We regret the inconvenience caused. <:so_sad:810172533692694538>", color=0xE74C3C)
                await channel.send(embed=embed)
            await msg.edit(content="Server is now Locked", view=None)

    @lockdown.command(name="add", description="add channel to the lockdown list")
    @commands.check_any(perm_check(), is_me())
    async def add(self, ctx, channel: discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Your Server config is not done yet please use config command")
        data["lockdown_channels"].append(channel.id)
        await self.bot.config.upsert(data)
        config = discord.Embed(description="list updated")
        await ctx.send(embed=config)

    @lockdown.command(name="remove", description="remove channel form lockdown list")
    @commands.check_any(perm_check(), is_me())
    async def remove(self, ctx, channel: discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Your Server config is not done yet please use config command")
        data["lockdown_channels"].remove(channel.id)
        list_embed = discord.Embed(
            description=f"The channel {channel.mention} Has been Removed")
        await self.bot.config.upsert(data)
        await ctx.send(embed=list_embed)

    @lockdown.command(name="list", description="list of lockdown channels list")
    @commands.check_any(perm_check(), is_me())
    async def list(self, ctx):
        channels = await self.bot.config.find(ctx.guild.id)
        if channels['lockdown_channels'] is None or len(channels['lockdown_channnels']) == 0:
            return await ctx.send("No channels has Added Yet")
        embed = discord.Embed(title="Lockdown Channels List",
                              description="", color=0x9B59B6)
        try:
            i = 1
            for channel in channels['lockdown_channels']:
                channel = self.bot.get_channel(channel)
                if channel:
                    embed.description += f"{i}.{channel.mention}\n"
                    i += 1
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("There are no channel in the list")

    @lockdown.command(name="end", description="End Server Lockdown")
    @commands.check_any(perm_check(), is_me())
    async def end(self, ctx):
        msg = await ctx.send("Are you Sure Want to Unlock Server", view=Confirm(ctx))
        await view.wait()
        if view.value:
            channels = await self.bot.config.find(ctx.guild.id)
            role = ctx.guild.default_role

            for channel in channels["lockdown_channels"]:
                channel = self.bot.get_channel(channel)
                overwrite = channel.overwrites_for(role)
                overwrite.send_messages = None
                await channel.set_permissions(role, overwrite=overwrite)
                embed = discord.Embed(
                    title="Server UnLockdown", description="The Server Is Unlocked\nIf any channel is still lock ping any Mod/Admin", color=0x2ECC71)
                await channel.send(embed=embed)
            await msg.edit(content="Server Now Unlocked", embed=None, view=None)
    
    @commands.command(name="Elock", description="lock an event channel")
    @commands.check_any(perm_check(), is_me(), commands.has_any_role(801798369281703936, 868070416722296902,864452953951305758, 882283892722262036))
    async def elock(self, ctx):
        if ctx.channel.category.id != 787366209464565770: return await ctx.send("this comamnd will only works in <#787366209464565770>")
        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        await channel.set_premissions(role, overwrite=overwrite)
        embed = discord.Embed(
            description="Event channel is now Locked"
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="Eunlock", description="lock an event channel")
    @commands.check_any(perm_check(), is_me(), commands.has_any_role(801798369281703936, 868070416722296902,864452953951305758, 882283892722262036))
    async def eunlock(self, ctx):
        if ctx.channel.category.id != 787366209464565770: return await ctx.send("this comamnd will only works in <#787366209464565770>")
        role = ctx.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None
        await channel.set_premissions(role, overwrite=overwrite)
        embed = discord.Embed(
            description="Event channel is now unlocked"
        )
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(channel(bot))
