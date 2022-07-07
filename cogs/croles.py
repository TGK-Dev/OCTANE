import discord
from discord.ext import commands
from discord import app_commands
from utils.paginator import Paginator
import typing

class Custom_Roles_slash(app_commands.Group):
    def __init__(self):
        super().__init__(name="custom_roles")
    
    @app_commands.command(name="link", description="Link custom role to user")
    @app_commands.describe(role="Role to link", member="Member to link role to")
    @app_commands.guilds(785839283847954433)
    async def link_role(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.send("You don't have permission to use this command.")

        data = await interaction.client.crole.find(role.id)
        if data is not None:
            await interaction.response.send_message("Role is Already Linked to User use `/crole unlink`", ephemeral=True)
        else:
            data = {"_id": member.id, "role": role.id, "linked_by": interaction.user.id, "members": []}
            await interaction.client.crole.insert(data)
            await member.add_roles(role)
            embed = discord.Embed(description=f"{role.name} has been linked to {member.mention}", color=member.color)
            await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(name="unlink", description="Unlink custom role from user")
    @app_commands.describe(role="Role to unlink", member="Member to unlink role from")
    @app_commands.guilds(785839283847954433)
    async def unlink_role(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.send("You don't have permission to use this command.")
        data = await interaction.client.crole.find(member.id)
        if data is None:
            await interaction.response.send_message("Role is Not Linked to User use `/crole link`", ephemeral=True)
        else:
            await interaction.client.crole.delete(member.id)
            embed = discord.Embed(description=f"{role.name} has been unlinked from {member.mention}", color=member.color)
            await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(name="list", description="List all custom roles")
    @app_commands.guilds(785839283847954433)
    async def list_roles(self, interaction: discord.Interaction):
        data = await interaction.client.crole.get_all()
        if data is None:
            await interaction.response.send_message("No Custom Roles", ephemeral=True)
        else:
            pages = []
            for i in data:
                role = discord.utils.get(interaction.guild.roles, id=i["role"])
                member = discord.utils.get(interaction.guild.members, id=i["_id"])
                embed = discord.Embed(description=f"Role: {role.mention}\nOwner: {member.mention}\nMember: {len(i['members'])}\nLinked By: <@{i['linked_by']}>", color=role.color)
                pages.append(embed)
            
            await Paginator(interaction, pages).start(quick_navigation=False,embeded=True)

    @app_commands.command(name="edit", description="edit custom role")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(name="New name of role", color="Hex color of role", icon="File of role icon")
    async def edit_role(self, interaction: discord.Interaction, name: str=None, color: str=None, icon: discord.Attachment=None):        
        data = await interaction.client.crole.find(interaction.user.id)
        if data is None:
            await interaction.response.send_message("You have currently no custom role liked to you", ephemeral=True)
        else:
            embed = discord.Embed(description="")
            if interaction.user.id == data['_id']:
                role = discord.utils.get(interaction.guild.roles, id=data["role"])
                if name:
                    embed.description += "New Name: " + name + "\n"
                    await role.edit(name=name)
                if color:
                    embed.description += "New Color: " + color + "\n"
                    await role.edit(color=discord.Color(int(color, 16)))          #࿔･ﾟ♡ jay's friends ♡ ࿔･ﾟ♡       
                if icon:
                    if icon.filename.endswith(".png") or icon.filename.endswith(".jpg"):
                        #convert icon to bytes-like object
                        icon_bytes = await icon.read()
                        embed.description += "New Icon: " + icon.filename + "\n"
                        await role.edit(display_icon=icon_bytes)                   
                    else:
                        await interaction.response.send_message(content="Please upload a valid Format: .png or .jpg")
                        
                embed.color=role.color
                await interaction.response.send_message(content=None,embed=embed)

    @app_commands.command(name="manage", description="Add member to custom role")
    @app_commands.describe(option="chose to add/remove members", member="Member to add to role")
    @app_commands.guilds(785839283847954433)
    async def add_member(self, interaction: discord.Interaction, member: discord.Member, option: typing.Literal['add', 'remove']):
        data = await interaction.client.crole.find(interaction.user.id)
        
        if data is None:
            await interaction.response.send_message("You have currently no custom role liked to you", ephemeral=True)
        else:

            if interaction.user.id == data['_id']:
                role = discord.utils.get(interaction.guild.roles, id=data["role"])

                if option == "add":

                    if len(data["members"]) >= 5:
                        await interaction.response.send_message("You have reached the max amount of members for this role", ephemeral=True)
                        return

                    await member.add_roles(role)
                    data["members"].append(member.id)
                    await interaction.client.crole.update(data)

                    embed = discord.Embed(description=f"{member.mention} has been added to {role.name}", color=role.color)
                    await interaction.response.send_message(content=None,embed=embed, ephemeral=False)

                elif option == "remove":

                    if role not in member.roles:
                        await interaction.response.send_message("Member is not in this role", ephemeral=True)
                        return
                    await member.remove_roles(role)
                    data["members"].remove(member.id)
                    await interaction.client.crole.update(data)

                    embed = discord.Embed(description=f"{member.mention} has been removed from {role.name}", color=role.color)
                    await interaction.edit_original_message(content=None,embed=embed, ephemeral=False)
            else:
                await interaction.response.send_message("You do not have permission to do this", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        try:
            await interaction.response.send_message(f"An error has occured {str(error)[:2000]}", ephemeral=True)
        except:
            await interaction.followup.send_message(f"An error has occured {str(error)[:2000]}")
class Custom_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(Custom_Roles_slash(), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

async def setup(bot):
    await bot.add_cog(Custom_Roles(bot))