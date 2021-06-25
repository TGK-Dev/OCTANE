import asyncio
import discord
import random
import re

from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from humanfriendly import format_timespan

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description="Channel Management Commands"

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
            return ctx.message.author.id in [488614633670967307 , 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916]
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
    async def lock(self, ctx, *,role: discord.Role = None):

        channel = ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x2f3136 , description=f'<:allow:819194696874197004> | Locked {channel.mention} for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="unlock", description="Unlock the given channel For mentioned Role", usage="[Role]", aliases=['ul'])
    @commands.check_any(perm_check(), is_me())
    async def unlock(self, ctx, *,role: discord.Role = None):

        channel = ctx.channel
        role = role if role else ctx.guild.default_role

        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None

        await ctx.message.delete()
        await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(color=0x2f3136 , description=f'<:allow:819194696874197004> | Unlocked {channel.mention} for {role.mention}')
        await channel.send(embed=embed)

    @commands.command(name="slowmode", description="Set Slowmode In Current Channel", usage="[slowmode time 1m, 1s 1h max 6h]", aliases=['sm'])
    @commands.check_any(perm_check(), is_me())
    async def slowmode(self, ctx, time:TimeConverter=None):
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
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
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
        role = role if role else discord.utils.get(ctx.guild.roles, name="࿐ NEWBIE 〢 0")
        overwrite = channel.overwrites_for(role)
        overwrite.view_channel = True
        await channel.set_permissions(role, overwrite=overwrite)
        await ctx.message.delete()

        embed = discord.Embed(
            color=0x02ff06, description=f'The {channel.name} is Now Visibal for for {role.name}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="Sync", description="Sync Channels permissions to it's Category", usage="[channel]")
    @commands.check_any(perm_check(), is_me())
    async def sync(self, ctx, channel: discord.TextChannel=None):
        channel = channel if channel else ctx.channel

        await channel.edit(sync_permissions=True)
        await ctx.send("permissions are Synced", delete_after=15)

    @commands.group(name="lockdown", description="Put server in Lock",invoke_without_command=True)
    @commands.check_any(perm_check(), is_me())
    async def lockdown(self, ctx):
        conform = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        m = await ctx.send("Are you Sure Want to lock Server", components=conform)

        try:
            res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=30)
            await res.respond(type=6)
            if res.component.label.lower() == "no":
                no_embed = discord.Embed(title="Server Lockdown", description="You are **not muted tbh**.  The server is currently under maintenance. We regret the inconvenience caused. <:so_sad:810172533692694538>", color=0xE74C3C)
                return await m.edit(embed=no_embed, components = [], content=None)
            if res.component.label.lower() == "yes":
                channels = await self.bot.config.find(ctx.guild.id)
                role = ctx.guild.default_role

                for channel in channels["lockdown_channels"]:
                    channel = self.bot.get_channel(channel)
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = False
                    await channel.set_permissions(role, overwrite=overwrite)
                    embed = discord.Embed(title="Server Lockdown", description="You are **not muted tbh**.  The server is currently under maintenance. We regret the inconvenience caused. <:so_sad:810172533692694538>", color=0xE74C3C)
                    await channel.send(embed=embed)
                await m.edit(embed=embed, components = [])
        except asyncio.TimeoutError:
            await ctx.send("TimeoutError canceling the command")



    @lockdown.command(name="add", description="add channel to the lockdown list")
    @commands.check_any(perm_check(), is_me())
    async def add(self, ctx, channel:discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Your Server config is not done yet please use config command")
        data["lockdown_channels"].append(channel.id)
        lsit_embed = discord.Embed(description=f"you want to add the {channel.name} to list")
        conform = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        m = await ctx.send(embed=lsit_embed, components=conform)
        try:
            res = await self.bot.wait_for("button_click", check=lambda res: res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=60)
            await res.respond(type=6)
            if res.component.label.lower() == "yes":
                await self.bot.config.upsert(data)
                config = discord.Embed(description="list updated")
                return await m.edit(embed=config, components=[])
            if res.component.label.lower() == "no":
                config = discord.Embed(description="Commands canceling")
                return await m.edit(components = [], embed=config)
        except asyncio.TimeoutError:
            config = discord.Embed(description="Commands canceling")
            await m.edit(components = [], embed=config)

    @lockdown.command(name="remove", description="remove channel form lockdown list")
    @commands.check_any(perm_check(), is_me())
    async def remove(self, ctx, channel:discord.TextChannel):
        data = await self.bot.config.find(ctx.guild.id)
        if data is None:
            return await ctx.send("Your Server config is not done yet please use config command")
        data["lockdown_channels"].remove(channel.id)

        lsit_embed = discord.Embed(description=f"you want to remove the {channel.name} form list")
        conform = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        m = await ctx.send(embed=lsit_embed, components=conform)
        try:
            res = await self.bot.wait_for("button_click", check=lambda res: res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=60)
            await res.respond(type=6)
            if res.component.label.lower() == "yes":
                await self.bot.config.upsert(data)
                config = discord.Embed(description="list updated")
                return await m.edit(embed=config, components=[])
            if res.component.label.lower() == "no":
                config = discord.Embed(description="Commands canceling")
                return await m.edit(components = [], embed=config)
        except asyncio.TimeoutError:
            config = discord.Embed(description="Commands canceling")
            await m.edit(components = [], embed=config)


    @lockdown.command(name="list", description="list of lockdown channels list")
    @commands.check_any(perm_check(), is_me())
    async def list(self, ctx):
        channels = await self.bot.config.find(ctx.guild.id)
        if channels['lockdown_channels'] is None:
            return await ctx.send("No channels has Added Yet")
        embed = discord.Embed(title="Lockdown Channels List", description="", color=0x9B59B6)
        try:
            i = 1
            for channel in channels['lockdown_channels']:
                channel = self.bot.get_channel(channel)
                embed.description += f"{i}.{channel.mention}\n"
                i += 1
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("There are no channel in the list")
        

    @lockdown.command(name="end", description="End Server Lockdown")
    @commands.check_any(perm_check(), is_me())
    async def end(self, ctx):
        conform = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        m = await ctx.send("Are you Sure Want to Unlock Server", components=conform)

        try:
            res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=30)
            await res.respond(type=6)
            if res.component.label.lower() == "no":
                embed = discord.Embed(description="Let me know when you want to unlock the Server")
                return await m.edit(embed=embed, components= [])
            if res.component.label.lower() == "yes":
                channels = await self.bot.config.find(ctx.guild.id)
                role = ctx.guild.default_role

                for channel in channels["lockdown_channels"]:
                    channel = self.bot.get_channel(channel)
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = None
                    await channel.set_permissions(role, overwrite=overwrite)
                    embed = discord.Embed(title="Server UnLockdown", description="Server is now unlock", color=0x2ECC71)
                    await channel.send(embed=embed)
                await m.edit(embed=embed, components = [])
        except asyncio.TimeoutError:
            await ctx.send("TimeoutError canceling the command")

def setup(bot):
    bot.add_cog(channel(bot))