import discord
from discord import Interaction, ui

class Channel_Select(ui.View):
    def __init__(self, author: discord.Member, interaction: Interaction=None, message: discord.Message=None):
        super().__init__(timeout=120)
        self.interaction = None
        self.message = None
        self.author: discord.Member = author
        self.value = None
        self.channels = None
    
    @ui.select(cls=ui.ChannelSelect, placeholder="Select a channel from below", channel_types=[discord.ChannelType.text],max_values=20)
    async def channel_select(self, interaction: Interaction, select: ui.ChannelSelect):
        self.value = True
        self.channels = select.values
        self.interaction = interaction
        self.stop()
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.author.id:
            return True
        else:
            await interaction.response.send_message("This is not your confirmation menu.", ephemeral=True)
            return False
    
    # async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item):
    #     try:
    #         await interaction.response.send_message(f"An error occured: {error}", ephemeral=True)
    #     except:
    #         await interaction.followup.send(f"An error occured: {error}", ephemeral=True)

class Role_Select(ui.View):
    def __init__(self, author: discord.Member, interaction: Interaction=None, message: discord.Message=None):
        super().__init__(timeout=120)
        self.interaction = None
        self.message = None
        self.author: discord.Member = author
        self.value = None
        self.roles = None
    
    @ui.select(cls=ui.RoleSelect, placeholder="Select a role from below", max_values=20)
    async def role_select(self, interaction: Interaction, select: ui.RoleSelect):
        self.value = True
        self.roles = select.values
        self.interaction = interaction
        self.stop()
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.author.id:
            return True
        else:
            await interaction.response.send_message("This is not your confirmation menu.", ephemeral=True)
            return False
    
    # async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item):
    #     try:
    #         await interaction.response.send_message(f"An error occured: {error}", ephemeral=True)
    #     except:
    #         await interaction.followup.send(f"An error occured: {error}", ephemeral=True)

class User_Select(ui.View):
    def __init__(self, author: discord.Member, interaction: Interaction=None, message: discord.Message=None):
        super().__init__(timeout=120)
        self.interaction = None
        self.message = None
        self.author: discord.Member = author
        self.value = None
        self.users = None
    
    @ui.select(cls=ui.UserSelect, placeholder="Select a user from below", max_values=20)
    async def user_select(self, interaction: Interaction, select: ui.UserSelect):
        self.value = True
        self.users = select.values
        self.interaction = interaction
        self.stop()
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.author.id:
            return True
        else:
            await interaction.response.send_message("This is not your confirmation menu.", ephemeral=True)
            return False
    
    # async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item):
    #     try:
    #         await interaction.response.send_message(f"An error occured: {error}", ephemeral=True)
    #     except:
    #         await interaction.followup.send(f"An error occured: {error}", ephemeral=True)

class Mentionable_Select(ui.View):
    def __init__(self, author: discord.Member, interaction: Interaction=None, message: discord.Message=None):
        super().__init__(timeout=120)
        self.interaction = None
        self.message = None
        self.author: discord.Member = author
        self.value = None
        self.mentionables = None
    
    @ui.select(cls=ui.MentionableSelect, placeholder="Select a mentionable from below", max_values=20)
    async def mentionable_select(self, interaction: Interaction, select: ui.MentionableSelect):
        self.value = True
        self.mentionables = select.values
        self.interaction = interaction
        self.stop()
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.author.id:
            return True
        else:
            await interaction.response.send_message("This is not your confirmation menu.", ephemeral=True)
            return False
    
    # async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item):
    #     try:
    #         await interaction.response.send_message(f"An error occured: {error}", ephemeral=True)
    #     except:
    #         await interaction.followup.send(f"An error occured: {error}", ephemeral=True)

