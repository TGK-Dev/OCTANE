import random
import asyncio
import datetime
import discord
import chat_exporter
import io
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

        if message.id == 836537042614616115:

            if payload.emoji.name == "help":

                channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), sync_permissions=True, name=f"{member.display_name} Ticket", topic=f"User Id: {member.id}")
                overwrite = channel.overwrites_for(member)
                overwrite.send_messages = True
                overwrite.view_channel = True

                await self.bot.ticket.increment(4455160013290432032, 1, "globle")
                current_ticket_count = {'_id': 4455160013290432032}
                counts = await self.bot.ticket.find_many_by_custom(current_ticket_count)

                for count in counts:
                    goble_count = count['globle']

                embed = discord.Embed(title=f"Hi {member.display_name}, Welcome to Server Support",
                    color=0x008000,
                    description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
                embed.set_footer(text="Developed and Owned by Jay & utki007")

                ticket_filter = {"user_id": member.id, "guild_id": guild.id, "ticket_number": goble_count}
                ticket_data = {"ticket_id": channel.id, "timestamp": datetime.datetime.now()}
                await self.bot.ticket.upsert_custom(ticket_filter, ticket_data)

                await channel.edit(name=f"{member.display_name} ticket {goble_count}")
                await channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)

                await channel.send(f"{member.mention}", embed=embed)

                await message.remove_reaction(payload.emoji, member)
        else:
            return

    @commands.command(name="eml", hidden=True)
    @commands.has_role(785842380565774368)
    async def eml(self, ctx):
        embed = discord.Embed(title=f"Hi {ctx.author.display_name}, Welcome to Server Support",
                    color=0x008000,
                    description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")
        await ctx.send(embed=embed)

    @commands.command(name="setup", hidden=True)
    @commands.has_role(785842380565774368)
    async def setup(self, ctx):
        embed = discord.Embed(title="Server Support",
            description="React below with <:help:836533559325753405>. This will help you to contact the server staff to help you / discussion about partnership",
            color=0x2ECC71)
        message = await ctx.send(embed=embed)
        emoji = self.bot.get_emoji(836533559325753405)
        await message.add_reaction(emoji)

    @commands.command(name="close", description="close The ticket", usage="")
    async def close(self, ctx):
        if ctx.channel.category.id == 829230513516445736:
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

        ticket_filter = {"ticket_id": ctx.channel.id}

        tickets = await self.bot.ticket.find_many_by_custom(ticket_filter)

        if not bool(tickets):
            return await ctx.send(f"Couldn't find any Close Tickets")

        tickets = sorted(tickets, key=lambda x: x["ticket_number"])

        for ticket in tickets:
            member = ctx.guild.get_member(ticket['user_id'])
            
            await ctx.channel.set_permissions(member, view_channel=True, send_messages=True, attach_files=True, embed_links=True)
            
            embed = discord.Embed(color=0x02ff06, description=f"ticket open by {ctx.author.mention}")

            await ctx.send(embed=embed)
            


    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def transcript(self, ctx, limit: int=None, tz_info=None):

        limit = limit if limit else 500
        tz_info = tz_info if tz_info else "Asia/Kolkata"

        channel =  self.bot.get_channel(833386438338674718)
        transcript = await chat_exporter.export(ctx.channel, limit, tz_info)

        if transcript is None:
            return

        transcript_file = discord.File(io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")

        await channel.send(f"{ctx.channel.name}", file=transcript_file)
        await ctx.send("transcript Saved")

        
    @commands.command(name="delete", description="delete the ticket", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def delete(self, ctx):
        channel = ctx.channel
        async with ctx.typing():
            if ctx.channel.category.id == 829230513516445736:
                await ctx.send("Are Your sure?[Y/N]")
                try:

                    await self.bot.wait_for("message", check=lambda m: m.content.startswith("Y") or m.content.startswith("y"), timeout=60)
                    embed_delete = discord.Embed(description="``Deleting this ticket in 10 seconds``")
                    await ctx.send(embed=embed_delete)
                    ticket_filter = {"ticket_id": channel.id}

                    await self.bot.ticket.delete_by_custom(ticket_filter)
                    await asyncio.sleep(10)
                    await channel.delete()
                except asyncio.TimeoutError:
                    embed = discord.Embed(description="``Time out canceling the commands ``")
                    await ctx.send(embed=embed)

    @commands.command(name="Claim", description="Claim Tickets to provide Support", usage="")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889, 831405039830564875)
    async def Claim(self, ctx):
        guild = ctx.guild

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

    @commands.command(name="adduser", description="add User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def adduser(self, ctx, member: discord.User=None):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if member == ctx.author:
                await ctx.send("you use command on your self")

            await channel.set_permissions(member, send_messages=True, view_channel=True)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The User {member.mention} Is added to the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)


    @commands.command(name="removeuser", description="Remove User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def removeuser(self, ctx, member:discord.Member):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if member == ctx.author:
                await ctx.send("you use command on your self")

            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = False
            overwrite.send_messages = False

            await channel.set_permissions(member, send_messages=None, view_channel=None)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The User {member.mention} Is Remove from the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)

    @commands.command(name="addrole", description="add User to the channel", usage="[member] [channel]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def addrole(self, ctx, role: discord.Role):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            if role == ctx.guild.default_role:
                return await ctx.send("you need to enter role mention/id or u can't add this role")

            await channel.set_permissions(role, send_messages=True, view_channel=True)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The Role {role.mention} Is added to the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)

    @commands.command(name="removerole", description="Remove User to the channel", usage="[Role.id/mention] [channel]", aliases=["removr"])
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def removerole(self, ctx, role:discord.Role):
        channel = ctx.channel
        if ctx.channel.category.id == 829230513516445736:

            await channel.set_permissions(role, send_messages=None, view_channel=None)

            embed = discord.Embed(
                color=0x02ff06,
                description=f"The Role {role.mention} Is Remove from the Channel"
                )
            await ctx.message.delete()
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(tickets(bot))
