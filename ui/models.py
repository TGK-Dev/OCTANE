from discord import Interaction
from discord.ext import commands
import discord.ui as ui
import discord

class Mass_ban(ui.Modal, title="Mass Ban Modal"):
    def __init__(self, bot: commands.Bot, interaction: Interaction, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = interaction
        self.reason = reason
    
    mass_ban_users = ui.TextInput(label="User Id's", placeholder="Enter user id's seperated by spaces", style=discord.TextStyle.paragraph, min_length=18, custom_id="MASS:BAN:USER:IDS")

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        user_ids = self.mass_ban_users.value.split(" ")
        users = ""
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(int(user_id))
                await interaction.guild.ban(user, reason=f"Mass Ban Authorised by {self.ctx.user.name}#{self.ctx.user.discriminator} | Reason: {self.reason.value}")
            except discord.NotFound:
                pass
        
        await interaction.followup.send(users)
    
    async def on_timeout(self, error: Exception, interaction: Interaction):
        embed = discord.Embed(description="Error: " + str(error), color=0xFF0000)
        await interaction.response.send_message(embed=embed)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id == self.ctx.user.id and interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message("You do not have permission to use this command/modal.", ephemeral=True)
            return False

class Ticket_Panel_edit(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} description")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(f"Editing {self.name} description")
        print(self.children)
        for child in self.children:
            if child.label == "Description":
                self.data['panels'][self.name]['description'] = child.value
                await interaction.edit_original_message(content=f"{self.name} description: {child.value}")
                await interaction.client.ticket_system.update(self.data)
                break

class Ticket_Panel_edit_Other(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} Extra Info")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        for child in self.children:
            if child.label == "Emoji":
                self.data['panels'][self.name]['emoji'] = child.value
            if child.label == "Color":
                if child.value == "":
                    self.data['panels'][self.name]['color'] = None
                if child.value in ['red', 'green', 'blue', 'grey']:
                    self.data['panels'][self.name]['color'] = child.value
            
            
        embed = discord.Embed(title=f"Editing {self.name} Extra Info", description=f"{self.name} Extra Info", color=0xFF0000)
        embed.add_field(name="Emoji", value=self.data['panels'][self.name]['emoji'])
        embed.add_field(name="Color", value=self.data['panels'][self.name]['color'])
        await interaction.response.send_message(embed=embed)
        await interaction.client.ticket_system.update(self.data)




