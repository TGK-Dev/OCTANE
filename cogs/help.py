import discord
from utils.checks import checks
from discord.ext import commands
from discord import app_commands
from typing import Union, List

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_tree_commands()
    
    def load_tree_commands(self):

        @app_commands.command(name="help", description="Show help Command for selected command")
        @app_commands.describe(command="Enter a Command name")
        async def help(interaction, command: str = None):
            command = self.bot.get_command(command)
            if command is None:
                return await interaction.response.send_message("I can't find a command with that name!", ephemeral=True)
            
            embed = discord.Embed(color=0x00ff00)
            embed.add_field(name=f"Help: {command.name}", value=f"```\n{command.description}\n```",inline=False)
            embed.add_field(name="Usage:", value=f"```\n>{command.name} {command.usage}\n```", inline=False)
            aliases = ", ".join(command.aliases)
            if command.aliases:
                embed.add_field(name="Aliases:", value=f"```\n{aliases}\n```", inline=False)
            
            if type(command) is commands.Group:
                embed.add_field(name="Subcommands:", value=f"```\n{', '.join(cmd.name for cmd in command.commands)}```", inline=False)

            await interaction.response.send_message(embed=embed)

        @help.autocomplete('command')
        async def help_autocomplete(interaction: discord.Interaction, current: str, namespace:app_commands.Namespace) -> List[app_commands.Choice[str]]:
            command = []
            for cmd in self.bot.commands:

                can_use = checks.help_ckeck(self.bot, cmd, interaction)
                if can_use == True:
                    command.append(cmd.name)
            
            choice = [
                app_commands.Choice(name=cmd , value=cmd)
            for cmd in command if current.lower() in cmd.lower()
            ]

            return(choice[:24])
        
        self.bot.slash_commands.append(help)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded-----')

def setup(bot):
    bot.add_cog(Help(bot))
