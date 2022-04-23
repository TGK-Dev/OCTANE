from discord import app_commands
from discord import Interaction
from discord.ext import commands
import discord

class CommandDisableByDev(commands.CommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

class CommandDisableByDev_Slash(app_commands.AppCommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

class Commands_Checks():

    def is_owner():
        def predicate(ctx):
            return ctx.author.id == ctx.guild.owner.id
        return commands.check(predicate)
    
    def is_me():
        def predicate(ctx):
            return ctx.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)
    
    def can_use():
        async def predicate(ctx):
            try:
                command = ctx.bot.perm[ctx.command.name]
            except KeyError:
                command = {"_id": ctx.command.name, "allowed_roles": [], 'allowed_users': [],"disable": False}
            
            if command['disable'] == True:
                raise CommandDisableByDev(ctx.message)
            
            if ctx.author.id in [488614633670967307, 301657045248114690]: return True

            user_roles = [role.id for role in ctx.author.roles]

            if ctx.author.id in command['allowed_users']:
                return True
            else:
                pass

            if (set(user_roles) & set(command['allowed_roles'])):
                return True
            else:
                return False
                
        return commands.check(predicate)

    def slash_check():
        async def predicate(interaction: discord.Interaction):
            slash_command = interaction.command
            try:
                command_data = interaction.client.perm[slash_command.name]

            except KeyError:
                command_data = {"_id": slash_command.name, "allowed_roles": [], 'allowed_users': [],"disable": False}
                await interaction.client.perms.insert(command_data)
            
            if command_data['disable'] == True:
                raise CommandDisableByDev_Slash(interaction)
            
            if interaction.user.id in [488614633670967307, 301657045248114690]: return True

            user_roles = [role.id for role in interaction.user.roles]

            if interaction.user.id in command_data['allowed_users']:
                return True
            
            if (set(user_roles) & set(command_data['allowed_roles'])):
                return True
            else:
                if interaction.user.guild_permissions.administrator:
                    return True
                return False
            
        return app_commands.check(predicate)

class Dynamic_cooldown():

    def is_me(interaction: discord.Interaction):
        if interaction.user.id in [488614633670967307, 301657045248114690]:
            return None
        return app_commands.Cooldown(1, 300)