import discord
from discord.ext import commands
from discord import app_commands
from utils.paginator import Paginator
from utils.converter import TimeConverter
import typing

class Custom_Roles_slash(app_commands.Group):
    def __init__(self):
        super().__init__(name="custom_roles")
    
    @app_commands.command(name="Create", description="Create a custom role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="Name of the role", color="Color of the role", time="duration of the role")
    async def create(self, interaction: discord.Interaction, owner: discord.Member, name: str, color: str, time: str):
        time = await TimeConverter().convert(interaction, time)
        role = await interaction.guild.create_role(name=name, color=discord.Color(int(color, 16)), reason=f"Created by {interaction.user.name}")
        await owner.add_roles(role, reason=f"Created by {interaction.user.name}")
        embed = discord.Embed(description=f"{role.mention} has been created", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
        data = {"_id": owner.id, 'created_at': role.created_at, 'created_by': interaction.user.id, 'time': time, 'frineds': [], 'role': role.id, 'frinds_limit': 2}
        await interaction.client.crole.insert(data)

    @app_commands.command(name="Delete", description="Delete a custom role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="select option", reason="reason for deleting role")
    async def delete(self, interaction: discord.Interaction, role: discord.Role, reason: str="No reason provided"):
        data = await interaction.client.crole.find_by_custom({'role': role.id})
        if not data:
            embed = discord.Embed(description=f"{role.mention} is not a custom role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        await interaction.guild.delete_role(role, reason=reason)
        await interaction.client.crole.delete_by_custom({'role': role.id})
        embed = discord.Embed(description=f"{role.mention} has been deleted", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addtime", description="Add time to a custom role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="User to add time", time="duration of the role")
    async def addtime(self, interaction: discord.Interaction, user: discord.Member, time:str):
        data = await interaction.client.crole.find_by_custom({'_id': user.id})
        if not data:
            embed = discord.Embed(description=f"{user.mention} has no custom role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        time = await TimeConverter().convert(interaction, time)
        data['time'] += time
        await interaction.client.crole.update(data)
        embed = discord.Embed(description=f"{user.mention} has been given {time} more time", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addfriend", description="Add a friend to a custom role")
    @app_commands.describe(user="User to add friend", friend="friend to add")
    async def addfriend(self, interaction: discord.Interaction, friend: discord.Member):
        data = await interaction.client.crole.find_by_custom({'_id': interaction.author.id})
        if not data:
            embed = discord.Embed(description=f"{interaction.author.mention} has no custom role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        if friend in data['friends']:
            embed = discord.Embed(description=f"{friend.mention} is already a friend of {interaction.author.mention}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        if len(data['friends']) >= data['frinds_limit']:
            embed = discord.Embed(description=f"{interaction.author.mention} has reached the limit of friends", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        data['friends'].append(friend.id)
        await interaction.client.crole.update(data)
        await friend.add_roles(interaction.guild.get_role(data['role']), reason=f"Added by {interaction.author.name}")
        embed = discord.Embed(description=f"{friend.mention} has been added to {interaction.author.mention}'s friends", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removefriend", description="Remove a friend from a custom role")
    @app_commands.describe(user="User to remove friend", friend="friend to remove")
    async def removefriend(self, interaction: discord.Interaction, friend: discord.Member):
        data = await interaction.client.crole.find_by_custom({'_id': interaction.author.id})
        if not data:
            embed = discord.Embed(description=f"{interaction.author.mention} has no custom role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        if friend not in data['friends']:
            embed = discord.Embed(description=f"{friend.mention} is not a friend of {interaction.author.mention}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        data['friends'].remove(friend.id)
        await interaction.client.crole.update(data)
        await friend.remove_roles(interaction.guild.get_role(data['role']), reason=f"Removed by {interaction.author.name}")
        embed = discord.Embed(description=f"{friend.mention} has been removed from {interaction.author.mention}'s friends", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setlimit", description="Set the limit of friends a custom role can have")
    @app_commands.describe(user="User to set limit", limit="limit of friends")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlimit(self, interaction: discord.Interaction, user: discord.Member, limit:int):
        data = await interaction.client.crole.find_by_custom({'_id': user.id})
        if not data:
            embed = discord.Embed(description=f"{user.mention} has no custom role", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        if limit > 10:
            embed = discord.Embed(description=f"{limit} is too high", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        data['friends_limit'] = limit
        await interaction.client.crole.update(data)
        embed = discord.Embed(description=f"{user.mention}'s friends limit has been set to {limit}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        try:
            await interaction.response.send_message(error, ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send(error, ephemeral=True)
        except:
            pass
class Custom_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(Custom_Roles_slash(), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

async def setup(bot):
    await bot.add_cog(Custom_Roles(bot))


        # data = await interaction.client.crole.find(interaction.user.id)
        # if data is None:
        #     await interaction.response.send_message("You have currently no custom role liked to you", ephemeral=True)
        # else:
        #     embed = discord.Embed(description="")
        #     if interaction.user.id == data['_id']:
        #         role = discord.utils.get(interaction.guild.roles, id=data["role"])
        #         if name:
        #             embed.description += "New Name: " + name + "\n"
        #             await role.edit(name=name)
        #         if color:
        #             embed.description += "New Color: " + color + "\n"
        #             await role.edit(color=discord.Color(int(color, 16)))          #࿔･ﾟ♡ jay's friends ♡ ࿔･ﾟ♡       
        #         if icon:
        #             if icon.filename.endswith(".png") or icon.filename.endswith(".jpg"):
        #                 #convert icon to bytes-like object
        #                 icon_bytes = await icon.read()
        #                 embed.description += "New Icon: " + icon.filename + "\n"
        #                 await role.edit(display_icon=icon_bytes)                   
        #             else:
        #                 await interaction.response.send_message(content="Please upload a valid Format: .png or .jpg")