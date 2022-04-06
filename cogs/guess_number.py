import discord
import random
import asyncio
from discord.ext import commands
from utils.checks import checks
from discord import app_commands
from typing import List
list_of_items =[
    "Heist Starter",
    "1 Mil Dmc",
]

class Confirm(discord.ui.View):
    def __init__(self, message: discord.Message, ctx, range:int, bot):
        super().__init__(timeout=10)
        self.value = None
        self.message = message
        self.ctx = ctx
        self.range = range
        self.bot = bot

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction,button: discord.ui.Button):
        await interaction.response.edit_message(view=start(self.ctx, self.message, self.range, self.bot))
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction,button: discord.ui.Button):
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
    async def Start(self, interaction: discord.Interaction,button: discord.ui.Button):
        right_num = random.randint(0, self.max_num)
        await interaction.response.send_message(f"Starting, right number is: {right_num}", ephemeral=True)
        await interaction.user.send(f"Right Number is: {right_num}")
        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        button.label = str("Started")
        await self.message.edit(view=self)
        thread = await self.message.create_thread(name="Guess Number Here", auto_archive_duration=60)
        self.bot.dispatch('game_start', self.message, thread, right_num)
        self.bot.guess_number[thread.id] = {'thread': thread, 'right_num': right_num, 'guess_num': 0}
        await self.message.channel.send(f"Start guessing the number in thread above, {thread.mention}")

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.response.send_message("You nor the Staff or Host of the event", ephemeral=True)

class Drop(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label='Drop', style=discord.ButtonStyle.blurple, emoji="<a:GiftShake:820323765941436446>", custom_id="Drop:drop")
    async def drop(self, interaction: discord.Interaction,button: discord.ui.Button):
        self.stop()
        self.children[0].disabled=True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(content="You Won", ephemeral=True)        
        embed = interaction.message.embeds[0]
        embed.add_field(name="Winner: ", value=f"{interaction.user.mention}(**{interaction.user.display_name}**)",inline=False)
        await interaction.message.edit(embed=embed)

class Guess_number(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guess = 0
        
    async def item_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choice = [
            app_commands.Choice(name=cmd , value=cmd)
            for cmd in list_of_items if current.lower() in cmd.lower()
        ]

        return(choice)

    @app_commands.command(name="drop", description="Do a Drop of any item")
    @app_commands.describe(item="name of price")
    @app_commands.autocomplete(item=item_auto)
    @app_commands.guilds(discord.Object(785839283847954433))
    async def drop(self, interaction: discord.Interaction, item: str):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.send("You don't have permission to use this command")
        embed = discord.Embed(title="Drop Incoming",color=interaction.user.color)
        embed.add_field(name="Prize:", value=f"{item}",inline=False)
        embed.add_field(name="Host:", value=f"**{interaction.user.display_name}**",inline=False)
        await interaction.response.send_message("Drop droped",ephemeral=True)
        view = Drop()
        await interaction.channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Drop())
        print(f'{self.__class__.__name__} Cog has been loaded-----')

    @commands.Cog.listener()
    async def on_game_start(self, message:discord.Message, channel: discord.channel, right:int):
        #
        def check(m, total_guess=self.guess):
            if m.channel.id == channel.id and m.content == str(right):
                self.bot.guess_number[m.channel.id]['guess_num'] += 1
                return True
            elif m.channel.id == channel.id and m.content != str(right):
                self.bot.guess_number[m.channel.id]['guess_num'] += 1
        try:
            win_msg = await self.bot.wait_for("message", check=check, timeout=3600)
            await win_msg.reply(f"{win_msg.author.mention} You Guessed The Right Number")         
            await channel.edit(name="Game Has Ended",archived=True, locked=True)
            data = message.embeds[0]
            data.add_field(name="Winner: ", value=f"{win_msg.author.mention}(**{win_msg.author.display_name}**)",inline=True)
            data.add_field(name="Guesses: ", value=self.bot.guess_number[win_msg.channel.id]['guess_num'], inline=True )
            await message.edit(embed=data)
            win_embed = discord.Embed(description=f"🏆 {win_msg.author.mention} Guessed The Correct Number", color=win_msg.author.color)
            await message.reply(embed=win_embed)
            
        except asyncio.TimeoutError:

            await channel.send(f"No one won")
            await channel.edit(archived=True, locked=True)

    @commands.command(name="Guess Number", description="starting Guess The Number Game!", aliases=['gn'])
    @commands.check_any(checks.can_use())
    async def guess_number(self, ctx, max: int):
        embed = discord.Embed(title=f"{ctx.author} is Starting An Guess The Number Game",color=ctx.author.color,
        description=f"Start guessing the number in thread below after the event starts")
        embed.add_field(name="Range", value=f"0-{max}")
        embed.add_field(name="Channel", value=ctx.channel.mention)
        embed.set_footer(text=f"Confirm The Range and Channel and use buttons below")

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

async def setup(bot):
    await bot.add_cog(Guess_number(bot))