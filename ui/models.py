from discord import Interaction
from discord.ext import commands
from discord import app_commands
from utils.callbacks import Normal_CallBack, Argument_CallBack
import discord.ui as ui
import discord
import json

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

class Embed_Modal(discord.ui.Modal, title="Embed Modal"):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    embed_code = ui.TextInput(label="Embed Code", placeholder="Enter the embed code", style=discord.TextStyle.paragraph, custom_id="EMBED:CODE", required=True)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True)
        embed = json.loads(self.embed_code.value)
        embed['type'] = 'rich'        

        await interaction.followup.send(embed=discord.Embed.from_dict(embed))

class RenameTicket(discord.ui.Modal, title="New Name"):
    def __init__(self, bot, interaction):
        super().__init__(timeout=None)
        self.bot = bot
        self.interaction = interaction
    
    new_name = ui.TextInput(label="New Name", placeholder="Enter name of ticket", style=discord.TextStyle.short, custom_id="NEW:NAME", required=True)

    async def on_submit(self, interaction: Interaction):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("You do not have permission to use this command/modal.", ephemeral=True)
        
        await interaction.response.send_message(f"Renaming ticket to {self.new_name.value}")

        await interaction.channel.edit(name=self.new_name.value)

        await interaction.edit_original_message(content=f"Renamed to {self.new_name.value}")

class Normal_tags(discord.ui.Modal):
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name
        super().__init__(timeout=None, title=f"New Tag: {self.name}")
    
    tag_content = ui.TextInput(label="Tag Content", placeholder="Enter content of tag", style=discord.TextStyle.paragraph, custom_id="TAG:CONTENT", required=True, max_length=2000)
    tag_description = ui.TextInput(label="Tag Description", placeholder="Enter description of tag", style=discord.TextStyle.short, custom_id="TAG:DESCRIPTION", required=True, max_length=30)

    async def on_submit(self, interaction: Interaction):
        data = {"_id": self.name, 'author': interaction.user.id, 'content': self.tag_content.value, 'description': self.tag_description.value, 'guildID': interaction.guild.id, 'type': 'normal'}

        commands = app_commands.Command(name=self.name.lower(),
                                        description=self.tag_description.value,
                                        callback=Normal_CallBack,
                                        guild_ids=[interaction.guild.id])
                                    
        self.bot.tree.add_command(commands)
        await interaction.response.send_message(f"Created tag {self.name}", ephemeral=True)
        await self.bot.tags.insert(data)
        self.bot.active_tag[self.name] = data

class Argument_tags(discord.ui.Modal):
    def __init__(self, bot, name):
        self.bot = bot
        self.name = name
        super().__init__(timeout=None, title=f"New Tag: {self.name}")
    
    tag_content = ui.TextInput(label="Tag Content", default="Exmaple: {member}, Make sure to follow the {channel}", style=discord.TextStyle.paragraph, custom_id="TAG:CONTENT", required=True, max_length=2000)
    tag_description = ui.TextInput(label="Tag Description", placeholder="Enter description of tag", style=discord.TextStyle.short, custom_id="TAG:DESCRIPTION", required=True, max_length=30)

    async def on_submit(self, interaction: Interaction):
        data = {"_id": self.name, 'author': interaction.user.id, 'content': self.tag_content.value, 'description': self.tag_description.value, 'guildID': interaction.guild.id, 'type': 'argument'}

        commands = app_commands.Command(name=self.name.lower(),description=self.tag_description.value,callback=Argument_CallBack,guild_ids=[interaction.guild.id],)
                                    
        self.bot.tree.add_command(commands)
        await interaction.response.send_message(f"Created tag {self.name}", ephemeral=True)
        await self.bot.tags.insert(data)
        self.bot.active_tag[self.name] = data

class Edit_Tag(discord.ui.Modal):
    def __init__(self, bot, tag_data):
        self.bot = bot
        self.tag_data = tag_data
        super().__init__(timeout=None, title=f"Edit Tag: {self.tag_data['_id']}")
        self.tag_content = ui.TextInput(label="Tag Content", default=self.tag_data['content'], style=discord.TextStyle.paragraph, custom_id="TAG:CONTENT", required=True, max_length=2000)
        self.tag_description = ui.TextInput(label="Tag Description", default=self.tag_data['description'], style=discord.TextStyle.short, custom_id="TAG:DESCRIPTION", required=True, max_length=30)    

    async def on_submit(self, interaction: discord.Interaction):
        self.tag_data['content'] = self.tag_content.value
        self.tag_data['description'] = self.tag_description.value
        await self.bot.tags.update(self.tag_data)
        await interaction.response.send_message(f"Edited tag {self.tag_data['_id']}\nMake sure to sync the tag with the bot", ephemeral=True)