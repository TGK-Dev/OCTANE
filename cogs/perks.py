import discord
import datetime
from discord.ext import commands
from discord.app_commands import Group
from discord import Interaction
from discord import app_commands
from utils.db import Document
from utils.converter import TimeConverter
from typing import Union
from io import BytesIO
import asyncio
import aiohttp

class Perks(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.perks = Document(self.bot.db, "Perks")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is ready.')
    
    perks_give = Group(name="give", description="Give a special to user")

    @perks_give.command(name="role", description="Give user an custom role perk")
    @app_commands.describe(user="User to give perks", friend_limit="Limit of friends can user add", expire="Expire time of perks")
    async def role(self, interaction: Interaction, user: discord.Member, expire:str,friend_limit: app_commands.Range[int,1, 20]=5):
        await interaction.response.send_message("Starting the process")

        time= await TimeConverter().convert(interaction, expire)
        data = await self.bot.perks.find(user.id)
        if not data:
            data = {
                '_id': user.id,
                'guild': interaction.guild.id,
                'has_role_perks': None,
                'has_channel_perks': None,
                'role_perks': {'role_id': None, 'expires': None, 'has_created': False, 'given_by': None, 'given_at': None, 'friend_limit': None, 'friends': []},
                'channel_perks': {'channel_id': None, 'expires': None, 'has_created': False, 'given_by': None, 'given_at': None, 'friend_limit': None, 'friends': []},
            }
            await self.bot.perks.insert(data)
        
        if data['has_role_perks'] == True:
            await interaction.edit_original_response(content="user already have Custom Role Perks")
            return
        
        data['has_role_perks'] = True
        data['role_perks']['given_by'] = interaction.user.id
        data['role_perks']['expires'] = time
        data['role_perks']['given_at'] = datetime.datetime.now()
        data['role_perks']['friend_limit'] = friend_limit
        awat = await self.bot.perks.update(data)
        await interaction.edit_original_response(content="Custom Role Perks has been given to {}".format(user.mention))
    
    @perks_give.command(name="channel", description="Give user an custom channel perk")
    @app_commands.describe(user="User to give perks", expire="Expire time of perks", friend_limit="Limit of friends can user add")
    async def channel(self, interaction: Interaction, user: discord.Member, expire:str, friend_limit: app_commands.Range[int,1, 20]=5):
        await interaction.response.send_message("Starting the process")

        data = await self.bot.perks.find(user.id)
        if not data:
            data = {
                '_id': user.id,
                'guild': interaction.guild.id,
                'has_role_perks': None,
                'has_channel_perks': None,
                'role_perks': {'role_id': None, 'expires': None, 'has_created': False, 'given_by': None, 'given_at': None, 'friend_limit': friend_limit, 'friends': []},
                'channel_perks': {'channel_id': None, 'expires': None, 'has_created': False, 'given_by': None, 'given_at': None, 'friend_limit': friend_limit, 'friends': []},
            }
            await self.bot.perks.insert(data)
        
        if data['has_channel_perks'] == True:
            await interaction.edit_original_response(content="user already have Custom Channel Perks")
            return
        
        data['has_channel_perks'] = True
        data['channel_perks']['given_by'] = interaction.user.id
        data['channel_perks']['expires'] = datetime.datetime.now()
        data['channel_perks']['given_at'] = datetime.datetime.now()
        data['channel_perks']['friend_limit'] = 5
        await self.bot.perks.update(data)
        await interaction.edit_original_response(content="Custom Channel Perks has been given to {}".format(user.mention))

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
    
    @app_commands.command(name="clear", description="Clear perks for user")
    @app_commands.describe(user="User to clear perks")
    async def clear(self, interaction: Interaction, user: discord.Member):
        data = await self.bot.perks.find(user.id)
        if not data:
            await interaction.response.send_message("User has no perks", ephemeral=True)
            return
        if data['has_role_perks'] == True:
            role = discord.utils.get(interaction.guild.roles, id=data['role_perks']['role_id'])
            await role.delete()
        if data['has_channel_perks'] == True:
            channel = discord.utils.get(interaction.guild.channels, id=data['channel_perks']['channel_id'])
            await channel.delete()
        await self.bot.perks.delete(user.id)
        await interaction.response.send_message("Perks has been cleared", ephemeral=True)
        try:
            await user.send("Your Custom Role/Channel Perks has been cleared, please contact an admin if you think this is a mistake")
        except discord.HTTPException:
            pass
class Custom(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
        # self.bot.perks = Document(self.bot.db, "Perks")
    role = Group(name="role", description="edit a custom role")
    channel = Group(name="channel", description="edit a custom channel")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is ready.')

    @role.command(name="create", description="Create a custom role")
    @app_commands.describe(name="name of role", color="hex code of color", icon="icon of role")
    async def crole(self, interaction: Interaction, name:str, color:str, icon: discord.Attachment=None):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom role perks")
            return
        elif data['has_role_perks'] == False or None:
            await interaction.response.send_message("You don't have custom role perks")
            return

        config = await self.bot.perks.find(interaction.guild.id)
        if not config:
            await interaction.response.send_message("Contanct server because config is not found")
            return
        
        if data['role_perks']['has_created'] == True:
            await interaction.edit_original_response(content=f"You already have a custom role <@&{data['role_perks']['role_id']}>")
            return

        await interaction.response.send_message("Starting the process")
        if icon:
            if not icon.filename.endswith(('.png', '.jpg')):
                await interaction.edit_original_response(content="Please provide a valid image file type (png, jpg)")
                return
            else:
                url = icon.url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        icon = await response.read()
        role = await interaction.guild.create_role(name=name, color=discord.Color(int(color, 16)), display_icon=icon)
        await role.edit(position=int(config['role_position']))
        data['role_perks']['role_id'] = role.id
        data['role_perks']['has_created'] = True
        await self.bot.perks.update(data)
        await interaction.user.add_roles(role)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Custom Role has been created", color=discord.Color.green())
        await interaction.edit_original_response(embed=embed, content=None)
    
    @channel.command(name="create", description="Create a custom channel")
    @app_commands.describe(name="name of channel")
    async def cchannel(self, interaction: Interaction, name:str):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom channel perks")
            return
        elif data['has_channel_perks'] == False or None:
            await interaction.response.send_message("You don't have custom channel perks")
            return

        config = await self.bot.perks.find(interaction.guild.id)
        if not config:
            await interaction.response.send_message("Contanct server because config is not found")
            return
        
        if data['channel_perks']['has_created'] == True:
            await interaction.edit_original_response(content=f"You already have a custom channel <#{data['channel_perks']['channel_id']}>")
            return
        await interaction.response.send_message("Starting the process")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, attach_files=True, embed_links=True, add_reactions=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, attach_files=True, embed_links=True, add_reactions=True)            
        }
        channel = await interaction.guild.create_text_channel(name, overwrites=overwrites, category=interaction.guild.get_channel(config['category']))
        data['channel_perks']['channel_id'] = channel.id
        data['channel_perks']['has_created'] = True
        await self.bot.perks.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Channel has been created and added to your profile", color=discord.Color.green())
        await interaction.edit_original_response(embed=embed, content=None)


    @role.command(name="edit", description="Edit a custom role")
    @app_commands.describe(name="name of role", color="hex code of color", icon="icon of role")
    async def edit(self, interaction: Interaction, name:str=None, color:str=None, icon: discord.Attachment=None):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom role perks", ephemeral=True)
            return
        elif data['has_role_perks'] == False or None:
            await interaction.response.send_message("You don't have custom role perks", ephemeral=True)
            return
        if all(x is None for x in [name, color, icon]):
            await interaction.response.send_message("Please provide an Valid arguments", ephemeral=True)
            return
        config = await self.bot.perks.find(interaction.guild.id)
        if not config:
            await interaction.response.send_message("Contanct server because config is not found", ephemeral=True)
            return
        await interaction.response.send_message("Starting the process")
        role = interaction.guild.get_role(data['role_perks']['role_id'])
        if name:
            await role.edit(name=name)
        if color:
            await role.edit(color=discord.Color(int(color, 16)))
        if icon:
            if not icon.filename.endswith(('.png', '.jpg')):
                await interaction.edit_original_response(content="Please provide a valid image file type (png, jpg)")
                return
            else:
                url = icon.url
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        role_icon = await response.read()
                await role.edit(display_icon=role_icon)                    

        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Custom Role has been edited successfully", color=discord.Color.green())
        await interaction.edit_original_response(embed=embed, content=None)
    
    @channel.command(name="edit", description="Edit a custom channel")
    @app_commands.describe(name="name of channel")
    async def edit(self, interaction: Interaction, name:str):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom channel perks", ephemeral=True)
            return
        elif data['has_channel_perks'] == False or None:
            await interaction.response.send_message("You don't have custom channel perks", ephemeral=True)
            return
        elif data['channel_perks']['has_created'] == False or None:
            await interaction.response.send_message("You don't have created a channel", ephemeral=True)
            return
        config = await self.bot.perks.find(interaction.guild.id)
        if not config:
            await interaction.response.send_message("Contanct server because config is not found")
            return
        await interaction.response.send_message("Starting the process")
        channel = interaction.guild.get_channel(data['channel_perks']['channel_id'])
        await channel.edit(name=name)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Channel has been edited", color=discord.Color.green())
        await interaction.edit_original_response(embed=embed, content=None)
    
    @role.command(name="addfriend", description="add your custom role to a friend")
    @app_commands.describe(member="friend to add role to")
    @app_commands.rename(member='friend')
    async def addfriend(self, interaction: Interaction, member: discord.Member):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['has_role_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        if data['role_perks']['has_created'] == False or None or data['role_perks']['role_id'] == None:
            await interaction.response.send_message("You haven't created a role yet", ephemeral=True)
            return
        
        role = interaction.guild.get_role(data['role_perks']['role_id'])
        if len(data['role_perks']['friends']) >= int(data['role_perks']['friend_limit']):
            await interaction.response.send_message("You have reached the limit of friends", ephemeral=True)
            return
        if role in member.roles:
            await interaction.response.send_message("This member already has the role", ephemeral=True)
            return
        await member.add_roles(role)
        data['role_perks']['friends'].append(member.id)
        await self.bot.perks.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Added {role.mention} to your friend {member.mention}".format(role=role, member=member), color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    
    @role.command(name="removefriend", description="remove your custom role from a friend")
    @app_commands.describe(member="friend to remove role from")
    @app_commands.rename(member='friend')
    async def removefriend(self, interaction: Interaction, member: discord.Member):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['has_role_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        if data['role_perks']['has_created'] == False or None or data['role_perks']['role_id'] == None:
            await interaction.response.send_message("You haven't created a role yet", ephemeral=True)
            return
        role = interaction.guild.get_role(data['role_perks']['role_id'])
        if role not in member.roles:
            embed = discord.Embed(description="<:dynoError:1000351802702692442> | This member doesn't have the role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message("You can't remove your own role", ephemeral=True)
            return
        await member.remove_roles(role)
        data['role_perks']['friends'].remove(member.id)
        await self.bot.perks.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Removed {role.mention} from your friend {member.mention}".format(role=role, member=member), color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    
    @role.command(name="info", description="info about your custom role")
    async def info(self, interaction: Interaction):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['has_role_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['role_perks']['has_created'] == False or None or data['role_perks']['role_id'] == None:
            await interaction.response.send_message("You haven't created a role yet", ephemeral=True)
            return
        role = interaction.guild.get_role(data['role_perks']['role_id'])
        embed = discord.Embed(title="Role Info",color=role.color)
        embed.add_field(name="Role", value=role.mention)
        embed.add_field(name="Role ID", value=role.id)
        embed.add_field(name="Friends", value=f"Friends Limit: {len(data['role_perks']['friends'])}/{data['role_perks']['friend_limit']}"+"\n"+"\n".join([f"<@{friend}>" for friend in data['role_perks']['friends']]))
        await interaction.response.send_message(embed=embed)    
    
    @channel.command(name="addfriend", description="add your custom channel to a friend")
    @app_commands.describe(member="friend to add channel to")
    @app_commands.rename(member='friend')
    async def addfriend(self, interaction: Interaction, member: Union[discord.Member, discord.Role]):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks",ephemeral=True)
            return
        elif data['has_channel_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        if data['channel_perks']['has_created'] == False or None or data['channel_perks']['channel_id'] == None:
            await interaction.response.send_message("You haven't created a channel yet", ephemeral=True)
            return
        elif len(data['channel_perks']['friends']) > data['channel_perks']['friend_limit']:
            await interaction.response.send_message("You have reached the friend limit", ephemeral=True)
            return

        await interaction.response.send_message("Starting the process")
        channel = interaction.guild.get_channel(data['channel_perks']['channel_id'])
        
        await channel.set_permissions(member, read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
        data['channel_perks']['friends'].append(member.id)
        await self.bot.perks.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Added {channel.mention} to your friend {member.mention}".format(channel=channel, member=member), color=discord.Color.green())
        await interaction.edit_original_response(content=None, embed=embed)
    
    @channel.command(name="removefriend", description="remove your custom channel from a friend")
    @app_commands.describe(member="friend to remove channel from")
    @app_commands.rename(member='friend')
    async def removefriend(self, interaction: Interaction, member: discord.Member):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['has_channel_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        if data['channel_perks']['has_created'] == False or None or data['channel_perks']['channel_id'] == None:
            await interaction.response.send_message("You haven't created a channel yet", ephemeral=True)
            return
        elif len(data['channel_perks']['friends']) > data['channel_perks']['friend_limit']:
            await interaction.response.send_message("You have reached the friend limit", ephemeral=True)
            return

        await interaction.response.send_message("Starting the process")
        channel = interaction.guild.get_channel(data['channel_perks']['channel_id'])
        await channel.set_permissions(member, view_channel=False)
        data['channel_perks']['friends'].remove(member.id)
        await self.bot.perks.update(data)
        embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Removed {member.mention} from your chanenl {channel.mention}".format(channel=channel, member=member), color=discord.Color.green())
        await interaction.edit_original_response(content=None, embed=embed)
    
    @channel.command(name="info", description="show info about your custom channel")
    async def info(self, interaction: Interaction):
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        elif data['has_channel_perks'] == False or None:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        
        if data['channel_perks']['has_created'] == False or None or data['channel_perks']['channel_id'] == None:
            await interaction.response.send_message("You haven't created a channel yet", ephemeral=True)
            return

        channel = interaction.guild.get_channel(data['channel_perks']['channel_id'])
        embed = discord.Embed(title="Channel Info")
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Channel ID", value=channel.id)
        embed.add_field(name="Friend Limit", value=data['channel_perks']['friend_limit'])
        embed.add_field(name="Friends", value=f"Friends Limit: {len(data['channel_perks']['friends'])}/{data['channel_perks']['friend_limit']}"+"\n"+",".join([f"<@{member}>" for member in data['channel_perks']['friends']]))
        embed.color = discord.Color.green()
        await interaction.response.send_message(embed=embed)
    
    @channel.command(name="message-delete", description="delete a message from your custom channel")
    @app_commands.describe(message="id of the message to delete")
    async def message_delete(self, interaction: Interaction, message: str):
        try:
            message: int = int(message)
        except:
            await interaction.response.send_message("Invalid message id", ephemeral=True)
            return
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        if interaction.channel.id == data['channel_perks']['channel_id']:return await interaction.response.send_message("you can only delete messages from your custom channel", ephemeral=True)

        try:
            msg = await interaction.channel.fetch_message(message)
            if msg.author.id in [816699167824281621, 810041263452848179]: return await interaction.response.send_message("You can't delete messages from me or my bro", ephemeral=True)

            await msg.delete()
            embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Deleted message from {msg.author.mention}".format(msg=msg), color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except discord.NotFound:
            await interaction.response.send_message("Message not found", ephemeral=True)
            return
    
    @channel.command(name="message-ping", description="ping a user from your custom channel")
    @app_commands.describe(message="id of the message to ping")
    async def message_ping(self, interaction: Interaction, message: str):
        try:
            message: int = int(message)
        except:
            await interaction.response.send_message("Invalid message id", ephemeral=True)
            return
        data = await self.bot.perks.find(interaction.user.id)
        if not data:
            await interaction.response.send_message("You don't have custom perks", ephemeral=True)
            return
        if interaction.channel.id == data['channel_perks']['channel_id']:return await interaction.response.send_message("you can only ping members from your custom channel", ephemeral=True)

        try:
            msg = await interaction.channel.fetch_message(message)
            if msg.pinned == True:
                await msg.unpin()
                embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Unpinned message from {msg.author.mention}".format(msg=msg), color=discord.Color.green())
                await interaction.response.send_message(embed=embed)

            else:
                await msg.pin()
                embed = discord.Embed(description="<:dynosuccess:1000349098240647188> | Pinned message from {msg.author.mention}".format(msg=msg), color=discord.Color.green())
                await interaction.response.send_message(embed=embed)

            await interaction.response.send_message(msg.author.mention)
        except Exception as e:
            embed = discord.Embed(description="Error: {e}".format(e=e), color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return


async def setup(bot):
    await bot.add_cog(Perks(bot), guilds=[discord.Object(785839283847954433)])
    await bot.add_cog(Custom(bot), guilds=[discord.Object(785839283847954433)])