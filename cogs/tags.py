import discord 
from discord import app_commands
from discord.ext import commands
from typing import Union, Optional, List, Literal
from ui.models import Normal_tags, Argument_tags, Edit_Tag
from utils.paginator import Paginator
from utils.callbacks import Normal_CallBack , Argument_CallBack
class TagSlash(app_commands.Group, name="tag", description="Tag commands module"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='tag')
    
    async def command_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_command = [cmd['_id'] for cmd in await self.bot.tags.get_all() if cmd['guildID']== interaction.guild.id]
        choice = [
            app_commands.Choice(name=cmd, value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]
        return(list(choice[:24]))
    
    @app_commands.command(name="create", description="Create a tag")
    @app_commands.describe(name="Tag name")
    @app_commands.default_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction, name:str, type: Literal['Normal Tag', 'Argument Tag']):
        if type == 'Normal Tag':
            await interaction.response.send_modal(Normal_tags(self.bot, name))
        elif type == 'Argument Tag':
            await interaction.response.send_modal(Argument_tags(self.bot, name))

    @app_commands.command(name="delete", description="Delete a tag")
    @app_commands.describe(name="Tag name")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(name=command_auto)
    async def delete(self, interaction: discord.Interaction, name:str):
        await interaction.response.send_message(f"Deleting tag {name}")
        await self.bot.tags.delete(name)
        for commnads in self.bot.tree.get_commands(guild=interaction.guild):
            if commnads.name == name:
                command = commnads
                self.bot.tree.remove_command(command)
                await interaction.edit_original_message(content=f"Tag {name} deleted, remeber to use /tag sync to update the bot")
                self.bot.active_tag.remove(name)
                return
        
        await interaction.edit_original_message(content=f"Error: Tag {name} not found")        
            

    @app_commands.command(name="sync", description="sync tags")
    #@app_commands.checks.Cooldown(1, 300)
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(name=command_auto)
    async def sync(self, interaction: discord.Interaction, name:str=None):

        if not name:
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.response.send_message("Synced", ephemeral=True)

        elif name:
            await interaction.response.send_message(f"Syncing tag {name}")
            data = await self.bot.tags.find(name)
            if data:
                command = app_commands.Command(
                    name=data['_id'],
                    description=data['description'],
                    callback=Normal_CallBack if data['type'] == 'Normal Tag' else Argument_CallBack
                )
                self.bot.tree.add_command(command)
                self.bot.active_tags[data['_id']] = data
                await interaction.edit_original_message(content=f"Synced tag {name}", ephemeral=True)
            else:
                await interaction.edit_original_message(content=f"Error: Tag Data not found", ephemeral=True)
    
    @app_commands.command(name="list", description="List all tags")
    @app_commands.default_permissions(administrator=True)
    async def list(self, interaction: discord.Interaction):
        tags = []
        for key, value in self.bot.active_tag.items():
            if int(value['guildID']) == interaction.guild.id:
                tags.append(value)
        
        if tags:
            pages = []
            for tag in tags:
                embed = discord.Embed(title=f"Tag: {tag['_id']}", description=f"```\n{tag['content']}\n```\n", color=discord.Color.blue())
                embed.add_field(name="Created by", value=f"<@{tag['author']}>", inline=False)
                pages.append(embed)
            
            await Paginator(interaction, pages).start(embeded=True, quick_navigation=False)

    @app_commands.command(name="edit", description="Edit a tag")
    @app_commands.describe(name="Tag name")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(name=command_auto)
    async def edit(self, interaction: discord.Interaction, name:str):
        tag_data = await self.bot.tags.find(name)
        if tag_data:
            await interaction.response.send_modal(Edit_Tag(self.bot, interaction, tag_data))

class Tag(commands.Cog, description="Tag commands."):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(TagSlash(self.bot), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

async def setup(bot):
    await bot.add_cog(Tag(bot))
