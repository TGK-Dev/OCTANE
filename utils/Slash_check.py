import discord
from discord import Interaction
from discord import app_commands
from typing import Optional
class DisableByDev(app_commands.AppCommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

def is_me(interaction: Interaction):
    return interaction.user.id in [488614633670967307, 301657045248114690]

def can_use_slash(interaction: Interaction):
    try:
        cmd = interaction.client.perm[interaction.command.name]
    except KeyError:
        cmd = {"_id": interaction.command.name, "allowed_roles": [], 'allowed_users': [],"disable": False}
    
    if cmd['disable'] == True:
        raise DisableByDev(interaction)
    
    user_roles = [role.id for role in interaction.user.roles]
    if interaction.user.id in cmd['allowed_users'] or (set(user_roles) & set(cmd['allowed_roles'])): 
        return True
    else:
        return False

def can_bypass_cd(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    if interaction.user.id in [488614633670967307, 301657045248114690]:
        return None
    return app_commands.Cooldown(3, 60)
