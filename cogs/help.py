import discord
from utils.checks import checks
from discord.ext import commands
from discord import app_commands
from typing import Union, List, Optional

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def command_auto(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        current_command = [cmd.name for cmd in self.bot.commands]
        choice = [
            app_commands.Choice(name=cmd , value=cmd)
            for cmd in current_command if current.lower() in cmd.lower()
        ]

        return(choice[:24])

    @app_commands.command(name="help", description="Help command")
    @app_commands.describe(command="help")
    @app_commands.autocomplete(command=command_auto)
    @app_commands.guilds(discord.Object(785839283847954433))
    async def help(self, interaction: discord.Interaction, command: str):

        command = self.bot.get_command(command)
        manul_check = checks.ManualCheck(self.bot, command.name, interaction)

        if manul_check == False:
            return await interaction.response.send_message("You don't have permission to use this command", ephemeral=True)

        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name=f"Help: {command.name}", value=f"```\n{command.description}\n```",inline=False)
        embed.add_field(name="Usage:", value=f"```\n>{command.name} {command.usage}\n```", inline=False)
        aliases = ", ".join(command.aliases)
        if command.aliases:
            embed.add_field(name="Aliases:", value=f"```\n{aliases}\n```", inline=False)
        
        if type(command) is commands.Group:
            embed.add_field(name="Subcommands:", value=f"```\n{', '.join(cmd.name for cmd in command.commands)}```", inline=False)

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded-----')

async def setup(bot):
    await bot.add_cog(Help(bot))
