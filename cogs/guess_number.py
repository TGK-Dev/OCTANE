from discord import Interaction
from discord.ext import commands
from discord import app_commands
from ui.buttons import Start_Gn
from utils.checks import Commands_Checks
import discord
import random
import asyncio

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

class Guess_number(commands.Cog, name="Guess The Number", description="Guess The Number Game"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Drop())
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_game_start(self, message: discord.Message, channel: discord.Thread, right_num: int,):

        def check(m):
            if m.channel.id == channel.id and m.content == str(right_num) and not m.author.bot:
                self.bot.guess_number[m.channel.id]['guess_num'] += 1
                return True
            if m.channel.id == channel.id and m.content != str(right_num):
                self.bot.guess_number[m.channel.id]['guess_num'] += 1
            
        try:
            win_message = await self.bot.wait_for('message', check=check, timeout=3600)
            await win_message.reply(f"{win_message.author.mention} You Guessed The Right Number")
            await channel.edit(name="Game Has Ended",archived=True, locked=True)

            data = message.embeds[0]
            data.add_field(name="Winner: ", value=f"{win_message.author.mention}(**{win_message.author.display_name}**)",inline=True)
            data.add_field(name="Guesses: ", value=self.bot.guess_number[win_message.channel.id]['guess_num'], inline=True )
            await message.edit(embed=data)

            win_embed = discord.Embed(description=f"🏆 {win_message.author.mention} Guessed The Correct Number", color=win_message.author.color)
            await message.reply(embed=win_embed)

        except asyncio.TimeoutError:

            await channel.send(f"No one won")
            await channel.edit(archived=True, locked=True)


    @app_commands.command(name="guessnumber",description="Guess The Number Game")
    @app_commands.describe(number="Max Range of Number")
    @app_commands.guilds(785839283847954433)
    async def guess_number(self, interaction: Interaction, number: app_commands.Range[int, 100, 1000]):
        embed = discord.Embed(title=f"{interaction.user} is Starting An Guess The Number Game",color=interaction.user.color,
        description=f"Start guessing the number in thread below after the event starts")
        embed.add_field(name="Range", value=f"0-{number}")
        embed.add_field(name="Channel", value=interaction.channel.mention)
        embed.set_footer(text=f"Buttons will be Expired in 5 Minutes")

        await interaction.response.send_message(embed=embed, ephemeral=False, view=Start_Gn(self.bot, interaction, number))

    @app_commands.command(name="drop", description="Drop a giveaway 1 enter wins")
    @app_commands.describe(item="item you want to drop")
    @app_commands.guilds(785839283847954433)
    async def drop(self, interaction: Interaction, item: str):
        embed = discord.Embed(title="Drop Incoming",color=interaction.user.color)
        embed.add_field(name="Prize:", value=f"{item}",inline=False)
        embed.add_field(name="Host:", value=f"**{interaction.user.display_name}**",inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False, view=Drop())

        

async def setup(bot):
    await bot.add_cog(Guess_number(bot))