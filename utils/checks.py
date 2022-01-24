from discord.ext import commands
import nextcord

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
            command = await ctx.bot.active_cmd.find(ctx.command.name)
            
            if command['disable'] == True:
                raise CommandDisableByDev(ctx.message)
                
            if ctx.author.id in [488614633670967307, 301657045248114690]: return True

            user_roles = [role.id for role in ctx.author.roles]
            #if ctx.author.id in command['allowed_users']: return True

            if (set(user_roles) & set(command['allowed_roles'])):
                return True
            else:
                return False
                
        return commands.check(predicate)