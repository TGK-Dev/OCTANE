import datetime
import discord
import discord_slash

from discord.ext import commands

class Events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('The command is disabed by Owner')
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('Please Wait for last Game to End')
        elif isinstance(error, commands.CommandInvokeError):
            return
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            #raise error
            embed = discord.Embed(color=0xE74C3C, 
                description=f"<:dnd:840490624670892063> | Error: `{error}`")
            await ctx.send(embed=embed)
            #mess = await ctx.send_help(ctx.command, )

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Hey! You lack permission to use this command.")
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send("Hey! You lack permission to use this command.")
        else:
            embed = discord.Embed(color=0xE74C3C, 
                description=f"Error: `{error}`")
            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link','vote Link','Vote link', 'pls vote', 'pls Vote', 'Pls vote']

        if message.author.bot:
            return

        messageContent = message.content
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    return await message.reply('**Vote for us here**:\nhttps://top.gg/servers/785839283847954433/vote\n\n__**Voting Perks**__\n❥ Special "Voted" Role.\n❥ 2,500 Casino Cash. Collect using ,collectincome in #:game_die:。casino.\n❥ Access to Dank Memer Premium with 2x Amaari.\n❥ Guild wide 1x Amaari.', mention_author=False)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = self.bot.get_guild(797920317871357972)
        if after.guild.id != 785839283847954433:
            return
        if len(before.roles) < len(after.roles):
            guild = self.bot.get_guild(797920317871357972)
            # The user has gained a new role, so lets find out which one
            newRole = next(role for role in after.roles if role not in before.roles)

            if newRole.id == 786477872029892639:
                channel = self.bot.get_channel(838041413320835072)
                embed = discord.Embed(title="New Booster",
                description=f"{after.mention} Just Boosted The Server Yeye!\nThank you so much for the Boosting our lovely Server",color=0xff73fa)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if guild.id != 785839283847954433:
            return
        logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        channel = self.bot.get_channel(806107399005667349)
        logs = logs[0]
        if logs.target == member:
            embed = discord.Embed(title="Case Ban",
                description=f"**>**Moderator:`{logs.user}`\n**>**Offender: `{logs.target}`\n**>**Reason: `{logs.reason}`",color=0xE74C3C)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        if guild.id != 785839283847954433:
            return
        log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
        channel = self.bot.get_channel(806107399005667349)
        logs = log[0]
        if logs.target == member:
            embed = discord.Embed(title="Case UnBan",
                description=f"**>**Moderator:`{logs.user}`\n**>**Offender: `{logs.target}`\n**>**Reason: `{logs.reason}`",color=0x2ECC71)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild.id 
        guild = self.bot.get_guild(785839283847954433)
        channel =  self.bot.get_channel(837285329610080276)
        robot = discord.utils.get(guild.roles, id=810153515610537994)
        count = guild.member_count
        ping = discord.utils.get(guild.roles, id=810400876657115166)
        unverified = discord.utils.get(guild.roles, id=843399308408782868)
        level = discord.utils.get(guild.roles, id=810132828250832948)
        game = discord.utils.get(guild.roles, id=810135369177759774)
        dono = discord.utils.get(guild.roles, id=810134737829888050)
        special = discord.utils.get(guild.roles, id=810134311163920404)
    
        if member.guild.id == 785839283847954433:
    
            embed = discord.Embed(title=f'**WELCOME TO TGK, {member.display_name}!**',
                description=f"\n\n:sparkles: Get your favorite roles from <#785882615202316298>,\nand say _Hello_ to everyone in <#785847439579676672> !\n\n**To access Dank Memer, react in <#801394407521517578>.**\n\n:circus_tent: Also check out other fun game bots on the server:\n✦ <#802195590208421908> ✦ <#786117471840895016> ✦ <#807124148165804035> ✦ <#835810935184293928> ✦\n\nMake sure you follow the <#785841560918163501> of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from <#785901543349551104>.\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len([m for m in guild.members if m.bot])}",
                color=0x000000)
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(f"{member.mention}", embed=embed)
            await member.add_roles(ping)
            await member.add_roles(unverified)
            await member.add_roles(level)
            await member.add_roles(game)
            await member.add_roles(dono)
            await member.add_roles(special)
            try:
                await member.send(embed=embed)
            except discord.HTTPException:
                pass
    
        else:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        echannel = self.bot.get_channel(payload.channel_id)
        message = await echannel.fetch_message(payload.message_id)
        guild = await self.bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        

        if message.id == 843398585856557068:

        	if payload.emoji.name == "success_tick":

        		unverified = discord.utils.get(guild.roles, id=843399308408782868)
        		newbiw = discord.utils.get(guild.roles, id=787566421592899614)

        		await member.remove_roles(unverified,)
        		await member.add_roles(newbiw,)

        	else:
        		return
        else:
        	return

    @commands.command(name="joint", hidden=True)
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def joint(self, ctx):
        embed = discord.Embed(title=f'**WELCOME TO TGK, {ctx.author.display_name}!**',
            description=f"\n\n:sparkles: Get your favorite roles from [Self Roles](https://discord.gg/6WmKQZrKD9),\nand say _Hello_ to everyone in [Chat](https://discord.gg/B2FDCggkES) !\n\n**To access Dank Memer, react in [Dank Bifrost](https://discord.gg/BUtTb7FVxJ).**\n\n:circus_tent: Also check out other fun game bots on the server:\n✦ [Pokemon](https://discord.gg/6dGkammu6P)  ✦ [Casino](https://discord.gg/f4YzaVyhRE)  ✦[Akinator](https://discord.gg/HyVgTrF2E5)  ✦ [Mudae](https://discord.gg/u2XJ8SaY) ✦\n\nMake sure you follow the [Rules](https://discord.gg/Z4rbTcvDyb) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [Server Support](https://discord.gg/gJhmaFJmra).\n\nHave fun!\n\n__Server Member Count:__ {ctx.author.guild.member_count}",
            color=0x2ECC71)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))