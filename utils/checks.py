from discord.ext import commands

class checks():
    
    def is_me():
        def predicate(ctx):
            return ctx.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def can_use():
        async def predicate(ctx):
            if ctx.author.id in [488614633670967307, 301657045248114690]: return True
            command = await ctx.bot.active_cmd.find_by_custom({'command_name': ctx.command.name})
            if not command: return await ctx.send("Error Happend Report to Jay")
            if command['disable'] == True: return await ctx.send("Command is disabled by Jay/Utki")
            user_roles = [role.id for role in ctx.author.roles]
            if ctx.author.id in command['allowed_users']: return True
            if (set(user_roles) & set(command['allowed_roles'])):
                return True
            else:
                return False
        return commands.check(predicate)