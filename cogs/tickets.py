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
from typing import Union, overload

from discord.ext.commands.converter import CategoryChannelConverter
from discord.ext.commands.core import command
from discord.ui import view

description = "Ticket System For the Server Support"

class PersistentView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        url = 'https://dyno.gg/form/99ad4f31'
        self.add_item(discord.ui.Button(label='Ban Appeal', url=url))

    @discord.ui.button(label='Server Support', style=discord.ButtonStyle.red, custom_id='persistent_view:red', emoji="<:support:837272254307106849>")
    async def support(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        guild = interaction.guild
        data = await self.bot.ticket.find_by_custom({"_id": user.id, "guild": interaction.guild.id})
        if data and data['type'] == "support": 
            return await interaction.followup.send(f"Your last tickets still excites: <#{data['channel']}>", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True,read_message_history=True),            
        }
        channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), name=f"{user.name} Support Ticket", topic=f"User Id: {user.id}", overwrites=overwrites)
        await interaction.followup.send(f"You new Ticekt has Been Open in {channel.mention}", ephemeral=True)
        
        Tembed = discord.Embed(title=f"Hi {user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        Tembed.set_footer(text="Developed and Owned by Jay & utki007")
        await channel.send(f"{user.mention} | @here", embed=Tembed)
        user_data = {'_id': user.id,
                         'guild': user.guild.id,
                         'channel': channel.id,
                         'type': 'support'}
        await self.bot.ticket.upsert(user_data)

    @discord.ui.button(label='Partership', style=discord.ButtonStyle.green, custom_id='persistent_view:partner_ship', emoji="<:partner:837272392472330250>")
    async def partnership(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        guild = interaction.guild
        data = await self.bot.ticket.find_by_custom({"_id": user.id, "guild": interaction.guild.id})
        if data and data['type'] == "partnership":
            return await interaction.followup.send(f"Your last tickets still excites: <#{data['channel']}>", ephemeral=True)

        partnership_m = discord.utils.get(guild.roles, id=831405039830564875)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True,read_message_history=True),
            partnership_m: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True,read_message_history=True)
        }
        channel = await guild.create_text_channel(category=self.bot.get_channel(829230513516445736), name=f"{user.name} Partnership Ticket", topic=f"User Id: {user.id}", overwrites=overwrites)
                
        Tembed = discord.Embed(title=f"Hi {user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        Tembed.set_footer(text="Developed and Owned by Jay & utki007")
        m = await channel.send(f"{user.mention} | {partnership_m.mention}", embed=Tembed)
        await interaction.followup.send(f"You new Ticekt has Been Open in {channel.mention}", ephemeral=True)
        user_data = {'_id': user.id,
                    'guild': user.guild.id,
                    'channel': channel.id,
                    'type': 'partnership'}
        await self.bot.ticket.upsert(user_data)

class Confirm(discord.ui.View):
    def __init__(self, user=None):
        super().__init__()
        self.value = None
        self.user = user

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Thanks For Allowing us', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()
    async def interaction_check(self ,interaction):
        if interaction.user.id == self.user:
            return True
        else:
            await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(PersistentView(self.bot))
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')

    @commands.command()
    @commands.check_any(commands.has_any_role(831405039830564875, 799037944735727636), is_me())
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=PersistentView(self.bot))

    @commands.command()
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039), is_me())
    async def close(self, ctx):
        data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        if not data: return await ctx.send("Please use this command only in tickets")
        user = ctx.guild.get_member(int(data['_id']))
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = False
        await ctx.channel.set_permissions(user, overwrite=overwrite)
        embed = discord.Embed(color=0x2f3136, description=f"Ticket Closed By {ctx.author.mention}")
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039,831405039830564875), is_me())
    async def open(self, ctx):
        data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        if not data: return await ctx.send("Please use this command only in tickets")
        user = ctx.guild.get_member(int(data['_id']))
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        await ctx.channel.set_permissions(user, overwrite=overwrite)
        embed = discord.Embed(color=0x2f3136, description=f"Ticket Opend By {ctx.author.mention}")
        await ctx.send(content=f"<@{data['_id']}>",embed=embed)

    @commands.command(name="delete", description="delete the ticekt")
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039,831405039830564875), is_me())
    async def delete(self, ctx):
        data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})

        if not data: return await ctx.send("Please use this command only in tickets")

        msg = await ctx.send("Deleting this Ticekt in 10s `type fs` to cancel this command")
        try:
            await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == "fs", timeout=10)
            return await msg.edit(content="Ok cancelling the command")
        except asyncio.TimeoutError:
            await ctx.channel.delete()
            await self.bot.ticket.delete(data['_id'])

    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039,831405039830564875), is_me())
    async def transcript(self, ctx, limit: int = None, *, ticket=None):

        ticket = ticket if ticket else "Topic Not Given"

        limit = limit if limit else 500
        tz_info = "Asia/Kolkata"

        data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        view = Confirm(data['_id'])
        embed = discord.Embed(description=f"<@{data['_id']}> Press Below Button to allow us to save this conversation of this ticket, This conversation will not be share anywhere")
        m = await ctx.send(f"<@{data['_id']}>", embed=embed, view=view)
        await view.wait()
        if view.value is None:
            await m.edit('Timed out...')
        elif view.value:
            await m.edit(content="Saving Started",embed=None,view=None)
            channel = self.bot.get_channel(833386438338674718)
            transcript = await chat_exporter.export(ctx.channel, limit, tz_info)

            if transcript is None:
                return

            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                        filename=f"transcript-{ctx.channel.name}.html")

            await channel.send(f"{ctx.channel.name} | {ticket}", file=transcript_file)
            await m.edit(content=f"{ctx.author.mention} transcript Saved",)
            channel_file = discord.File(io.BytesIO(transcript.encode()),
                                        filename=f"transcript-{ctx.channel.name}.html")
            await ctx.send(f"{ctx.channel.name} | {ticket}", file=channel_file)
        else: 
            pass
    
    @commands.command(name="add", description="add User to the channel", usage="[member]")
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039,831405039830564875), is_me())
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
    @commands.check_any(commands.has_any_role(831405039830564875, 810134909372203039,831405039830564875), is_me())
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

def setup(bot):
    bot.add_cog(Tickets(bot))
