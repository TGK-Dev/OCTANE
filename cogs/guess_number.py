import discord
import random
import asyncio
from discord.ext import commands
from utils.checks import checks

class Confirm(discord.ui.View):
    def __init__(self, message: discord.Message, ctx, range:int, bot):
        super().__init__(timeout=10)
        self.value = None
        self.message = message
        self.ctx = ctx
        self.range = range
        self.bot = bot

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=start(self.ctx, self.message, self.range, self.bot))
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

    async def on_timeout(self):
        for view in self.children:
            view.disabled = True
        await self.message.edit(view=self)

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

class start(discord.ui.View):
    def __init__(self, ctx,message: discord.Message, max_num: int, bot):
        super().__init__()
        self.ctx = ctx
        self.message = message
        self.max_num = max_num
        self.bot = bot

    @discord.ui.button(label='Start Game!', style=discord.ButtonStyle.green)
    async def Start(self, button: discord.ui.Button, interaction: discord.Interaction):
        right_num = random.randint(0, self.max_num)
        await interaction.response.send_message(f"Starting, right number is: {right_num}", ephemeral=True)
        await interaction.user.send(f"Right Number is: {right_num}")
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        button.label = str("Started")
        await self.message.edit(view=self)
        thread = await self.message.create_thread(name="Guess Number Here", auto_archive_duration=60)
        self.bot.dispatch('game_start', self.message, thread, right_num)
        await self.message.channel.send(f"Start guessing the number in thread above, {thread.mention}")

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

