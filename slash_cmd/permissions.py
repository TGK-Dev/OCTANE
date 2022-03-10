from discord import app_commands
import discord
from typing import Union, Optional, List

class Permissions(app_commands.Group):
    def __init__(self, bot, name: str = "permissons", parent=None):
        super().__init__(name=name, parent=parent)
        self.bot = bot


    @app_commands.command(name="check", description="Check permissions of role or user")
    @app_commands.describe(target='The member or role or to check')
    async def check(self, interaction: discord.Interaction, target: Union[discord.Member, discord.Role]):

        cmd_data = await self.bot.active_cmd.get_all()
        embed = discord.Embed(description=f"***Permission's  {target.mention}***",color=interaction.user.color)
        allowed_list = " "
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)
        if isinstance(target, discord.Member):
            for cmd in cmd_data:
                if target.id in cmd['allowed_users']: 
                    allowed_list += f"{cmd['_id']}, "
            
            if allowed_list != " ":
                embed.add_field(name="Allowed commands", value=allowed_list)
            else:
                embed.add_field(name="Allowed commands", value="None")

            await interaction.response.send_message(embed=embed)
            
        if isinstance(target, discord.Role):

            for cmd in cmd_data:
                if target.id in cmd['allowed_users']: 
                    allowed_list += f"{cmd['_id']}, "
            
            if allowed_list != " ":
                embed.add_field(name="Allowed commands", value=allowed_list)
            else:
                embed.add_field(name="Allowed commands", value="None")

            await interaction.response.send_message(embed=embed)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='cmd')
    @app_commands.describe(command='check permissions of a command')
    async def cmd_check(
        self, 
        interaction: discord.Interaction, 
        command: str,
    ):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to use this command",ephemeral=True)
        command = self.bot.get_command(command)

        if command is None: return await interaction.response.send_message("I can't find a command with that name!")

        cmd_data = await self.bot.active_cmd.find(command.name)
        if not cmd_data:return await interaction.response.send_message("NO data found")

        embed = discord.Embed(title=f"permission {command.name}",color=interaction.user.color)

        roles,users = [], []

        for role in cmd_data['allowed_roles']: 
            roles.append(f"<@&{role}>")
        if len(roles) == 0: 
            embed.add_field(name="Allowed roles", value="None")
        else: 
            embed.add_field(name="Allowed roles", value=", ".join(roles))

        embed.add_field(name="Disabed?:", value=cmd_data['disable'], inline=False)
        await interaction.response.send_message(embed=embed)

    @cmd_check.autocomplete('command')
    async def command_auto(self, interaction: discord.Interaction, current: str, namespace:app_commands.Namespace) -> List[app_commands.Choice[str]]:
        current_command = [cmd.name for cmd in self.bot.commands]
        choice = [
            app_commands.Choice(name=cmd , value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]

        return(choice[:24])

    async def on_error(self, interaction: discord.Interaction, command, error):
        pass