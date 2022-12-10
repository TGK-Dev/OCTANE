import discord
from discord import app_commands
from discord.ext import commands
from utils.db import Document
from utils.transformers import TimeConverter, MutipleRole
import unidecode
import stringcase
import unicodedata
import re
import datetime

class serversettings(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.joingate = Document(self.bot.db, "joingate")
        self.bot.joingate_cache = {}
    
    joingate = app_commands.Group(name="joingate", description="Commands to change joingate settings")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in await self.bot.joingate.get_all(): self.bot.joingate_cache[guild["_id"]] = guild
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @staticmethod 
    async def create_joingate(guild_id):
        return {"_id": guild_id, "joingate": {'enabled': None, 'action': None, 'accountage': None, 'whitelist': [], 'autorole': [], 'decancer': None, 'logchannel': None}}

    
    @joingate.command(name='toggle', description="Toggle joingate on or off")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(enabled="Whether to enable or disable joingate")
    async def joingate_toggle(self, interaction: discord.Interaction, enabled: bool):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None: 
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        data["joingate"]["enabled"] = enabled
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
        await interaction.response.send_message(f"Joingate has been {'enabled' if enabled else 'disabled'}")
    
    @joingate.command(name='action', description="Set the action to take when a user fails the joingate")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(action="The action to take when a user fails the joingate. Options are: ban, kick")
    @app_commands.choices(action=[app_commands.Choice(name="kick", value="kick"), app_commands.Choice(name="ban", value="ban")])
    async def joingate_action(self, interaction: discord.Interaction, action: app_commands.Choice[str]):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None: 
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        data["joingate"]["action"] = action.value
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
        await interaction.response.send_message(f"Joingate action has been set to {action.value}")
    
    @joingate.command(name='accountage', description="Set the minimum account age required to pass the joingate")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(accountage="The minimum account age required to pass the joingate")
    @app_commands.choices(accountage=[app_commands.Choice(name="1 day", value="1"), app_commands.Choice(name="2 days", value="2"), app_commands.Choice(name="3 days", value="3"), app_commands.Choice(name="4 days", value="4"), app_commands.Choice(name="5 days", value="5"), app_commands.Choice(name="6 days", value="6"), app_commands.Choice(name="7 days", value="7")])
    async def joingate_accountage(self, interaction: discord.Interaction, accountage: app_commands.Choice[str]):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None: 
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        data["joingate"]["accountage"] = accountage.value
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
        await interaction.response.send_message(f"Joingate account age has been set to {accountage.value} days")
    
    @joingate.command(name='whitelist', description="Add or remove a user from the joingate whitelist")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(user="The user to add or remove from the whitelist")
    async def joingate_whitelist(self, interaction: discord.Interaction, user: str):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None: 
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        user = await self.bot.fetch_user(user)
        if user.id in data["joingate"]["whitelist"]:
            data["joingate"]["whitelist"].remove(user.id)
            await interaction.response.send_message(f"{user} has been removed from the joingate whitelist")
        else:
            data["joingate"]["whitelist"].append(user.id)
            await interaction.response.send_message(f"{user} has been added to the joingate whitelist")
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
    
    @joingate.command(name='autorole', description="Add or remove a role from the joingate autorole list")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(roles="The role to add or remove from the autorole list")
    async def joingate_autorole(self, interaction: discord.Interaction, roles: app_commands.Transform[discord.Role, MutipleRole]):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None:
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        added_roles = []
        removed_roles = []
        for role in roles:
            if role.id in data["joingate"]["autorole"]:
                data["joingate"]["autorole"].remove(role.id)
                removed_roles.append(role.mention)
            else:
                data["joingate"]["autorole"].append(role.id)
                added_roles.append(role.mention)
        embed = discord.Embed(title="Joingate Autorole", description="The following roles have been added to the joingate autorole list")
        embed.add_field(name="Added", value=", ".join(added_roles) if added_roles else "None")
        embed.add_field(name="Removed", value=", ".join(removed_roles) if removed_roles else "None")
        await interaction.response.send_message(embed=embed)
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
    
    @joingate.command(name='decancer', description="Toggle decancer on or off")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(enabled="Whether to enable or disable decancer")
    async def joingate_decancer(self, interaction: discord.Interaction, enabled: bool):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None:
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        data["joingate"]["decancer"] = enabled
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
        await interaction.response.send_message(f"Decancer has been set to {enabled}")
    
    @joingate.command(name="logchannel", description="Set the log channel for joingate")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(channel="The channel to log joingate actions to")
    async def joingate_logchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None:
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        data["joingate"]["logchannel"] = channel.id
        await self.bot.joingate.update(data)
        self.bot.joingate_cache[interaction.guild.id] = data
        await interaction.response.send_message(f"Joingate log channel has been set to {channel.mention}")
    
    @joingate.command(name="show", description="Show the current joingate settings")
    @app_commands.default_permissions(administrator=True)
    async def joingate_show(self, interaction: discord.Interaction):
        data = await self.bot.joingate.find(interaction.guild.id)
        if data is None:
            data = await self.create_joingate(interaction.guild.id)
            await self.bot.joingate.insert(data)
        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="Enabled", value=data["joingate"]["enabled"])
        embed.add_field(name="Action", value=data["joingate"]["action"])
        embed.add_field(name="Account Age", value=f'{data["joingate"]["accountage"]} Days')
        embed.add_field(name="Decancer", value=data["joingate"]["decancer"] if data["joingate"]["decancer"] else "Disabled")
        embed.add_field(name="Whitelist", value=", ".join(f'<@{user}>' for user in data['joingate']['whitelist']) if data["joingate"]["whitelist"] else "None")
        embed.add_field(name="Autorole", value=", ".join([f"<@&{role}>" for role in data["joingate"]["autorole"]]) if data["joingate"]["autorole"] else "None")
        embed.add_field(name="Log Channel", value=f"<#{data['joingate']['logchannel']}>")
        await interaction.response.send_message(embed=embed)
    
class JoinGateBackEnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in await self.bot.joingate.get_all(): self.bot.joingate_cache[guild["_id"]] = guild
        print(f"{self.__class__.__name__} is ready")
    
    @staticmethod
    def is_cancerous(text: str) -> bool:
        for segment in text.split():
            for char in segment:
                if not (char.isascii() and char.isalnum()):
                    return True
        return False

    @staticmethod
    def strip_accs(text):
        try:
            text = unicodedata.normalize("NFKC", text)
            text = unicodedata.normalize("NFD", text)
            text = unidecode.unidecode(text)
            text = text.encode("ascii", "ignore")
            text = text.decode("utf-8")
        except Exception as e:
            print(e)
        return str(text)
        
    async def nick_maker(self, guild: discord.Guild, old_shit_nick):
        old_shit_nick = self.strip_accs(old_shit_nick)
        new_cool_nick = re.sub("[^a-zA-Z0-9 \n.]", "", old_shit_nick)
        new_cool_nick = " ".join(new_cool_nick.split())
        new_cool_nick = stringcase.lowercase(new_cool_nick)
        new_cool_nick = stringcase.titlecase(new_cool_nick)
        default_name = "Request a new name"
        if len(new_cool_nick.replace(" ", "")) <= 1 or len(new_cool_nick) > 32:
            if default_name == "Request a new name":
                new_cool_nick = await self.get_random_nick(2)
            elif default_name:
                new_cool_nick = default_name
            else:
                new_cool_nick = "Request a new name"
        return new_cool_nick


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot: return
        if member.guild.id not in self.bot.joingate_cache.keys(): return
        data = self.bot.joingate_cache[member.guild.id]
        if not data["joingate"]["enabled"]: return
        if member.id in data["joingate"]["whitelist"]: return

        fail = self.bot.dispatch("joingate_check", member)
        if fail: return

        if data["joingate"]["decancer"]:
            print('doing decancer')
            if self.is_cancerous(member.display_name):
                print('is cancerous')
                new_nick = await self.nick_maker(member.guild, member.display_name)
                
                embed = discord.Embed(color=discord.Color.green(), title="Decancer", description="")
                embed.description += f"**Offender:** {member.mention}\n"
                embed.description += f"**Action:** Nickname Decancer\n"
                embed.description += f"**Reason:** Nickname contained non-ascii characters\n"
                embed.description += f"**Moderator:** {self.bot.user.mention}\n"
                embed.set_footer(text=f"User ID: {member.id}")
                embed.timestamp = datetime.datetime.utcnow()

                logchannel = member.guild.get_channel(data["joingate"]["logchannel"])
                try:
                    await member.edit(nick=new_nick, reason="joingate decancer")
                except:
                    return
                if logchannel: await logchannel.send(embed=embed)

    
    @commands.Cog.listener()
    async def on_joingate_check(self, member: discord.Member):
        data = self.bot.joingate_cache[member.guild.id]
        guild = member.guild
        if not data['joingate']['accountage']: return
        if (discord.utils.utcnow() - member.created_at).days < int(data['joingate']['accountage']):
            try:
                await member.send(f"Your account is too new to join this server. Please wait {data['joingate']['accountage']} days before joining.")
            except discord.Forbidden:
                pass
            if data["joingate"]["action"] == "kick":
                await member.kick(reason="joingate kick")
            elif data["joingate"]["action"] == "ban":
                await member.ban(reason="joingate ban")
            embed = discord.Embed(title="Kick", description="")
            embed.description += f"**Target:** {member.mention}\n"
            embed.description += f"**Action:** {data['joingate']['action'].title()}\n"
            embed.description += f"**Reason:** Account age is less than joingate account age\n"
            embed.description += f"**Moderator:** {self.bot.user.mention}\n"
            embed.set_footer(text=f"ID: {member.id}")
            embed.timestamp = discord.utils.utcnow()
            embed.color = discord.Color.red()

            logchannel = member.guild.get_channel(data["joingate"]["logchannel"])
            if logchannel: await logchannel.send(embed=embed)
            return True
        else:
            roles = [guild.get_role(role) for role in data["joingate"]["autorole"]]
            await member.edit(roles=roles, reason="joingate autorole")

async def setup(bot):
    await bot.add_cog(serversettings(bot), guilds=[discord.Object(785839283847954433)])
    await bot.add_cog(JoinGateBackEnd(bot), guilds=[discord.Object(785839283847954433)])