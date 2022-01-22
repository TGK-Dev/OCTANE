from discord.ext import commands

class checks():
    
    def is_me():
        def predicate(ctx):
            return ctx.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def can_use():
        async def predicate(ctx):
            command = await ctx.bot.active_cmd.find(ctx.command.name)
            if command['disable'] == True:
                await ctx.send("Command is disabled by Jay/Utki")
                return False

            if ctx.author.id in [488614633670967307, 301657045248114690]: return True

            user_roles = [role.id for role in ctx.author.roles]
            if ctx.author.id in command['allowed_users']: return True

            if (set(user_roles) & set(command['allowed_roles'])):
                return True
            else:
                return False
                
        return commands.check(predicate)