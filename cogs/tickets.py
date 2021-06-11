import asyncio
import chat_exporter
import datetime
import discord
import io
import json
import random
#----------------------
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from bson.objectid import ObjectId
from copy import deepcopy
from discord import message
from discord import channel
from discord.ext import commands
from typing import Union

from discord.ext.commands.converter import CategoryChannelConverter

description = "Ticket System For the Server Support"

class tickets(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot
        self.setup = self.bot.ticket_setup.get_all()

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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        data = deepcopy(self.bot.ticket_setups)
        setups = json.dumps(data)
        setup = json.loads(setups)

        ticket_filter = {"guild_id": payload.guild_id}
        ticket = await self.bot.config.find(ticket_filter)

        echannel = self.bot.get_channel(payload.channel_id)
        message = await echannel.fetch_message(payload.message_id)
        member =  self.bot.get_user(payload.user_id)
        try:
            guild = self.bot.get_guild(setup["_id"])
        except KeyError:
            return 

        if message.id == setup["message_id"]:

            if member.id in self.bot.blacklist_user:
                try:
                    await member.send("Your Blacklist form bot and it's Ticket System")
                    return await message.remove_reaction(payload.emoji, member)
                except discord.HTTPException:
                    await echannel.send(f"Your {member.mention} Blacklist form bot and it's Ticket System", delete_after=15)
                    return await message.remove_reaction(payload.emoji, member)


            ticket_check = {'user_id': member.id}
            check = await self.bot.ticket.find_many_by_custom(ticket_check)

            if bool(check):
                await echannel.send(f"Your {member.mention} have Reach the max number of the tickets", delete_after=15)
                return await message.remove_reaction(payload.emoji, member)


            if payload.emoji.name == setup["emoji_1"]:

                channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{member.display_name} Ticket", topic=f"User Id: {member.id}")
                overwrite = channel.overwrites_for(member)
                overwrite.send_messages = True
                overwrite.view_channel = True

                embed = discord.Embed(title=f"Hi {member.display_name}, Welcome to Server Support",
                    color=0x008000,
                    description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
                embed.set_footer(text="Developed and Owned by Jay & utki007")

                ticket_filter = {"user_id": member.id, "guild_id": guild.id,}
                ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}
                await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

                await channel.edit(name=f"{member.display_name} Ticket")
                await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

                await channel.send(f"{member.mention}", embed=embed)

                await message.remove_reaction(payload.emoji, member)

                return

            if payload.emoji.name == setup["emoji_2"]:
                

                channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{member.display_name} Ticket-Partnership", topic=f"User Id: {member.id}")
                overwrite = channel.overwrites_for(member)
                overwrite.send_messages = True
                overwrite.view_channel = True
                prole = discord.utils.get(guild.roles, id=831405039830564875)

                embed = discord.Embed(title=f"Hi {member.display_name}, Welcome to Server Support",
                    color=0x008000,
                    description="Kindly wait patiently. A staff member/ partnership Manager will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
                embed.set_footer(text="Developed and Owned by Jay & utki007")

                ticket_filter = {"user_id": member.id, "guild_id": guild.id,}
                ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}
                await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

                await channel.edit(name=f"{member.display_name} Partnership Ticket")
                poverwrite = channel.overwrites_for(prole)
                poverwrite.send_messages = True
                poverwrite.view_channel = True

                await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)
                await channel.set_permissions(prole, overwrite=poverwrite)

                await channel.send(f"{member.mention}\n{prole.mention}", embed=embed)

                await message.remove_reaction(payload.emoji, member)

                return

        else:
            return
        
    @commands.command(name="setup", description="Start Server Ticket System Setup")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def setup(self, ctx, channel: discord.TextChannel, emoji1: discord.Emoji, emoji2: discord.Emoji):

        #ticket_setup = {" _id": ctx.guild.id}
        setup = await self.bot.ticket_setup.find(ctx.guild.id)
        if not bool(setup):
            embed = discord.Embed(title="SERVER SUPPORT",
                description="Get in touch with TGK Staff Team by reacting below.\nMake sure you react with the right emoji, to get apt support.\n\n<:support:837272254307106849> **Queries and Complaints**\n<:partner:837272392472330250> **Partnership**\n\nPlease Note that only 1 Active Ticket is allowed per member.\nTo raise a New Ticket, ensure that your previous ticket is Closed and Deleted.\n\nMisuse of the service will lead to Blacklisting of the Member from the Service.",
                color=0x2ECC71)
            message = await channel.send(embed=embed)
            await message.add_reaction(emoji1)
            await message.add_reaction(emoji2)

            ticket_filter = {"_id": ctx.guild.id, "channel_id": channel.id}
            ticket_data = { "message_id": message.id, "emoji_1": emoji1.name, "emoji_2": emoji2.name}

            await self.bot.ticket_setup.upsert_custom(ticket_data, ticket_filter)

            await ctx.send("Your Tickets System is Done")
            datas = await self.bot.ticket_setup.get_all()
            for data in datas:
                setup = json.dumps(data)
                self.bot.ticket_setups = json.loads(setup)


        else:

            await ctx.send("your ticket system is alredy Done")
            channel = self.bot.get_channel(setup["channel_id"])
            emoji1 = setup["emoji_1"]
            emoji2 = setup["emoji_2"]
            emoji1 = await commands.EmojiConverter().convert(ctx, emoji1)
            emoji2 = await commands.EmojiConverter().convert(ctx, emoji2)
            message = await channel.fetch_message(setup["message_id"])
            embed = discord.Embed(title="Tickets System Info",
                description=f"Support channel : {channel.mention}\n\
                Support message: [here]({message.jump_url})\n\
                Emojis: 1. {emoji1} 2. {emoji2}")
            await ctx.send(embed=embed)
            delete = await ctx.send("You Want to delete the Old Setup? if yes Type yes your have 10s")
            try:
                await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.startswith("Y") or m.content.startswith("y"), timeout=10)
                channel = self.bot.get_channel(setup["channel_id"])
                message = await channel.fetch_message(setup["message_id"])
                await self.bot.ticket_setup.delete(ctx.guild.id)
                await message.delete()
                await  ctx.send("Your Old Setup Deleted also your support message also")
                datas = await self.bot.ticket_setup.get_all()
                for data in datas:
                    setup = json.dumps(data)
                    self.bot.ticket_setups = json.loads(setup)
            except asyncio.TimeoutError:
                await delete.edit(content="Time Out")



    @commands.command(name="new", hidden=True)
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def new(self, ctx, member: discord.Member=None):
        member = member if member else ctx.author
        guild = self.bot.get_guild(785839283847954433)
        channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{member.display_name} Ticket", topic=f"User Id: {member.id}")
        overwrite = channel.overwrites_for(member)
        overwrite.send_messages = True
        overwrite.view_channel = True

        embed = discord.Embed(title=f"Hi {member.display_name}, Welcome to Server Support",
            color=0x008000,
            description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")

        ticket_filter = {"user_id": member.id, "guild_id": guild.id,}
        ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}
        await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

        await channel.edit(name=f"{member.display_name} Ticket")
        await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

        await channel.send(f"{member.mention}", embed=embed)
        await ctx.message.delete()

    @commands.command(name="pnew", hidden=True)
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def pnew(self, ctx, member: discord.Member=None):
        member = member if member else ctx.author
        guild = self.bot.get_guild(785839283847954433)
        channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{member.display_name} Ticket-Partnership", topic=f"User Id: {member.id}")
        overwrite = channel.overwrites_for(member)
        overwrite.send_messages = True
        overwrite.view_channel = True
        prole = discord.utils.get(guild.roles, id=831405039830564875)

        embed = discord.Embed(title=f"Hi {member.display_name}, Welcome to Server Support",
            color=0x008000,
            description="Kindly wait patiently. A staff member/ partnership Manager will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")

        ticket_filter = {"user_id": member.id, "guild_id": guild.id,}
        ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}
        await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

        await channel.edit(name=f"{member.display_name} Partnership Ticket")
        poverwrite = channel.overwrites_for(prole)
        poverwrite.send_messages = True
        poverwrite.view_channel = True

        await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        await channel.set_permissions(prole, overwrite=poverwrite)

        await channel.send(f"{member.mention}", embed=embed)
        await ctx.message.delete()

    @commands.command(name="close", description="close The ticket", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def close(self, ctx):
        if ctx.channel.category.id == 829230513516445736:
            await ctx.message.delete()
            if ctx.channel.permissions_synced:
                await ctx.send("ticket Is Closed already")
            else:
                await ctx.channel.edit(sync_permissions=True)
                embed = discord.Embed(description=f"Ticket Closed By {ctx.author.mention}")
                await ctx.send(embed=embed)
        else:
            await ctx.send("You can't use this command here")

    @commands.command(name="open", description="Reopens current ticket", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def open(self, ctx):
        if ctx.channel.permissions_synced==False:
            return await ctx.send("Ticket already Opned")
        else:

            ticket_filter = {"ticket_id": ctx.channel.id}
            tickets = await self.bot.ticket.find_many_by_custom(ticket_filter)

            if not bool(tickets):
                return await ctx.send(f"Couldn't find any Close Tickets")

            for ticket in tickets:
                member = ctx.guild.get_member(ticket['user_id'])

            if not member:
                return await ctx.send("user Not Found maybe he has Left server you may delete ticket by >delete")

            await ctx.channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

            embed = discord.Embed(color=0x02ff06, description=f"ticket open by {ctx.author.mention}")

            await ctx.send(embed=embed)
            await ctx.message.delete()
           


    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def transcript(self, ctx, limit: int=None, *,ticket=None):

        ticket = ticket if ticket else "Topic Not Given"
        message = await ctx.send("Saving Started")

        limit = limit if limit else 500
        tz_info = "Asia/Kolkata"

        channel =  self.bot.get_channel(833386438338674718)
        transcript = await chat_exporter.export(ctx.channel, limit, tz_info)

        if transcript is None:
            return

        transcript_file = discord.File(io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")

        await channel.send(f"{ctx.channel.name} / {ticket}", file=transcript_file)
        await message.edit(content=f"{ctx.author.mention} transcript Saved")
        await ctx.send(file=transcript_file)

        
    @commands.command(name="delete", description="delete the ticket", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def delete(self, ctx):
        channel = ctx.channel
        buttons = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        cancel = [
            [
                Button(style=ButtonStyle.red, label="Focre Stop")
            ]
        ]
        start_embed = discord.Embed(description=f"Are you Sure want to delete this ticket")
        no_embed = discord.Embed(description="Alright whatever just come hit me up when you wanna delete the ticket")
        cancel_embed = discord.Embed(description=f"Canceling the command Reason: TimeoutError or Focre Stop by Admin")
        delete_embed = discord.Embed(description=f"Deleting This Ticket Now you have 10s to cancel it by taping on below buttons")
        m = await ctx.send(embed=start_embed, components=buttons, content=ctx.author.mention)
        try:
            res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=30)

            if res.component.label.lower() == "yes":

                await m.edit(components = [])
                await m.delete()
                m = await ctx.send(embed=delete_embed, components = cancel)
                try:
                    res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=10)
                    await m.edit(embed=cancel_embed, components = [])
                except asyncio.TimeoutError:
                    ticket_filter = {"ticket_id": channel.id}
                    await self.bot.ticket.delete_by_custom(ticket_filter)
                    await m.edit(components = [])
                    await asyncio.sleep(0.5)
                    await channel.delete()
            if res.component.label.lower() == "no":
                return await m.edit(embed=no_embed, components= [])
        except asyncio.TimeoutError:
            print("TimeoutError")
            await m.edit(embed=cancel_embed, components = [])

    @commands.command(name="Claim", description="Claim Tickets to provide Support", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def Claim(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        if ctx.channel.category.id == 829230513516445736:

            mod_role = discord.utils.get(guild.roles, id=785845265118265376)
            jr_mod = discord.utils.get(guild.roles, id=787259553225637889)
            partner = discord.utils.get(guild.roles, id=831405039830564875)


            await ctx.channel.set_permissions(ctx.author, send_messages=True, view_channel=True, attach_files=True, embed_links=True)
            await ctx.channel.set_permissions(mod_role, send_messages=False, view_channel=True)
            await ctx.channel.set_permissions(jr_mod, send_messages=False, view_channel=True)
            await ctx.channel.set_permissions(partner, send_messages=False, view_channel=True)

            embed = discord.Embed(description=f"This ticket will now be handled by {ctx.author.mention}")
            await ctx.send(embed=embed)

    @commands.command(name="unClaim", description="UnClaim Tickets", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def unClaim(self, ctx):
        guild = ctx.guild
        await ctx.message.delete()
        if ctx.channel.category.id == 829230513516445736:
            
            admin_role = discord.utils.get(guild.roles, id=799037944735727636)
            mod_role = discord.utils.get(guild.roles, id=785845265118265376)
            jr_mod = discord.utils.get(guild.roles, id=787259553225637889)
            partner = discord.utils.get(guild.roles, id=831405039830564875)


            await ctx.channel.set_permissions(ctx.author, send_messages=None, view_channel=None, attach_files=None, embed_links=None)
            await ctx.channel.set_permissions(mod_role, send_messages=None, view_channel=True)
            await ctx.channel.set_permissions(jr_mod, send_messages=None, view_channel=True)
            await ctx.channel.set_permissions(partner, send_messages=None, view_channel=True)

            embed = discord.Embed(description=f"This Ticket is now UnClaimed")
            await ctx.send(embed=embed)

    @commands.command(name="add", description="add User to the channel", usage="[member]")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def add(self, ctx, *, target: Union[discord.Member, discord.Role]):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            overwrite = channel.overwrites_for(target)
            overwrite.view_channel = True
            overwrite.send_messages = True

            await channel.set_permissions(target, overwrite=overwrite)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Added {target.mention} to the Tick")

            await ctx.send(embed=embed)



    @commands.command(name="remove", description="Remove User to the channel", usage="[member]")
    @commands.check_any(commands.has_any_role(831405039830564875),perm_check(), is_me())
    async def remove(self, ctx, *, target: Union[discord.Member, discord.Role]):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            overwrite = channel.overwrites_for(target)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(target, overwrite=overwrite)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed {target.mention} to the Tick")

            await ctx.send(embed=embed)

    @commands.command(name="dtest", description="new delete command")
    @commands.check_any(perm_check(), is_me())
    async def dtest(self, ctx):
        channel = ctx.channel
        buttons = [
            [
                Button(style=ButtonStyle.green, label="Yes"),
                Button(style=ButtonStyle.red, label="No")
            ]
        ]
        cancel = [
            [
                Button(style=ButtonStyle.red, label="Focre Stop")
            ]
        ]
        start_embed = discord.Embed(description=f"Are you Sure want to delete this ticket")
        no_embed = discord.Embed(description="Alright whatever just come hit me up when you wanna delete the ticket")
        cancel_embed = discord.Embed(description=f"Canceling the command Reason: TimeoutError or Focre Stop by Admin")
        delete_embed = discord.Embed(description=f"Deleting This Ticket Now you have 10s to cancel it by taping on below buttons")
        m = await ctx.send(embed=start_embed, components=buttons, content=ctx.author.mention)
        try:
            res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=30)

            if res.component.label.lower() == "yes":

                await m.edit(components = [])
                m = await ctx.send(embed=delete_embed, components = cancel)
                try:
                    res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=10)
                    await m.delete()
                    await m.edit(embed=cancel_embed, components = [])
                except asyncio.TimeoutError:
                    ticket_filter = {"ticket_id": channel.id}
                    await self.bot.ticket.delete_by_custom(ticket_filter)
                    await m.edit(components = [])
                    await asyncio.sleep(0.5)
                    await channel.delete()
            if res.component.label.lower() == "no":
                return await m.edit(embed=no_embed, components= [])
        except asyncio.TimeoutError:
            print("TimeoutError")
            await m.edit(embed=cancel_embed, components = [])


def setup(bot):
    bot.add_cog(tickets(bot))
