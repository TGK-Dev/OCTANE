import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import Interaction
from ui.poll import *
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from io import BytesIO
from utils.db import Document
from ui.buttons import Payout_Buttton
import os

class Dump(commands.GroupCog, name="dump", description="dump data"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role", description="Dump role data")
    async def dump_user(self, interaction: Interaction, role: discord.Role):
        if len(role.members) <= 10:
            msg = f"{role.name} has {len(role.members)} members:\n"
            embed = discord.Embed(title=role.name, description="", color=role.color)
            for member in role.members:
                embed.description += f"{member.mention} | `{member.id}`\n"
            
            await interaction.response.send_message(msg, embed=embed)

        elif len(role.members) > 10:
            await interaction.response.send_message("Role has too many members making file to send.")
            members = ""
            for member in role.members:
                members += f"{member.name} | `{member.id}`\n"
            buffer = BytesIO(members.encode('utf-8'))
            file = discord.File(buffer, filename=f"{role.name}.txt")
            buffer.close()

            await interaction.edit_original_response(attachments=[file])


    @app_commands.command(name="invite", description="Dumps invite data of user")
    async def invite(self, interaction: Interaction, user: discord.Member):
        data = await self.bot.invites.find_by_custom({'_id': user.id})
        if not data: return await interaction.response.send_message("No Data to Dump")
        await interaction.response.send_message("<a:loading:998834454292344842> Loading Data...")
        invited_users = list(set(data['userInvited']))

        if len(invited_users) <= 10:
            
            embed = discord.Embed(description="")
            for i in invited_users:
                embed.description += f"{int(i)}\n"
            
            await interaction.edit_original_response(embed=embed, content=None)

        elif len(invited_users) > 10:
            users = ""
            for i in invited_users:
                users += f"{int(i)}\n"
            buffer = BytesIO(users.encode('utf-8'))
            file = discord.File(buffer, filename=f"{user.name}.txt")
            buffer.close()
            await interaction.edit_original_response(content=None,attachments=[file])
       

class Poll(commands.GroupCog, name="poll", description="poll commands"):
    def __init__(self, bot):
        self.bot = bot
        self.poll_check = self.check_polls.start()

    
    @commands.Cog.listener()
    async def on_ready(self):
        for poll in await self.bot.poll.get_all():
            self.bot.polls[poll['_id']] = poll
            self.bot.add_view(PollView(poll))
        print(f"{self.__class__.__name__} Cog has been loaded.")
    
    def cog_unload(self):
        self.poll_check.cancel()

    @tasks.loop(seconds=10)
    async def check_polls(self):
        current_polls = deepcopy(self.bot.polls)
        for item, value in current_polls.items():
            if datetime.datetime.now() > value['end_time']:
                self.bot.dispatch('poll_end', value)
    
    @check_polls.before_loop
    async def before_check_current_polls(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_poll_end(self, poll):
        channel = self.bot.get_channel(poll['channel'])
        try:
            msg = await channel.fetch_message(poll['_id'])
        except discord.errors.NotFound:
            self.bot.poll.delete(poll['_id'])
        
        view = discord.ui.View.from_message(msg)
        for button in view.children:
            button.disabled = True
            button.style = discord.ButtonStyle.green

        embed = msg.embeds[0]
        for field in embed.fields:
            index = embed.fields.index(field)
            embed.set_field_at(index=index, name=f"{field.name} | {poll['options'][str(index)]['count']} ({poll['options'][str(index)]['count']/poll['total_votes']*100:.2f}%)", value=field.value, inline=field.inline)
        
        embed.set_footer(text="Poll has ended automatically.")
        await msg.edit(view=view, embed=embed)                

        try:
            self.bot.polls.pop(poll['_id'])
        except KeyError:
            pass        
        
        await self.bot.poll.delete(poll['_id'])
    
    @app_commands.command(name='create', description="Create a poll")
    @app_commands.describe(title="title of the poll", options="options of the poll spearated by !", duration="duration of the poll ex: 1h30m", thread="Create poll with thread")
    @app_commands.default_permissions(manage_messages=True)
    async def create(self, interaction: Interaction, title: str, options: str,duration: str, thread: bool=None):
        await make_poll(interaction, title, options, duration, thread)


class Payout(commands.GroupCog, name="payout"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.payout = Document(self.bot.db, "payout")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Payout_Buttton())
        print(f"{self.__class__.__name__} Cog has been loaded.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.guild.id != 785839283847954433: return
        if not message.author.bot: return
        if message.author.id != 693167035068317736: return
        if message.channel.id != 1040975933772931172: return
        if len(message.embeds) == 0: return

        embed = message.embeds[0]
        if embed.title == "<:Crwn2:872850260756664350> **__WINNER!__**" and len(message.mentions) == 1:
            winner = message.mentions[0]
            price = "10M Dmc"
            event = "daily Rumble"
            message_link = message_link.split("/")

            data = {'_id': message.id,'event': event,'winner': winner.id,'price': price,'message_link': message_link,'set_by': "AutoMatic Payout System", 'log_channel_id': None}
            embed = discord.Embed(title="Payout Queued")
            embed.add_field(name="Event", value=f"**<:nat_reply_cont:1011501118163013634> {event}**")
            embed.add_field(name="Winner", value=f"**<:nat_reply_cont:1011501118163013634> {winner.mention}**")
            embed.add_field(name="Price", value=f"**<:nat_reply_cont:1011501118163013634> {price}**")
            embed.add_field(name="Channel", value=f"**<:nat_reply_cont:1011501118163013634> {message.channel.mention}**")
            embed.add_field(name="Message Link", value=f"**<:nat_reply_cont:1011501118163013634> [Click Here]({message.jump_url})**")
            embed.add_field(name="Set By", value=f"**<:nat_reply_cont:1011501118163013634> AutoMatic Payout System**")
            embed.add_field(name="Payout Status", value="**<:nat_reply_cont:1011501118163013634> Pending**")
            embed.color = discord.Color.random()

            payout_channel = self.bot.get_channel(1031982594826457098)
            msg = await payout_channel.send(embed=embed, content=f"{winner.mention}, you will be paid out in the next `24hrs`! \n> If not paid within the deadline claim from <#785901543349551104>.", view=Payout_Buttton())
            data['log_channel_id'] = msg.id
            await self.bot.payout.insert(data)
            await message.channel.send(f"{winner.mention}, you price has been queued for payout. Please wait for the payout to be processed. \n> If not paid within the deadline claim from <#785901543349551104>.")            
        
    
    @app_commands.command(name="set", description="Set payout for a event")
    @app_commands.describe(event="event name", message_link="event message link", winner="winner of the event", price="price of the event")
    async def set(self, interaction: Interaction, event: str, message_link: str, winner: discord.Member, price: str):
        await interaction.response.send_message("Setting payout...", ephemeral=True)

        message_link = message_link.split("/")
        if len(message_link) < 6:
            return await interaction.edit_original_response(content="Invalid message link split")

        channel = self.bot.get_channel(int(message_link[5]))
        if not channel:
            return await interaction.edit_original_response(content="Message link channel not found")
        try:
            message = await channel.fetch_message(int(message_link[6]))
        except discord.NotFound:
            return await interaction.edit_original_response(content="Message not found")
        
        data = await self.bot.payout.find(message.id)
        if data: return await interaction.edit_original_response(content="Payout already set for this event")
        data = {'_id': message.id,'event': event,'winner': winner.id,'price': price,'message_link': message_link,'set_by': interaction.user.id, 'log_channel_id': None}

        await interaction.edit_original_response(content="Payout added to queue successfully")

        embed = discord.Embed(title="Payout Queued")
        embed.add_field(name="Event", value=f"**<:nat_reply_cont:1011501118163013634> {event}**")
        embed.add_field(name="Winner", value=f"**<:nat_reply_cont:1011501118163013634> {winner.mention}**")
        embed.add_field(name="Price", value=f"**<:nat_reply_cont:1011501118163013634> {price}**")
        embed.add_field(name="Channel", value=f"**<:nat_reply_cont:1011501118163013634> {message.channel.mention}**")
        embed.add_field(name="Message Link", value=f"**<:nat_reply_cont:1011501118163013634> [Click Here]({message.jump_url})**")
        embed.add_field(name="Set By", value=f"**<:nat_reply_cont:1011501118163013634> {interaction.user.mention}**")
        embed.add_field(name="Payout Status", value="**<:nat_reply_cont:1011501118163013634> Pending**")

        embed.color = discord.Color.random()
        embed.set_footer(text="Payout Created At", icon_url=interaction.guild.icon.url)
        embed.timestamp = datetime.datetime.now()
        
        payout_channel = self.bot.get_channel(1031982594826457098)
        msg = await payout_channel.send(embed=embed, content=f"{winner.mention}, you will be paid out in the next `24hrs`! \n> If not paid within the deadline claim from <#785901543349551104>.", view=Payout_Buttton())
        data['log_channel_id'] = msg.id
        await self.bot.payout.insert(data)

async def setup(bot):
    await bot.add_cog(Payout(bot), guild=discord.Object(785839283847954433))
    await bot.add_cog(Poll(bot), guild=discord.Object(785839283847954433))
    await bot.add_cog(Dump(bot), guild=discord.Object(785839283847954433))
