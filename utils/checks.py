from discord.ext import commands
import discord

class CommandDisableByDev(commands.CommandError):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

class checks():

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
    
    async def slash_check(bot, interaction: discord.Interaction,command):
        try:
            command = bot.perm[command]
        except KeyError:
            command = {"_id": command, "allowed_roles": [], 'allowed_users': [],"disable": False}

        if interaction.user.id in [488614633670967307, 301657045248114690]: return True

        user_roles = [role.id for role in interaction.user.roles]

        if (set(user_roles) & set(command['allowed_roles'])):
            return True
        else:
            return False