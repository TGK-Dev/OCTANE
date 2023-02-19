import discord
import datetime
from discord.ext import commands
from discord.app_commands import Group
from discord import Interaction
from discord import app_commands
from utils.db import Document
from utils.converter import TimeConverter
from ui.confirm import Confirm
from typing import Union, Literal
from io import BytesIO
import re
import asyncio
import aiohttp

#cretae an regex to get emoji id from str
emoji_regex = re.compile(r"<a?:\w+:(\d+)>")
class Perks(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.perks = Document(self.bot.db, "Perks")
        self.bot.autoreact = Document(self.bot.db, "AutoReact")
        self.bot.crole = Document(self.bot.db, "CustomRole")
        self.bot.cchannel = Document(self.bot.db, "CustomChannel")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is ready.')
    
    perks_give = Group(name="give", description="Give a special to user")

    # async def send_log(self, perk, given_by: discord.Member,user: discord.Member,expires: str, action: str, friends: int, color: discord.Color):
    #     embed = discord.Embed(title="Perks Update", description="", color=color)
    #     embed.description += f"**Perk:** {perk}\n"
    #     embed.description += f"**User:** {user.mention} ({user.id})\n"
    #     embed.description += f"**Given By:** {given_by.mention} ({given_by.id})\n"
    #     embed.description += f"**Expires:** {expires}\n"
    #     if friends: embed.description += f"**Friends:** {friends}\n"
    #     embed.description += f"**Action:** {action}\n"
    #     embed.timestamp = datetime.datetime.now()
    #     embed.set_footer(text=f"ID: {user.id}")
    #     log_channel = self.bot.get_channel(1060215919747543111)
    #     await log_channel.send(embed=embed)

    @perks_give.command(name="role", description="Give user an custom role perk")
    @app_commands.describe(user="User to give perks", friend_limit="Limit of friends can user add", expire="Expire time of perks leave it empty for permanent")
    async def role(self, interaction: Interaction, user: discord.Member, friend_limit: app_commands.Range[int,1, 20]=5, expire:str=None):
        data = await self.bot.crole.find(user.id)
        if not data:
            data = {
                '_id': user.id,
                'guild': interaction.guild.id,
                'role_id': None,
                'expires': None,
                'createdAt': None,
                'given_by': None,
                'friend_limit': None,
                'friends': []
            }
            data['expires'] = expire if expire else "Permanent"
            data['friend_limit'] = friend_limit
            data['given_by'] = interaction.user.id
            await self.bot.crole.insert(data)
            await interaction.channel.send(f"{user.mention} Now can create custom role by using </custom role create:1013452052401225839>")
            await interaction.response.send_message(f"Succesfully given {user.mention} a custom role perks", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} already have a custom role", ephemeral=True)
        
        #await self.send_log("Custom Role", interaction.user, user, expire, "Given", friend_limit, discord.Color.green())


    @perks_give.command(name="channel", description="Give user an custom channel perk")
    @app_commands.describe(user="User to give perks", expire="Expire time of perks", friend_limit="Limit of friends can user add")
    async def channel(self, interaction: Interaction, user: discord.Member, friend_limit: app_commands.Range[int,1, 20]=5, expire:str=None):
        data = await self.bot.cchannel.find(user.id)
        if not data:
            data = {
                '_id': user.id,
                'guild': interaction.guild.id,
                'channel_id': None,
                'expires': None,
                'createdAt': None,
                'given_by': None,
                'friend_limit': None,
                'friends': []
            }
            data['expires'] = expire if expire else "Permanent"
            data['friend_limit'] = friend_limit
            data['given_by'] = interaction.user.id

            await self.bot.cchannel.insert(data)
            await interaction.response.send_message(f"Succesfully given {user.mention} a custom channel perks")
            await interaction.chanenl.send(f"{user.mention} Now can create custom channel by using </custom channel create:1013452052401225839> ")
        else:
            await interaction.response.send_message(f"{user.mention} already have a custom channel", ephemeral=True)
        
        #await self.send_log("Custom Channel", interaction.user, user, expire, "Given", friend_limit, discord.Color.green())
    
        
    @perks_give.command(name="autoreact", description="Give user an custom autoreact perk")
    @app_commands.describe(user="User to give perks")
    async def autoreact(self, interaction: Interaction, user: discord.Member):
        data = await self.bot.autoreact.find(user.id)
        if data:
            await interaction.response.send_message("User already have autoreact perks", ephemeral=True)
            return
        data = {'_id': user.id, 'emoji': None, 'last_react': None}
        await self.bot.autoreact.insert(data)
        embed = discord.Embed(description="Successfully given autoreact perks to {}".format(user.mention), color=discord.Color.green())
        await interaction.channel.send(f"{user.mention} You can now use autoreact perks, please use </custom autoreact set:1013452052401225839> to set the emoji")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="config", description="Configure perks")
    @app_commands.describe(role_poistion="Positiob of role to create", category="Category of channel to create")
    async def config(self, interaction: Interaction, role_poistion: int, category: discord.CategoryChannel):
        data = await self.bot.perks.find(interaction.guild.id)
        if not data:
            data ={'_id': interaction.guild.id, 'role_position': None, 'category': None}
            await self.bot.perks.insert(data)
        data['role_position'] = role_poistion
        data['category'] = category.id
        await self.bot.perks.update(data)
        await interaction.response.send_message("Config has been saved", ephemeral=True)
    
    @app_commands.command(name="show", description="Show perks of user")
    @app_commands.describe(user="User to show perks")
    async def show(self, interaction: Interaction, user: discord.Member):
        crole = await self.bot.crole.find(user.id)
        cchannel = await self.bot.cchannel.find(user.id)
        autoreact = await self.bot.autoreact.find(user.id)
        embed = discord.Embed(title="Perks of {}".format(user.name), color=discord.Color.green())
        if crole:
            role = interaction.guild.get_role(crole['role_id'])
            value = f"Role: {interaction.guild.get_role(crole['role_id']).mention} ({crole['role_id']})\n"

            if crole['expires'] != 'Permanent' and crole['expires'] == int:
                value += f"Expires: <t:{round((role.created_at + datetime.timedelta(seconds=int(crole['expires']))).timestamp())}:R>\n"

            value += f"Given By: {interaction.guild.get_member(crole['given_by']).mention} ({crole['given_by']})\n"
            value += f"Created At: <t:{round(role.created_at.timestamp())}:R>\n"
            value += f"Friends: {len(role.members)}/{crole['friend_limit']}"
            embed.add_field(name="Custom Role", value=value, inline=False)

        if cchannel:
            channel = self.bot.get_channel(cchannel['channel_id'])
            print(channel)
            value = f"Channel: {channel.mention} ({cchannel['channel_id']})\n"

            if cchannel['expires'] != 'Permanent' or cchannel['expires'] == int:
                value += f"Expires: <t:{round((channel.created_at + datetime.timedelta(seconds=int(cchannel['expires']))).timestamp())}:R>\n"
            
            value += f"Given By: {interaction.guild.get_member(cchannel['given_by']).mention} ({cchannel['given_by']})\n"
            value += f"Created At: <t:{round(channel.created_at.timestamp())}:R>\n"
            value += f"Friends: {len(cchannel['friends'])}/{cchannel['friend_limit']}"
            embed.add_field(name="Custom Channel", value=value, inline=False)
        
        if autoreact:
            if autoreact['emoji']:
                emoji = await interaction.guild.fetch_emoji(autoreact['emoji'])
            else:
                emoji = "Not Set"
            value = f"Emoji: {emoji}\n"
            embed.add_field(name="AutoReact", value=value, inline=False)
        
        if not crole and not cchannel and not autoreact:
            embed.description = "User don't have any perks"

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="clear", description="Clear perks for user")
    @app_commands.describe(user="User to clear perks")
    async def clear(self, interaction: Interaction, user: discord.Member, perk: Literal['Custom Role', 'Custom Channel', 'AutoReact']):
        if perk == 'Custom Role':
            data = await self.bot.crole.find(user.id)
            if not data:
                await interaction.response.send_message("User don't have custom role perks", ephemeral=True)
                return
            role = interaction.guild.get_role(data['role_id'])
            if role:
                await role.delete()
            await self.bot.crole.delete(user.id)
            await interaction.response.send_message("Successfully cleared custom role perks", ephemeral=False)

        elif perk == 'Custom Channel':
            data = await self.bot.cchannel.find(user.id)
            if not data:
                await interaction.response.send_message("User don't have custom channel perks", ephemeral=True)
                return
            channel = interaction.guild.get_channel(data['channel_id'])
            if channel:
                await channel.delete()
            await self.bot.cchannel.delete(user.id)
            await interaction.response.send_message("Successfully cleared custom channel perks", ephemeral=False)
        
        elif perk == 'AutoReact':
            data = await self.bot.autoreact.find(user.id)
            if not data:
                await interaction.response.send_message("User don't have autoreact perks", ephemeral=True)
                return
            await self.bot.autoreact.delete(user.id)
            await interaction.response.send_message("Successfully cleared autoreact perks", ephemeral=False)
            try:
                self.bot.ar_cache.pop(user.id)
            except KeyError:
                pass
        
        #await self.send_log(perk, interaction.user, user, None, f"Cleared {perk}", None, discord.Color.red())
        
