from discord import app_commands
from discord import Interaction
from discord.ext import commands
import discord

class CommandDisableByDev(commands.CommandError):
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

