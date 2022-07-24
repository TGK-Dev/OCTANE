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

class Ticket_Panel_Roles(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} Roles")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = discord.Embed(title=f"Editing {self.name} Roles",color=discord.Color.blurple())

        for child in self.children:
            if child.label == "Support Roles":
                add_roles = ""
                rolesids = child.value.split(",")
                self.data['panels'][self.name]['support_roles'] = []
                for roleid in rolesids:
                    role = interaction.guild.get_role(int(roleid))
                    if role:
                        self.data['panels'][self.name]['support_roles'].append(role.id)
                        add_roles += f"{role.mention}\n"

                embed.add_field(name="Support Roles", value=add_roles)

            if child.label == "Ping Role":
                if child.value == "" or child.value == "None":
                    self.data['panels'][self.name]['ping_role'] = None
                    embed.add_field(name="Ping Role", value="None")
                else:
                    self.data['panels'][self.name]['ping_role'] = child.value
                    embed.add_field(name="Ping Role", value=child.value)

        await interaction.client.ticket_system.update(self.data)
        await interaction.followup.send(embed=embed)
