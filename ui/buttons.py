from discord import Interaction
from discord.ext import commands
import random
import discord
import asyncio
class verify(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot =  bot
        self.guild = self.bot.get_guild(785839283847954433)
        self.role = discord.utils.get(self.guild.roles, id=953006119436030054)
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.gray, custom_id="verify", emoji="<:verify_TGK:966187540774269008>")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.role in interaction.user.roles:
            await interaction.response.send_message(f"you have been verified, check <#944670176115294228> and <#944670050252648468>", ephemeral=True)
            await asyncio.sleep(2)
            await interaction.user.remove_roles(self.role)
        else:
            await interaction.response.send_message("You are already verified, create ticket from <#785901543349551104>", ephemeral=True)
class Start_Gn(discord.ui.View):
    def __init__(self, bot, interaction, number):
        self.bot = bot
        self.interaction = interaction
        self.number = number
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.green)
    async def start_game(self, interaction: Interaction, button: discord.Button):
        right_num = random.randint(1, self.number)
        await interaction.response.send_message(f"Right number is: {right_num}", ephemeral=True)

        await interaction.user.send(f"Right Number is: {right_num}")

        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        button.label = str("Started")

        await interaction.message.edit(view=self)

        thread = await interaction.message.create_thread(name="Guess Number Here", auto_archive_duration=60)

        self.bot.dispatch('game_start', interaction.message, thread, right_num)

        self.bot.guess_number[thread.id] = {'thread': thread, 'right_num': right_num, 'guess_num': 0}

        await interaction.channel.send(f"Start guessing the number in thread above, {thread.mention}")
    
    async def on_timeout(self, interaction):
        self.stop()

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.interaction.user.id:
            return True
        else:
            await interaction.response.send_message("You can't start the game, you are not the host", ephemeral=True)

class Invite_Panel(discord.ui.View):
    def __init__(self, staff_invite: discord.Invite, public_invite: discord.Invite):
        super().__init__(timeout=3600)
        self.staff_invite = staff_invite
        self.public_invite = public_invite
    
    @discord.ui.button(label="Public Invite", style=discord.ButtonStyle.green, custom_id="public-invite")
    async def public_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.public_invite, ephemeral=True)

    @discord.ui.button(label="Staff-invite", style=discord.ButtonStyle.red, custom_id="staff-invite")
    async def staff_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(self.staff_invite,ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this button.", ephemeral=True)
    
    
