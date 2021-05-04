import random
import asyncio
import datetime
import discord
import chat_exporter
import io

from typing import Union
from discord.ext import commands
from discord.ext.buttons import Paginator
from bson.objectid import ObjectId

class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        echannel = self.bot.get_channel(payload.channel_id)
        message = await echannel.fetch_message(payload.message_id)
        member =  self.bot.get_user(payload.user_id)
        guild = self.bot.get_guild(785839283847954433)

        if message.id == 837276253408198677:

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


            if payload.emoji.name == "support":

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

            if payload.emoji.name == "partner":


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

    @commands.command(name="new", hidden=True)
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
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
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
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



    @commands.command(name="setup", hidden=True)
    @commands.has_role(785842380565774368)
    async def setup(self, ctx):
        embed = discord.Embed(title="SERVER SUPPORT",
            description="Get in touch with TGK Staff Team by reacting below.\nMake sure you react with the right emoji, to get apt support.\n\n<:support:837272254307106849> **Queries and Complaints**\n<:partner:837272392472330250> **Partnership**\n\nPlease Note that only 1 Active Ticket is allowed per member.\nTo raise a New Ticket, ensure that your previous ticket is Closed and Deleted.\n\nMisuse of the service will lead to Blacklisting of the Member from the Service.",
            color=0x2ECC71)
        message = await ctx.send(embed=embed)
        semoji = self.bot.get_emoji(837272254307106849)
        pemoji = self.bot.get_emoji(837272392472330250)
        await message.add_reaction(semoji)
        await message.add_reaction(pemoji)

    @commands.command(name="close", description="close The ticket", usage="")
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
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def open(self, ctx):
        if ctx.channel.category.id == 829230513516445736:

            ticket_filter = {"ticket_id": ctx.channel.id}

            tickets = await self.bot.ticket.find_many_by_custom(ticket_filter)

            if not bool(tickets):
                return await ctx.send(f"Couldn't find any Close Tickets")

            for ticket in tickets:
                member = ctx.guild.get_member(ticket['user_id'])
                
                await ctx.channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)
                
                embed = discord.Embed(color=0x02ff06, description=f"ticket open by {ctx.author.mention}")

                await ctx.send(embed=embed)
                await ctx.message.delete()
            


    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.has_any_role(785842380565774368,799037944735727636)
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

        
    @commands.command(name="delete", description="delete the ticket", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def delete(self, ctx):
        channel = ctx.channel
        async with ctx.typing():
            if ctx.channel.category.id == 829230513516445736:
                await ctx.send("Are Your sure?[Y/N]")
                try:

                    await self.bot.wait_for("message", check=lambda m: m.content.startswith("Y") or m.content.startswith("y"), timeout=60)
                    embed_delete = discord.Embed(description="`Deleting this ticket in 10 seconds type >fstop/>fs to cancel`")
                    await ctx.send(embed=embed_delete)
                    try:
                        await self.bot.wait_for("message",check=lambda m: m.content.startswith(">fstop") or m.content.startswith(">fs"), timeout=10)
                        embed = discord.Embed(description="`canceling the command`")
                        return await ctx.send(embed=embed)
                    except asyncio.TimeoutError:

                        ticket_filter = {"ticket_id": channel.id}
                        await self.bot.ticket.delete_by_custom(ticket_filter)
                        await channel.delete()

                except asyncio.TimeoutError:
                    embed = discord.Embed(description="`Time out canceling the command`")
                    await ctx.send(embed=embed)

    @commands.command(name="Claim", description="Claim Tickets to provide Support", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889, 831405039830564875)
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
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889, 831405039830564875)
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
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
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
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def remove(self, ctx, *, target: Union[discord.Member, discord.Role]):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            overwrite = channel.overwrites_for(target)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(target, overwrite=overwrite)
            embed = discord.Embed(description=f"<:allow:819194696874197004> | Removed {target.mention} to the Tick")

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(tickets(bot))