class Custom(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.perks = Document(self.bot.db, "Perks")
        self.emoji_regex = re.compile(r"<a?:\w+:(\d+)>")

    role = Group(name="role", description="edit a custom role")
    channel = Group(name="channel", description="edit a custom channel")
    autoreact = Group(name="autoreact", description="edit autoreact")

    async def send_log(self, perk, given_by: discord.Member,user: discord.Member,expires: str, action: str, friends: int, color: discord.Color):
        embed = discord.Embed(title="Perks Update", description="", color=color)
        embed.description += f"**Perk:** {perk}\n"
        embed.description += f"**User:** {user.mention} ({user.id})\n"
        embed.description += f"**Given By:** {given_by.mention} ({given_by.id})\n"
        embed.description += f"**Expires:** {expires}\n"
        if friends: embed.description += f"**Friends:** {friends}\n"
        embed.description += f"**Action:** {action}\n"
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"ID: {user.id}")
        log_channel = self.bot.get_channel(1060215919747543111)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is ready.')

    @role.command(name="create", description="Create a custom role")
    @app_commands.describe(name="name of role", color="hex code of color", icon="icon of role")
    async def crole(self, interaction: Interaction, name:str, color:str, icon: discord.Attachment=None):
        data = await self.bot.crole.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom role perks")
            return
        
        if data['role_id'] != None: return await interaction.response.send_message("You already created a custom role", ephemeral=True)
        color.replace("#", "")
        await interaction.response.send_message(embed=discord.Embed(description="<a:loading:998834454292344842> | Creating role..."), ephemeral=False)
        if icon:
            if not icon.filename.endswith(('.png', '.jpg')):
                return await interaction.response.send_message("Icon must be png or jpg", ephemeral=True)
            else:
                url = icon.url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        icon = await resp.read()
        else:
            icon = None
        
        new_role = await interaction.guild.create_role(name=name, color=discord.Color(int(color, 16)), hoist=False, mentionable=False, reason="Custom Role Perk claimed by {}".format(interaction.user), display_icon=icon)
        await new_role.edit(position=145)
        data['role_id'] = new_role.id
        data['createdAt'] = new_role.created_at
        await self.bot.crole.update(data)
        await interaction.edit_original_response(embed=discord.Embed(description="<:Toggle_on:1029771260114243584> ! Successfully created role {}".format(new_role.mention), color=discord.Color.green()))

        #await self.send_log("Custom Role", interaction.user, interaction.user, None, "Created", None, discord.Color.green())
    
    @channel.command(name="create", description="Create a custom channel")
    @app_commands.describe(name="name of channel")
    async def cchannel(self, interaction: Interaction, name:str):
        data = await self.bot.cchannel.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom channel perks")
            return
        elif data['channel_id'] != None:
            return await interaction.response.send_message("You already created a custom channel", ephemeral=True)
        
        await interaction.response.send_message(embed=discord.Embed(description="<a:loading:998834454292344842> | Creating channel..."), ephemeral=False)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, use_application_commands=True),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(name=name, overwrites=overwrites, reason="Custom Channel Perk claimed by {}".format(interaction.user), category=self.bot.get_channel(821807876812701706))
        data['channel_id'] = channel.id
        await self.bot.cchannel.update(data)
        await interaction.edit_original_response(embed=discord.Embed(description="<:Toggle_on:1029771260114243584> ! Successfully created Channel {}".format(channel.mention), color=discord.Color.green()))

        #await self.send_log("Custom Channel", interaction.user, interaction.user, None, "Created", None, discord.Color.green())

    @role.command(name="edit", description="Edit a custom role")
    @app_commands.describe(name="name of role", color="hex code of color", icon="icon of role")
    async def edit(self, interaction: Interaction, name:str=None, color:str=None, icon: discord.Attachment=None):
        data = await self.bot.crole.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom role perks")
            return
        elif data['role_id'] == None:
            return await interaction.response.send_message("You don't have created a role", ephemeral=True)
        
        role = interaction.guild.get_role(data['role_id'])
        if not role:
            return await interaction.response.send_message("You don't have created a role", ephemeral=True)
        
        await interaction.response.send_message(embed=discord.Embed(description="<a:loading:998834454292344842> | Editing role..."), ephemeral=False)

        if name:
            await role.edit(name=name, reason="Custom Role Perk edited by {}".format(interaction.user))
        if color:
            color.replace("#", "")
            await role.edit(color=discord.Color(int(color, 16)), reason="Custom Role Perk edited by {}".format(interaction.user))
        if icon:
            if not icon.filename.endswith(('.png', '.jpg')):
                return await interaction.response.send_message("Icon must be png or jpg", ephemeral=True)
            else:
                url = icon.url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        icon = await resp.read()
                await role.edit(display_icon=icon, reason="Custom Role Perk edited by {}".format(interaction.user))
        
        await interaction.edit_original_response(embed=discord.Embed(description="<:Toggle_on:1029771260114243584> ! Successfully edited role {}".format(role.mention), color=discord.Color.green()))

        #await self.send_log("Custom Role", interaction.user, interaction.user, None, "Edited", None, discord.Color.green())

    
    @channel.command(name="edit", description="Edit a custom channel")
    @app_commands.describe(name="name of channel")
    async def edit(self, interaction: Interaction, name:str):
        data = await self.bot.cchannel.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom channel perks")
            return
        elif data['channel_id'] == None:
            return await interaction.response.send_message("You don't have created a channel", ephemeral=True)

        channel = interaction.guild.get_channel(data['channel_id'])
        if not channel:
            return await interaction.response.send_message("You don't have created a channel", ephemeral=True)

        await interaction.response.send_message(embed=discord.Embed(description="<a:loading:998834454292344842> | Editing channel..."), ephemeral=False)
        await channel.edit(name=name, reason="Custom Channel Perk edited by {}".format(interaction.user))
        await interaction.edit_original_response(embed=discord.Embed(description="<:Toggle_on:1029771260114243584> ! Successfully edited channel {}".format(channel.mention), color=discord.Color.green()))

        #await self.send_log("Custom Channel", interaction.user, interaction.user, None, "Edited", None, discord.Color.green())

    
    @role.command(name="friend", description="add/remove your custom role to a friend")
    @app_commands.describe(member="friend to add role to")
    @app_commands.rename(member='friend')
    async def addfriend(self, interaction: Interaction, member: discord.Member):
        data = await self.bot.crole.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['role_id'] == None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        role = interaction.guild.get_role(data['role_id'])
        if not role:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(description="Successfully removed custom role {} from {}".format(role.mention, member.mention), color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            data['friends'].remove(member.id)
        else:
            if len(member.roles)-1 == data['friend_limit']:
                return await interaction.response.send_message("You can't add role to this member because they have reached the limit of {}".format(data['friend_limit']), ephemeral=True)
            await member.add_roles(role)
            embed = discord.Embed(description="Successfully added custom role {} to {}".format(role.mention, member.mention), color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            data['friends'].append(member.id)
        
        await self.bot.crole.upsert(data)
        #await self.send_log("Custom Role", interaction.user, member, None, "Friend list updated", None, discord.Color.green())
    
    @role.command(name="info", description="info about your custom role")
    async def info(self, interaction: Interaction):
        data = await self.bot.crole.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['role_id'] == None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return

        role = interaction.guild.get_role(data['role_id'])
        if not role:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        embed = discord.Embed(title="Custom Role Info", color=role.color)
        embed.add_field(name="Role", value=role.mention)
        embed.add_field(name="Friends", value=len(data['friends']))
        embed.add_field(name="Friend Limit", value=data['friend_limit'])
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @role.command(name="friendfix", description="fix your roles from friends")
    async def friendfix(self, interaction: Interaction):
        data = await self.bot.crole.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['role_id'] == None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        role = interaction.guild.get_role(data['role_id'])
        if not role:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        embed = discord.Embed(description="Caution: This will overwrite your friends list with all the members that have your role. Are you sure you want to continue?", color=discord.Color.red())
        view = Confirm(interaction.user, 60)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        await view.wait()
        if view.value is None:
            await view.interaction.response.edit_message(embed=discord.Embed(description="Command cancelled", color=discord.Color.red()), view=None)
            return
        elif view.value:
            data['friends'] = [member.id for member in role.members if member.id != interaction.user.id]
            await self.bot.crole.upsert(data)
            embed = discord.Embed(description="Successfully fixed friends list", color=discord.Color.green())
            embed.add_field(name="New Friends", value=",".join([f"<@{member}>" for member in data['friends']]))
            await interaction.response.edit_message(embed=embed, view=None)
        
        #await self.send_log("Custom Role", interaction.user, None, None, "Fixed Friends", None, discord.Color.green())

    
    @channel.command(name="friend", description="add/remove your custom channel to a friend")
    @app_commands.describe(member="friend to add channel to")
    @app_commands.rename(member='friend')
    async def addfriend(self, interaction: Interaction, member: Union[discord.Member, discord.Role]):
        data = await self.bot.cchannel.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['channel_id'] == None:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
        
        channel = interaction.guild.get_channel(data['channel_id'])
        if not channel:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
        
        if member.id in data['friends']:
            await channel.set_permissions(member, view_channel=False, send_messages=False)
            await interaction.response.send_message(embed=discord.Embed(description="Removed {} from your channel".format(member.mention), color=discord.Color.green()), ephemeral=False)
            data['friends'].remove(member.id)
        else:
            if len(data['friends']) >= data['friend_limit']:
                await interaction.response.send_message("You have reached the friend limit", ephemeral=True)
                return
            await channel.set_permissions(member, view_channel=True, send_messages=True)
            await interaction.response.send_message(embed=discord.Embed(description="Added {} to your channel".format(member.mention), color=discord.Color.green()), ephemeral=False)
            data['friends'].append(member.id)
        
        await self.bot.cchannel.upsert(data)
        #await self.send_log("Custom Channel", interaction.user, None, None, "Friend List Updated", member, discord.Color.green())
    
    @channel.command(name="info", description="show info about your custom channel")
    async def info(self, interaction: Interaction):
        data = await self.bot.cchannel.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['channel_id'] == None:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return

        channel = interaction.guild.get_channel(data['channel_id'])
        if not channel:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
        
        embed = discord.Embed(title="Custom Channel Info", color=discord.Color.green())
        embed.add_field(name="Channel Name", value=channel.name)
        embed.add_field(name="Channel ID", value=channel.id)
        embed.add_field(name="Friend Limit", value=data['friend_limit'])
        embed.add_field(name="Friends", value=f"{len(data['friends'])}")

        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @channel.command(name="message-delete", description="delete a message from your custom channel")
    @app_commands.describe(message="id of the message to delete")
    async def message_delete(self, interaction: Interaction, message: str, reason: str = None):
        try: message: int = int(message)
        except:
            await interaction.response.send_message("Invalid message id", ephemeral=True)
            return
        data = await self.bot.cchannel.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['channel_id'] == None:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
            
        channel = interaction.guild.get_channel(data['channel_id'])
        if not channel:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
        
        try:
            msg = await channel.fetch_message(message)
        except discord.NotFound:
            await interaction.response.send_message("Message not found", ephemeral=True)
            return
        if data['_id'] != interaction.user.id: await interaction.response.send_message("You can only delete message from your channel", ephemeral=True)
        await msg.delete(reason=reason)
        await interaction.response.send_message(embed=discord.Embed(description="Deleted message", color=discord.Color.green()), ephemeral=False)

        #await self.send_log("Custom Channel", interaction.user, None, None, "Message Deleted", msg, discord.Color.green())

    @autoreact.command(name="set", description="set a message to auto react")
    @app_commands.describe(emoji="emoji to react with must be from this server")
    async def set(self, interaction: Interaction, emoji: str):
        data = await self.bot.autoreact.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have auto react perks", ephemeral=True)
            return
        emojiID = self.emoji_regex.findall(emoji)
        if not emojiID:
            await interaction.response.send_message("Invalid emoji", ephemeral=True)
            return
        emojiID = int(emojiID[0])
        emoji = self.bot.get_emoji(emojiID)
        if not emoji:
            await interaction.guild.fetch_emoji(emojiID)
            if not emoji:
                await interaction.response.send_message("Invalid emoji", ephemeral=True)
                return
        if emoji.guild.id != interaction.guild.id:
            await interaction.response.send_message("Invalid emoji", ephemeral=True)
            return
        data['emoji'] = emoji.id
        await self.bot.autoreact.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Set auto react emoji to {emoji}".format(emoji=emoji), color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        self.bot.ar_cache[data['_id']] = data
    
        #await self.send_log("Auto React", interaction.user, None, None, "Emoji Set", emoji, discord.Color.green())

async def setup(bot):
    await bot.add_cog(Perks(bot), guilds=[discord.Object(785839283847954433)])
    await bot.add_cog(Custom(bot), guilds=[discord.Object(785839283847954433)])
