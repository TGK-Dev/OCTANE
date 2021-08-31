import asyncio
import chat_exporter
import datetime
import discord
import io
import json
import random


from copy import deepcopy
from discord import message
from discord import channel
from discord.ext import commands
from typing import Union

from discord.ext.commands.converter import CategoryChannelConverter
from discord.ext.commands.core import command

description = "Ticket System For the Server Support"


class PersistentView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label='PartnerShip', style=discord.ButtonStyle.green, custom_id='persistent_view:partner_ship', emoji="<:partner:837272392472330250>")
    async def partnerShip(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        data = await self.bot.ticket.find(user.id)
        if data == None:
            data = await self.bot.config.find(guild.id)

            if data == None:
                return await interaction.response.send_message("guild ticket setup is not Done Yet")

            channel = await guild.create_text_channel(category=self.bot.get_channel(data['t_category']), name=f"{user.name} Partnership Ticket", topic=f"User Id: {user.id}")
            await channel.edit(sync_permissions=True)
            overwrite = channel.overwrites_for(user)
            overwrite.send_messages = True
            overwrite.read_messages = True
            overwrite.read_message_history = True
            overwrite.attach_files = True
            overwrite.view_channel = True
            await channel.set_permissions(user, overwrite=overwrite)

            embed = discord.Embed(title=f"Hi {user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
            embed.set_footer(text="Developed and Owned by Jay & utki007")
            await channel.send(f"{user.mention}", embed=embed)

            await interaction.response.send_message(f"{user.mention} Your Tickets Has been open at {channel.mention}", ephemeral=True)
            user_data = {'_id': user.id,
                         'guild': user.guild.id,
                         'channel': channel.id}
            await self.bot.ticket.upsert(user_data)
        else:
            channel = self.bot.get_channel(data['channel'])
            return await interaction.response.send_message(f"{user.mention}You alredy have an ticket {channel.mention}", ephemeral=True)
            data = await self.bot.config.find(guild.id)

    @discord.ui.button(label='Support', style=discord.ButtonStyle.red, custom_id='persistent_view:red', emoji="<:support:837272254307106849>")
    async def support(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        data = await self.bot.ticket.find(user.id)

        if data == None:
            data = await self.bot.config.find(guild.id)

            if data == None:
                return await interaction.response.send_message("guild ticket setup is not Done Yet")

            channel = await guild.create_text_channel(category=self.bot.get_channel(data['t_category']), name=f"{user.name} Support Ticket", topic=f"User Id: {user.id}")
            await channel.edit(sync_permissions=True)
            overwrite = channel.overwrites_for(user)
            overwrite.send_messages = True
            overwrite.read_messages = True
            overwrite.read_message_history = True
            overwrite.attach_files = True
            overwrite.view_channel = True
            await channel.set_permissions(user, overwrite=overwrite)

            embed = discord.Embed(title=f"Hi {user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
            embed.set_footer(text="Developed and Owned by Jay & utki007")
            await channel.send(f"{user.mention}", embed=embed)

            await interaction.response.send_message(f"{user.mention} Your Tickets Has been open at {channel.mention}", ephemeral=True)
            user_data = {'_id': user.id,
                         'guild': user.guild.id,
                         'channel': channel.id}
            await self.bot.ticket.upsert(user_data)
        else:
            channel = self.bot.get_channel(data['channel'])
            return await interaction.response.send_message(f"{user.mention}You alredy have an ticket {channel.mention}", ephemeral=True)


class tickets(commands.Cog, description=description):
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
        self.bot.add_view(PersistentView(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="new", hidden=True)
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def new(self, ctx, member: discord.Member = None):
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

        ticket_filter = {"user_id": member.id, "guild_id": guild.id, }
        ticket_data = {"ticket_id": channel.id,
                       "timestamp": datetime.datetime.now()}
        await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

        await channel.edit(name=f"{member.display_name} Ticket")
        await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

        await channel.send(f"{member.mention}", embed=embed)
        await ctx.message.delete()

    @commands.command(name="pnew", hidden=True)
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def pnew(self, ctx, member: discord.Member = None):
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

        ticket_filter = {"user_id": member.id, "guild_id": guild.id, }
        ticket_data = {"ticket_id": channel.id,
                       "timestamp": datetime.datetime.now()}
        await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

        await channel.edit(name=f"{member.display_name} Partnership Ticket")
        poverwrite = channel.overwrites_for(prole)
        poverwrite.send_messages = True
        poverwrite.view_channel = True

        await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)
        await channel.set_permissions(prole, overwrite=poverwrite)

        await channel.send(f"{member.mention}\n{prole.mention}", embed=embed)
        await ctx.message.delete()

    @commands.command(name="close", description="close The ticket", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def close(self, ctx):
        if ctx.channel.category.id == 829230513516445736:
            await ctx.message.delete()
            if ctx.channel.permissions_synced:
                await ctx.send("ticket Is Closed already")
            else:
                await ctx.channel.edit(sync_permissions=True)
                embed = discord.Embed(
                    color=0x2f3136, description=f"Ticket Closed By {ctx.author.mention}")
                await ctx.send(embed=embed)
        else:
            await ctx.send("You can't use this command here")

    @commands.command(name="open", description="Reopens current ticket", usage="")
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def open(self, ctx):
        if ctx.channel.permissions_synced == False:
            await ctx.message.delete()
            return await ctx.send("Ticket already Opned")
        else:

            ticket_filter = {"channel": ctx.channel.id, 'guild': ctx.guild.id}
            ticket = await self.bot.ticket.find_by_custom(ticket_filter)
            #prole = discord.utils.get(guild.roles, id=831405039830564875)

            if not bool(ticket):
                return await ctx.send(f"Couldn't find any Close Tickets")

            member = ctx.guild.get_member(ticket['_id'])

            if not member:
                return await ctx.send("user Not Found maybe he has Left server you may delete ticket by >delete")

            await ctx.channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

            embed = discord.Embed(
                color=0x2f3136, description=f"ticket open by {ctx.author.mention}")

            await ctx.message.delete()
            await ctx.send(content=f"{member.mention}", embed=embed)

    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def transcript(self, ctx, limit: int = None, *, ticket=None):

        ticket = ticket if ticket else "Topic Not Given"
        message = await ctx.send("Saving Started")

        limit = limit if limit else 500
        tz_info = "Asia/Kolkata"

        channel = self.bot.get_channel(833386438338674718)
        transcript = await chat_exporter.export(ctx.channel, limit, tz_info)

        if transcript is None:
            return

        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                       filename=f"transcript-{ctx.channel.name}.html")

        await channel.send(f"{ctx.channel.name} / {ticket}", file=transcript_file)
        await message.edit(content=f"{ctx.author.mention} transcript Saved")
        channel_file = discord.File(io.BytesIO(transcript.encode()),
                                    filename=f"transcript-{ctx.channel.name}.html")
        await ctx.send(f"{ctx.channel.name} / {ticket}", file=channel_file)

    @commands.command(name="delete", description="delete the ticekt")
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def delete(self, ctx):
        data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id})
        if data is None:
            return await ctx.send("Maybe this is not an ticket")
        msg = await ctx.send("Deleting this Ticekt in 10s `type fs` to cancel this command")
        try:
            await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == "fs", timeout=10)
            await msg.edit(content="Ok cancelling the command")
        except asyncio.TimeoutError:
            await ctx.channel.delete()

    @commands.command(name="add", description="add User to the channel", usage="[member]")
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def add(self, ctx, *, target: Union[discord.Member, discord.Role]):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            overwrite = channel.overwrites_for(target)
            overwrite.view_channel = True
            overwrite.send_messages = True

            await channel.set_permissions(target, overwrite=overwrite)
            embed = discord.Embed(
                description=f"<:allow:819194696874197004> | Added {target.mention} to the Ticket")

            await ctx.send(embed=embed)

    @commands.command(name="remove", description="Remove User to the channel", usage="[member]")
    @commands.check_any(commands.has_any_role(831405039830564875), perm_check(), is_me())
    async def remove(self, ctx, *, target: Union[discord.Member, discord.Role]):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            overwrite = channel.overwrites_for(target)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(target, overwrite=overwrite)
            embed = discord.Embed(
                description=f"<:allow:819194696874197004> | Removed {target.mention} to the Tick")

            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.check_any(is_me())
    async def invite(self, ctx, invite: discord.Invite):
        await ctx.send(f"invite: {invite}\nInvite Server ID: {invite.guild.id}")


def setup(bot):
    bot.add_cog(tickets(bot))
