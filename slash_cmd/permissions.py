from discord import app_commands
import discord
from typing import Union, Optional, List
from discord.app_commands import Choice
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
                if target.id in cmd['allowed_roles']:
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

    @app_commands.command(name="edit", description="Edit permissions of a command")
    @app_commands.describe(command='command you want to edit')
    @app_commands.describe(target="role or user")
    @app_commands.describe(choice="Action you want to do")
    @app_commands.choices(choice=[
        Choice(name="Add", value=1),
        Choice(name="Remove", value=2),
        Choice(name="Disable", value=3)
    ])
    async def edit(
        self, 
        interaction: discord.Interaction, 
        command: str, 
        target: Union[discord.Member, discord.Role], 
        choice: Choice[int]
    ):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to use this command",ephemeral=True)
            
        command = self.bot.get_command(command)

        if command is None: return await interaction.response.send_message("I can't find a command with that name!")

        await interaction.response.defer(thinking=True)
        cmd_data = await self.bot.active_cmd.find(command.name)

        if not cmd_data:
            cmd_data = {"_id": command.name, "allowed_roles": [], "allowed_users": [], "disable": False}
            
        if choice.value == 1:

            if isinstance(target, discord.Role):
                if target.id in cmd_data['allowed_roles']:
                    return await interaction.followup.send("This role is already allowed")
                else:
                    cmd_data['allowed_roles'].append(target.id)
                    await self.bot.active_cmd.update(cmd_data)
                    await interaction.followup.send(f"Added {target.mention} to allowed roles", allowed_mentions=discord.AllowedMentions(roles=False))

            if isinstance(target, discord.Member):
                if target.id in cmd_data['allowed_users']:
                    return await interaction.followup.send("This user is already allowed")
                else:
                    cmd_data['allowed_users'].append(target.id)
                    await self.bot.active_cmd.update(cmd_data)
                    await interaction.followup.send(f"Added {target.mention} to allowed users", allowed_mentions=discord.AllowedMentions(users=False))

        if choice.value == 2:

            if isinstance(target, discord.Role):
                if target.id not in cmd_data['allowed_roles']:
                    return await interaction.followup.send("This role is not allowed")
                else:
                    cmd_data['allowed_roles'].remove(target.id)
                    await self.bot.active_cmd.update(cmd_data)
                    await interaction.followup.send(f"Removed {target.mention} from allowed roles", allowed_mentions=discord.AllowedMentions(roles=False, users=False))
            
            if isinstance(target, discord.Member):
                if target.id not in cmd_data['allowed_users']:
                    return await interaction.followup.send("This user is not allowed")
                else:
                    cmd_data['allowed_users'].remove(target.id)
                    await self.bot.active_cmd.update(cmd_data)
                    await interaction.followup.send(f"Removed {target.mention} from allowed users", allowed_mentions=discord.AllowedMentions(roles=False, users=False))

        if choice.value == 3:

            if cmd_data['disable'] == True:
                return await interaction.response.send_message("This command is already disabled")
            else:
                cmd_data['disable'] = True
                await self.bot.active_cmd.update(cmd_data)
                await interaction.followup.send("This command is disabled")
        
        self.bot.perm[command.name] = cmd_data
        

    @edit.autocomplete('command')
    async def command_auto(self, interaction: discord.Interaction, current: str, namespace:app_commands.Namespace) -> List[app_commands.Choice[str]]:
        current_command = [cmd.name for cmd in self.bot.commands]
        choice = [
            app_commands.Choice(name=cmd , value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]

        return(choice[:24])

    # async def on_error(self, interaction: discord.Interaction, command, error):
    #     return await interaction.response.send_message("An error occured", ephemeral=True)