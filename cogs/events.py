import datetime
import discord
from discord import app_commands
from utils.checks import CommandDisableByDev
from discord.ext import commands, tasks
from utils.Slash_check import DisableByDev

class vote_button(discord.ui.View):
    def __init__(self, guild: int):
        super().__init__()
        url = f"https://top.gg/servers/785839283847954433/vote"
        self.add_item(discord.ui.Button(label='Click Here', url=url))

class verify(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot =  bot
        self.guild = self.bot.get_guild(785839283847954433)
        self.role = discord.utils.get(self.guild.roles, id=953006119436030054)
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify", emoji="<:YES_TICK:957348921120792717>")
    async def verify(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.role in interaction.user.roles:
            await interaction.response.send_message("Verified", ephemeral=True)
            await interaction.user.remove_roles(self.role)
        else:
            await interaction.response.send_message("You are already verified, create ticket from <#785901543349551104>", ephemeral=True)

class Events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.update_task = self.check_update_task.start()
        self.slash_error_handle()
    
    def slash_error_handle(self):
        tree = self.bot.tree

        @tree.error
        async def on_app_command_error(interaction: discord.Interaction, command, error):
            if isinstance(error ,app_commands.CommandOnCooldown):
                m, s = divmod(error.retry_after, 60)
                h, m = divmod(m, 60)
                if int(h) == 0 and int(m) == 0:
                    await interaction.response.send_message(f" You must wait {int(s)} seconds to use this command!", ephemeral=True)
                elif int(h) == 0 and int(m) != 0:
                    await interaction.response.send_message(
                        f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!", ephemeral=True
                    )
            elif isinstance(error, app_commands.CheckFailure):
                await interaction.response.send_message("Hey, You can't use this command!", ephemeral=True)
            
            elif isinstance(error, DisableByDev):
                await interaction.response.send_message("Command Disabled by Developer", ephemeral=True)
            else:
                embed = discord.Embed(color=0xE74C3C,
                    description=f"<:dnd:840490624670892063> | Error: `{error}`")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(seconds=900)
    async def check_update_task(self):

        self.bot.blacklist_users = []
        current_blacklist_user = await self.bot.config.find(785839283847954433)
        for blacklisted_user in current_blacklist_user['blacklist']:
            self.bot.blacklist_users.append(blacklisted_user)

        self.bot.afk_user = {}
        current_afk_user = await self.bot.afk.get_all()
        for afk in current_afk_user:
            self.bot.afk_user[afk["_id"]] = afk
        
        current_banned_user = await self.bot.bans.get_all()
        for banned_user in current_banned_user:
            self.bot.current_ban[banned_user["_id"]] = banned_user
        
        votes = await self.bot.votes.get_all()
        for vote in votes:
            self.bot.current_vote[vote["_id"]] = vote
        
        perm = await self.bot.active_cmd.get_all()
        for p in perm:
            self.bot.perm[p["_id"]] = p

    @check_update_task.before_loop
    async def before_check_current_free(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        self.bot.add_view(verify(self.bot))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.owner.id in [self.bot.user.id, 301657045248114690, 488614633670967307]:
            pass
        else:
            await guild.leave()
    @commands.command()
    async def verify(self, ctx):
        embed = discord.Embed(title="Verification", description="Click the button below to verify your Self", color=0xffffff)
        await ctx.send(embed=embed, view=verify(self.bot))

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
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('The command is disabed by Jay/Utki')
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send('Please Wait for last Game to End')
        elif isinstance(error, CommandDisableByDev):
            await ctx.send('The command is disabed by Jay/Utki')
        elif isinstance(error, commands.CommandInvokeError):
            return
        elif isinstance(error, commands.CommandNotFound):
            data_filter = ctx.message.content.replace('>', '')
            embed_filter = {'Key_name': data_filter}
            embed_data = await self.bot.embeds.find_by_custom(embed_filter)
            if embed_data is None: return
            await ctx.message.delete()
            embed = embed_data['embed']
            button = embed_data['buttons']    
            if len(button) > 0:
                view = discord.ui.View()
                for i in button:
                    view.add_item(discord.ui.Button(label=i['name'], url=i['url']))
                await ctx.send(embed=discord.Embed().from_dict(embed), view=view)
            else:
                await ctx.send(embed=discord.Embed().from_dict(embed))
        elif isinstance(error, app_commands.CommandAlreadyRegistered):
            pass
        else:
            #raise error
            embed = discord.Embed(color=0xE74C3C,
                                  description=f"<:dnd:840490624670892063> | Error: `{error}`")
            await ctx.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        word_list = ['vote link','how to get vote role', 'how to vote', 'pls vote', 'how to vote for server', 'link to vote']
        if message.author.bot:
            return

        messageContent = message.content.lower()
        flag = 0
        if len(messageContent) > 0:
            for word in word_list:
                if word in messageContent:
                    flag = 1
                    guild = message.guild.id
                    return await message.reply(f"__**Voting Perks**__\n"
                        f"❥ Special <@&786884615192313866> Role with 1x guild-wide multi.\n"
                        f"❥ 1x extra entry into all frisky giveaways.\n"
                        f"❥ 2,500 Casino Cash. Collect using ,collectincome in <#786117471840895016>.\n"
                        f"❥ Access to <#929613393097293874> with 2x Amaari\n"
                        , mention_author=False, view=vote_button(guild), allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

            
            channel_ids = [785847439579676672, 799364834927968336, 799378297855279125, 935763990670348309]
            immune_users = [301657045248114690, 488614633670967307, 562738920031256576, 413651113485533194, 928126608852811848, 690118001369808921, 457839031909351425, 651711446081601545]
            
            if "vote" in messageContent and flag ==0 and message.channel.id in channel_ids and message.author.id not in immune_users:
                guild = message.guild.id
                return await message.reply(f"__**Voting Perks**__\n"
                        f"❥ Special <@&786884615192313866> Role with 1x guild-wide multi.\n"
                        f"❥ 1x extra entry into all frisky giveaways.\n"
                        f"❥ 2,500 Casino Cash. Collect using ,collectincome in <#786117471840895016>.\n"
                        f"❥ Access to <#929613393097293874> with 2x Amaari\n"
                        , mention_author=False, view=vote_button(guild), allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False),delete_after=5)

            for word in ['heist']:
                if word in messageContent and message.channel.id in channel_ids and message.author.id not in immune_users:
                    return await message.reply('Keep an 👁️ on <#960535386768166992> for heist related requirements/updates.', delete_after=3, mention_author=False)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
 
        if member.guild.id != 785839283847954433: return
        if member.bot: return
        data = self.bot.config_data[member.guild.id]['welcome']
        if data is None: return

        channel = self.bot.get_channel(data)
        robot = discord.utils.get(guild.roles, id=810153515610537994)
        count = guild.member_count
        ping = discord.utils.get(guild.roles, id=810400876657115166)
        level = discord.utils.get(guild.roles, id=810132828250832948)
        game = discord.utils.get(guild.roles, id=810135369177759774)
        dono = discord.utils.get(guild.roles, id=810134737829888050)
        special = discord.utils.get(guild.roles, id=810134311163920404)
        
        await member.add_roles(ping)
        await member.add_roles(level)
        await member.add_roles(game)
        await member.add_roles(dono)
        await member.add_roles(special)

        embed = discord.Embed(title=f'**WELCOME TO TGK, {member.display_name}!**',
                              description=f"\n\nGet your favorite roles from [self-roles](https://discord.gg/58bc5QWE4q),\nand say _Hello_ to everyone in [chat](https://discord.gg/yEPYYDZ3dD)!\n\nAlso check out other fun game bots on the server:\n✦ [Casino](https://discord.gg/DJycdCqnqt) ✦ [Mudae](https://discord.gg/ujCHVRctHY) ✦ [Akinator](https://discord.gg/fzDTdGZFh6) ✦ [Pokemon](https://discord.gg/DpJ4mAUC9m)\n\nMake sure you follow the [rules](https://discord.gg/NmD4JGCaNc) of the house for a good time here. Also, check out rules and instructions of game bots in respective channels.\n\n:love_letter: To get in touch with staff, simply raise a ticket from [support](https://discord.gg/T8VWyvDfeB).\n\nHave fun!\n\n__Server Member Count:__ {guild.member_count - len([m for m in guild.members if m.bot])}",
                              color=0x000000)
                              
        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url or None)
        else:
            embed.set_thumbnail(url=member.default_avatar)
        await channel.send(f"{member.mention}", embed=embed)


        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        if guild.id != 785839283847954433: return
        logs = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban)]
        logs = logs[0]

        if logs.user.id == 816699167824281621:
            return
        if logs.target != member: return

        data = await self.bot.config.find(guild.id)
        if data is None:
            return
        if logs.reason is None:
            logs.reason = "None"
        log_channel = self.bot.get_channel(855784930494775296)
        log_embed = discord.Embed(title=f"🔨 Ban | Case ID: {data['case']}",
                                    description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0xE74C3C)
        if member.avatar != None:
            log_embed.set_thumbnail(url=member.avatar.url)
        else:
            log_embed.set_thumbnail(url=member.default_avatar)
        log_embed.timestamp = datetime.datetime.utcnow()
        log_embed.set_footer(text=f"ID: {member.id}")

        await log_channel.send(embed=log_embed)

        data["case"] += 1
        await self.bot.config.upsert(data)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        if guild.id != 785839283847954433: return
        log = [log async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban)]
        logs = log[0]
        data = await self.bot.config.find(guild.id)

        if logs.user.id == 816699167824281621:
            return
        if logs.target == member:
            data = await self.bot.config.find(guild.id)
            if data is None:
                return
            if logs.reason is None:
                logs.reason = "None"
            log_channel = self.bot.get_channel(855784930494775296)
            log_embed = discord.Embed(title=f"🔓 UnBan | Case ID: {data['case']}",
                                      description=f" **Offender**: {logs.target.name} | {logs.target.mention} \n**Reason**: {logs.reason}\n **Moderator**: {logs.user.name} {logs.user.mention}", color=0x2ECC71)

            if member.avatar != None:
                log_embed.set_thumbnail(url=member.avatar.url)
            else:
                log_embed.set_thumbnail(url=member.default_avatar)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.set_footer(text=f"ID: {member.id}")

            await log_channel.send(embed=log_embed)

            data["case"] += 1
            await self.bot.config.upsert(data)

async def setup(bot):
    await bot.add_cog(Events(bot))
