from discord import app_commands
from discord.ext import commands
from utils.checks import Commands_Checks
from typing import Union, Optional, List
from discord.app_commands import Choice
import discord 

class Permission_slash(app_commands.Group, name="permission", description="Bot Commands Permission System"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name="permission", description="Bot Commands Permission System")

    async def command_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_command = [cmd for cmd in self.bot.perm]
        choice = [
            app_commands.Choice(name=cmd, value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]
        return(list(choice[:24]))

    @app_commands.command(name="check", description="Check permissions of role or user")
    @app_commands.describe(target='The member or role or to check')
    async def check(self, interaction: discord.Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.defer(thinking=True)
        cmd_data = await self.bot.perms.get_all()
        allowd_cmd = ""
        if isinstance(target, discord.Member):

            for cmd in cmd_data:
                if target.id in cmd['allowed_users']:
                    allowd_cmd += f"{cmd['_id']}\n"
        
        elif isinstance(target, discord.Role):

            for cmd in cmd_data:
                if target.id in cmd['allowed_roles']:
                    allowd_cmd += f"{cmd['_id']}\n"
        
        embed = discord.Embed(description=f"***Permission's  {target.mention}***",color=interaction.user.color)

        if allowd_cmd == "":
            allowd_cmd = "None"
        embed.add_field(name="Allowed Commands", value=allowd_cmd)

        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name='cmd')
    @app_commands.describe(command='check permissions of a command')
    @app_commands.autocomplete(command=command_auto)
    async def cmd_check(
        self, 
        interaction: discord.Interaction, 
        command: str,
    ):  
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to use this command",ephemeral=True)
        await interaction.response.defer(thinking=True)

        cmd_data = await self.bot.perms.find(command)

        if cmd_data is None:
            return await interaction.followup.send("Command not found",ephemeral=True)

        embed = discord.Embed(title=f"permission {command}",color=interaction.user.color)

        roles,users = [], []

        for role in cmd_data['allowed_roles']:
            roles.append(f"<@&{role}>")
        for user in cmd_data['allowed_users']:
            users.append(f"<@{user}>")

        if len(roles) == 0: 
            embed.add_field(name="Allowed roles", value="None")
        else: 
            embed.add_field(name="Allowed roles", value=", ".join(roles))
        
        if len(users) == 0:
            embed.add_field(name="Allowed users", value="None")
        else:
            embed.add_field(name="Allowed users", value=", ".join(users))

        embed.add_field(name="Disabed?:", value=cmd_data['disable'], inline=False)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="edit", description="Add a role/user to a command")
    @app_commands.describe(target='Role or User to add')
    @app_commands.describe(command='Command to add to')
    @app_commands.describe(type="add/remove")
    @app_commands.choices(type=[Choice(name="add", value="add"), Choice(name="remove", value="remove")])
    @app_commands.autocomplete(command=command_auto)
    async def edit(self, interaction: discord.Interaction, target: Union[discord.Role, discord.Member], command: str, type: Choice[str]):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permission to use this command",ephemeral=True)

        await interaction.response.defer(thinking=True)
        if command == "*":
            all_data = await self.bot.perms.get_all()
            for data in all_data:
                if type.value == "add":
                    if isinstance(target, discord.Member):
                        if target.id not in data['allowed_users']:
                            data['allowed_users'].append(target.id)
                    elif isinstance(target, discord.Role):
                        if target.id not in data['allowed_roles']:
                            data['allowed_roles'].append(target.id)
                elif type.value == "remove":
                    if isinstance(target, discord.Member):
                        if target.id in data['allowed_users']:
                            data['allowed_users'].remove(target.id)
                    elif isinstance(target, discord.Role):
                        if target.id in data['allowed_roles']:
                            data['allowed_roles'].remove(target.id)
                
                await self.bot.perms.update(data)
            if type.value == "add":
                return await interaction.followup.send(f"{target.mention} is now allowed to use all commands")
            elif type.value == "remove":
                return await interaction.followup.send(f"{target.mention} rmeoved from all commands")

        
        cmd_data = await self.bot.perms.find(command)
        if cmd_data is None:
            cmd_data = {"_id": command, "allowed_roles": [], "allowed_users": [], 'disable': False}
            await self.bot.perms.insert(cmd_data)
        
        if type.value == "add":
            if isinstance(target, discord.Role):
                if target.id in cmd_data['allowed_roles']:
                    return await interaction.followup.send("Role already allowed", ephemeral=True)
                cmd_data['allowed_roles'].append(target.id)
            else:
                if target.id in cmd_data['allowed_users']:
                    return await interaction.followup.send("User already allowed", ephemeral=True)
                cmd_data['allowed_users'].append(target.id)
            
            await interaction.followup.send(f"Added {target.name} to {command}")
            
        elif type.value == "remove":
            if isinstance(target, discord.Role):
                if target.id not in cmd_data['allowed_roles']:
                    return await interaction.followup.send("Role not allowed", ephemeral=True)
                cmd_data['allowed_roles'].remove(target.id)
            else:
                if target.id not in cmd_data['allowed_users']:
                    return await interaction.followup.send("User not allowed", ephemeral=True)
                cmd_data['allowed_users'].remove(target.id)

            await interaction.followup.send(f"Removed {target.name} from {command}")

        await self.bot.perms.update(cmd_data)
        self.bot.perm[cmd_data["_id"]] = cmd_data

class Permission(commands.Cog, name="Permission", description="Bot Commands Permission System"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(Permission_slash(self.bot), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
async def setup(bot):
    await bot.add_cog(Permission(bot))