class Guess_number(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guess = 0



    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded-----')

    @commands.Cog.listener()
    async def on_game_start(self, message:discord.Message, channel: discord.channel, right:int):
        #
        def check(m, total_guess=self.guess):
            if m.channel.id == channel.id and m.content == str(right):
                return True
            elif m.channel.id == channel.id and m.content != str(right):
                self.guess = self.guess +1
                print(self.guess)
        try:
            win_msg = await self.bot.wait_for("message", check=check, timeout=3600)
            await win_msg.reply(f"{win_msg.author.mention} You Guessed The Right Number")         
            await channel.edit(name="Game Has Ended",archived=True, locked=True)
            data = message.embeds[0].to_dict()
            (data['fields'][len(data['fields'])-1]) = {'name': 'Winner', 'value': f'{win_msg.author.mention} | {win_msg.author.name}', 'inline': None}
            data['fields'].append({'name': 'Total Guesse', 'value': f'{self.guess}', 'inline': False})
            await message.edit(embed=discord.Embed().from_dict(data))
            win_embed = discord.Embed(description=f"🏆 {win_msg.author.mention} Guessed The Correct Number", color=win_msg.author.color)
            await message.reply(embed=win_embed)
            
        except asyncio.TimeoutError:

            await channel.send(f"No one won")
            await channel.edit(archived=True, locked=True)

    @commands.command(name="Guess Number", description="starting Guess The Number Game!", aliases=['gn'])
    @commands.check_any(checks.can_use())
    async def guess_number(self, ctx, max: int):
        self.guess = 0
        embed = discord.Embed(title=f"{ctx.author} is Starting An Guess The Number Game",color=ctx.author.color,
        description=f"Start guessing the number in thread below after the event starts")
        embed.add_field(name="Range", value=f"0-{max}")
        embed.add_field(name="Channel", value=ctx.channel.mention)
        embed.add_field(name="Note:", value="Confirm The Range and Channel and use buttons below", inline=False)

        msg = await ctx.channel.send(embed=embed)
        view = Confirm(msg ,ctx, max, self.bot)
        await msg.edit(view=view)

        await view.wait()
        if view.value is None:
            await msg.edit('Time Outed')
        elif view.value:
            pass
        else:
            await msg.delete()


def setup(bot):
    bot.add_cog(Guess_number(bot))

#None Thread Version
# from asyncio.tasks import wait, wait_for
# from datetime import time
# from logging import FATAL
# import re
# import discord
# import random
# import asyncio
# from discord.ext import commands
# from discord.ext.commands.core import command
# from discord.ui import view

# class Confirm(discord.ui.View):
#     def __init__(self, message: discord.Message, ctx, range:int, bot):
#         super().__init__(timeout=10)
#         self.value = None
#         self.message = message
#         self.ctx = ctx
#         self.range = range
#         self.bot = bot

#     @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
#     async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.edit_message(view=start(self.ctx, self.message, self.range, self.bot))
#         self.value = True
#         self.stop()

#     @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
#     async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.send_message('Cancelling', ephemeral=True)
#         self.value = False
#         self.stop()

#     async def on_timeout(self):
#         for view in self.children:
#             view.disabled = True
#         await self.message.edit(view=self)

#     async def interaction_check(self ,interaction):
#         if interaction.user.id == self.ctx.author.id:
#             return True
#         else:
#             await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

# class start(discord.ui.View):
#     def __init__(self, ctx,message: discord.Message, max_num: int, bot):
#         super().__init__()
#         self.ctx = ctx
#         self.message = message
#         self.max_num = max_num
#         self.bot = bot

#     @discord.ui.button(label='Start Game!', style=discord.ButtonStyle.green)
#     async def Start(self, button: discord.ui.Button, interaction: discord.Interaction):
#         right_num = random.randint(0, self.max_num)
#         await interaction.response.send_message(f"Starting, right number is: {right_num}", ephemeral=True)
#         await interaction.user.send(f"Right Number is: {right_num}")
#         button.style = discord.ButtonStyle.blurple
#         button.disabled = True
#         button.label = str("Started")
#         await self.message.edit(view=self)
#         self.bot.dispatch('game_start', self.message, self.message.channel, right_num)

#     async def interaction_check(self ,interaction):
#         if interaction.user.id == self.ctx.author.id:
#             return True
#         else:
#             await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

# class Cog_name(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
    
#     @commands.Cog.listener()
#     async def on_ready(self):
#         print(f'{self.__class__.__name__} Cog has been loaded-----')

#     @commands.Cog.listener()
#     async def on_game_start(self, message:discord.Message, channel: discord.TextChannel, right:int):
#         role = channel.guild.default_role
#         overwrite = channel.overwrites_for(role)
#         overwrite.send_messages = True
#         await channel.set_permissions(role, overwrite=overwrite)

#         try:
#             win_msg = await self.bot.wait_for("message", check=lambda m: m.channel.id == channel.id and m.content == str(right), timeout=3600)
#             await win_msg.reply(f"{win_msg.author.mention} You Guessed The Right Number")
#             overwrite.send_messages = False
#             await channel.set_permissions(role, overwrite=overwrite)

#             data = message.embeds[0].to_dict()
#             (data['fields'][len(data['fields'])-1]) = {'name': 'Winner', 'value': f'{win_msg.author.mention} | {win_msg.author.name}', 'inline': False}
#             await message.edit(embed=discord.Embed().from_dict(data))

#         except asyncio.TimeoutError:
#             await message.channel.send(f"No one won")
#             overwrite.send_messages = False
#             await channel.set_permissions(role, overwrite=overwrite)

#     @commands.command(name="Guess Number", description="starting Guess The Number Game!", aliases=['gn'])
#     async def guess_number(self, ctx, max: int):
#         embed = discord.Embed(title=f"{ctx.author} is Starting An Guess The Number Game",color=ctx.author.color,
#         description=f"You have to Guess The Number When Games Starts")
#         embed.add_field(name="Range", value=f"0-{max}")
#         embed.add_field(name="Channel", value=ctx.channel.mention)
#         embed.add_field(name="Note:", value="Confirm The Range and Channel and use buttons below", inline=False)

#         msg = await ctx.channel.send(embed=embed)
#         view = Confirm(msg ,ctx, max, self.bot)
#         await msg.edit(view=view)

#         await view.wait()
#         if view.value is None:
#             await msg.edit('Time Outed')
#         elif view.value:
#             pass
#         else:
#             await msg.delete()


# def setup(bot):
#     bot.add_cog(Cog_name(bot))