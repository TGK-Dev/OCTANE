import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import Interaction
from ui.poll import *
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from io import BytesIO
import os

class Dump(app_commands.Group, name="dump", description="dump data"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name="dump", description="Dump data from discord Objectes")

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

            await interaction.edit_original_message(attachments=[file])


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
            
            await interaction.edit_original_message(embed=embed, content=None)

        elif len(invited_users) > 10:
            users = ""
            for i in invited_users:
                users += f"{int(i)}\n"
            buffer = BytesIO(users.encode('utf-8'))
            file = discord.File(buffer, filename=f"{user.name}.txt")
            buffer.close()
            await interaction.edit_original_message(content=None,attachments=[file])
       

class Poll(app_commands.Group):
    def __init__(self):
        super().__init__(name="poll", description="Poll commands")
    
    @app_commands.command(name='create')
    @app_commands.describe(title="title of the poll", options="options of the poll spearated by !", duration="duration of the poll ex: 1h30m", thread="Create poll with thread", one_vote="only one vote per user")
    @app_commands.rename(one_vote="single_vote")
    @app_commands.default_permissions(manage_messages=True)
    async def create(self, interaction: Interaction, title: str, options: str,duration: str, thread: bool=None, one_vote: bool=False):
        await make_poll(interaction, title, options, duration, thread, one_vote)

class Serverutils(commands.Cog, description="Contains commands that are useful for the server."):
    def __init__(self, bot):
        self.bot = bot
        self.poll_check = self.check_polls.start()
    
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
        print("event Triggered")
        channel = self.bot.get_channel(poll['channel'])

        try:
            msg = await channel.fetch_message(poll['_id'])
        except discord.errors.NotFound:
            self.bot.poll.delete(poll['_id'])
        
        view = discord.ui.View.from_message(msg)
        for buttin in view.children:
            buttin.disabled = True
        embed = msg.embeds[0]
        embed.set_footer(text=f"Poll Has Ended • {embed.footer.text}")
        await msg.edit(view=view, embed=embed)                

        try:
            self.bot.polls.pop(poll['_id'])
        except KeyError:
            pass        
        
        await self.bot.poll.delete(poll['_id'])

    @commands.Cog.listener()
    async def on_ready(self):
        currrent_polls = await self.bot.poll.get_all()
        for poll in currrent_polls:
            channel = self.bot.get_channel(poll['channel'])
            msg = await channel.fetch_message(poll['_id'])
            self.bot.add_view(PollView(msg.embeds[0]))
            self.bot.polls[poll['_id']] = poll

        self.bot.tree.add_command(Dump(self.bot), guild=discord.Object(785839283847954433))
        self.bot.tree.add_command(Poll(), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded.")


async def setup(bot):
    await bot.add_cog(Serverutils(bot))