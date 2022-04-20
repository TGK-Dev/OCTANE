from discord import app_commands
from discord.ext import commands
from utils.checks import Commands_Checks
from typing import Union, Optional, List
import discord 


class Permission_slash(app_commands.Group, name="permission", description="Bot Commands Permission System"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name="permission", description="Bot Commands Permission System")

    async def command_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_command = [cmd.name for cmd in self.bot.commands]
        choice = [
            app_commands.Choice(name=cmd , value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]
        if len(choice) == 0:
            current_command = [cmd.name for cmd in self.bot.tree.get_commands(guild=interaction.guild)]
            for cmd in current_command:
                choice.append(app_commands.Choice(name=cmd, value=cmd))
        return(choice[:24])


    @app_commands.command(name="check", description="Check permissions of role or user")
    @app_commands.describe(target='The member or role or to check')
    async def check(self, interaction: discord.Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.send_message("Checking permissions of {}".format(target.name))
    
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

class Permission(commands.Cog, name="Permission", description="Bot Commands Permission System"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(Permission_slash(self.bot), guild=discord.Object(964377652813234206))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
async def setup(bot):
    await bot.add_cog(Permission(bot))