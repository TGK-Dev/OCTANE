import datetime
import discord
import re
from discord import Webhook
import aiohttp

from humanfriendly import format_timespan
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext import tasks
from utils.checks import checks
from discord import app_commands
from typing import Union
from utils.Slash_check import can_use_slash

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

description = "Moderation commands"

class roles(discord.ui.View):
    def __init__(self, bot, user: discord.Member):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
    
    @discord.ui.button(label="Show Roles", style=discord.ButtonStyle.blurple)
    async def roles(self,interaction: discord.Interaction, button: discord.ui.Button):
        hsorted_roles = sorted([role for role in self.user.roles[1:]], key=lambda x: x.position)
        embed = discord.Embed(description=", ".join(role.mention for role in hsorted_roles),color=self.user.color)
        embed.add_field(name="Total Roles", value=len(self.user.roles))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Permissions", style=discord.ButtonStyle.blurple)
    async def perms(self,interaction: discord.Interaction, button: discord.ui.Button):
        perm = ", ".join([str(p[0]).replace("_", " ").title() for p in self.user.guild_permissions if p[1]])
        embed = discord.Embed(description=f"`{perm}`", color=self.user.color)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction):
        if interaction.user.guild_permissions.manage_messages:
            return True
        else:
            return False

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)

def is_me(interaction: discord.Interaction):
    return interaction.user.id in [488614633670967307, 301657045248114690]


class v2Moderation(commands.Cog, description=description, command_attrs=dict(hidden=False)):
    def __init__(self, bot):
        self.bot = bot
        self.ban_task = self.check_current_bans.start()
        self.load_tree_commands()

    def load_tree_commands(self):
        
        @app_commands.context_menu(name="Whois")
        @app_commands.check(is_me)
        @app_commands.guilds(discord.Object(785839283847954433))
        async def whois(interaction: discord.Interaction, member: Union[discord.Member, discord.User]):
            usercolor = member.color

            embed = discord.Embed(title=f'{member.name}', color=usercolor)

            if member.avatar != None:
                embed.set_thumbnail(url=member.avatar.url or None)
                embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar.url)
            else:
                embed.set_thumbnail(url=member.default_avatar)
                embed.set_footer(text=f'ID {member.id}', icon_url=member.default_avatar)

            embed.add_field(name='Account Name:',
                            value=f'{member.name}', inline=False)
            embed.add_field(
                name='Created at:', value=f"<t:{round(member.created_at.timestamp())}:R>")
            embed.add_field(name='Joined at', value=f"<t:{round(member.joined_at.timestamp())}:R>")

            embed.add_field(name='Account Status',
                            value=str(member.status).title())
            embed.add_field(name='Account Activity',
                            value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

            Member = await self.bot.fetch_user(member.id)

            if Member.banner:
                embed.set_image(url=Member.banner)

            message = await interaction.response.send_message(embed=embed, ephemeral=True)
            #await message.edit(view=roles(self.bot, member, message))

        self.bot.slash_commands.append(whois)

    def cog_unload(self):
        self.ban_task.cancel()

    @tasks.loop(seconds=5)
    async def check_current_bans(self):
        currentTime = datetime.datetime.now()
        bans = deepcopy(self.bot.current_ban)
        for key, value in bans.items():
            if value['BanDuration'] is None:
                continue

            unbantime = value['BannedAt'] + relativedelta(days=7)

            if currentTime >= unbantime:
                guild = self.bot.get_guild(int(value['guildId']))
                member = await self.bot.fetch_user(int(value['_id']))
                moderator = guild.get_member(value['BanedBy'])
                self.bot.dispatch('ban_expired', guild, member, moderator)

                await self.bot.bans.delete(member.id)

                try:
                    self.bot.current_ban.pop(member.id)
                except KeyError:
                    pass
    
    @check_current_bans.before_loop
    async def before_check_current_bans(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_ban_expired(self, guild: discord.Guild, user: discord.User, moderator: discord.Member):
        if await guild.fetch_ban(user) == None:
            return
        try:
            await guild.unban(user, reason="Auto Automatic ban expired")
        except discord.NotFound:
            pass
        data = await self.bot.config.find(785839283847954433)
        embed = discord.Embed(title=f"🔨 UnBan | Case ID: {data['case']}",
                                    description=f" **Offender**: {user.name} | {user.mention} \n**Reason**: Auto Automatic expired\n **Moderator**: {moderator.name} {moderator.mention}", color=0xE74C3C)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"ID: {user.id}")
        data["case"] += 1
        await self.bot.config.upsert(data)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.bot.logging_webhook, session=session)
            await webhook.send(username=f"{self.bot.user.name} Logging", avatar_url=self.bot.user.avatar.url,embed=embed)
            await session.close()

    @app_commands.command(name="whois", description="Give all Infomation about user")
    @app_commands.check(can_use_slash)
    @app_commands.guilds(discord.Object(785839283847954433))
    async def uerinfo(self, interaction: discord.interactions, member: discord.Member = None):

        member = member if member else interaction.user
        usercolor = member.color

        embed = discord.Embed(title=f'{member.name}', color=usercolor)

        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url or None)
            embed.set_footer(text=f'ID {member.id}', icon_url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar)
            embed.set_footer(text=f'ID {member.id}', icon_url=member.default_avatar)

        embed.add_field(name='Account Name:',
                        value=f'{member.name}', inline=False)

        embed.add_field(
            name='Created at:', value=f"<t:{round(member.created_at.timestamp())}:R>")
        embed.add_field(name='Joined at', value=f"<t:{round(member.joined_at.timestamp())}:R>")

        embed.add_field(name='Account Status',
                        value=str(member.status).title())
        embed.add_field(name='Account Activity',
                        value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None")

        Member = await self.bot.fetch_user(member.id)

        if Member.banner:
            embed.set_image(url=Member.banner)

        msg = await interaction.response.send_message(embed=embed, view=roles(self.bot, member))

async def setup(bot):
    await bot.add_cog(v2Moderation(bot))
