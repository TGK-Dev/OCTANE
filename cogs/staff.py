import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
import random
import string
class Staff(app_commands.Group):
    def __init__(self):
        super().__init__(name='staff')
    

    @app_commands.command(name="add", description="Add a user to the staff list")
    @app_commands.choices(post=[app_commands.Choice(name="Head Admin", value="799037944735727636"), app_commands.Choice(name="Admin", value="785845265118265376"), app_commands.Choice(name="Moderator", value="787259553225637889"), app_commands.Choice(name="Trial Moderator", value="843775369470672916"),app_commands.Choice(name="Partnership Manager", value="831405039830564875"), app_commands.Choice(name="Giveaway Manager", value="803230347575820289"), app_commands.Choice(name="Event Manager", value="852125566802198528")])
    async def add(self, interaction: discord.Interaction, member: discord.Member, post: app_commands.Choice[str]):
        if interaction.user.id not in [488614633670967307, 301657045248114690,651711446081601545,413651113485533194,562738920031256576]:
            await interaction.response.send_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | You do not have permission to use this command", color=discord.Color.red()))
            return
        await interaction.response.send_message("Adding user to staff list...")
        data = await interaction.client.staff.find(member.id)
        if not data:
            data = {
                '_id': member.id,
                'post': [],
                'recovery_code': None,
            }
            await interaction.client.staff.insert(data)
        if post.value in data['post']:
            await interaction.edit_original_message(content=None, embed=discord.Embed(title="User already has this post", color=discord.Color.red()))
            return
        await interaction.client.staff.update(data)
        role = discord.utils.get(interaction.guild.roles, id=int(post.value))
        await member.add_roles(role)
        await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Successfully added {member.mention} to {role.name}`", color=discord.Color.green()))
    
    @app_commands.command(name="remove", description="Remove a user from the staff list")
    @app_commands.choices(post=[app_commands.Choice(name="Head Admin", value="799037944735727636"), app_commands.Choice(name="Admin", value="785845265118265376"), app_commands.Choice(name="Moderator", value="787259553225637889"), app_commands.Choice(name="Trial Moderator", value="785845265118265376"), app_commands.Choice(name="Partnership Manager", value="831405039830564875"), app_commands.Choice(name="Giveaway Manager", value="803230347575820289"), app_commands.Choice(name="Event Manager", value="852125566802198528")])
    async def remove(self, interaction: discord.Interaction, member: discord.Member, post:str):
        if interaction.user.id not in [488614633670967307, 301657045248114690,651711446081601545,413651113485533194,562738920031256576]:
            await interaction.response.send_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | You do not have permission to use this command", color=discord.Color.red()))
            return
        await interaction.response.send_message("Removing user from staff list...")
        data = await interaction.client.staff.find(member.id)
        if not data:
            await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | {member.mention} is not in the staff list", color=discord.Color.red()))
            return
        if post.value not in data['post']:
            await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | {member.mention} is not a {post.name}", color=discord.Color.red()))
            return
        await interaction.client.staff.update(data)
        role = discord.utils.get(interaction.guild.roles, id=int(post.value))
        await member.remove_roles(role)
        await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Successfully removed {member.mention} from {role.name}`", color=discord.Color.green()))

    @app_commands.command(name="list", description="List all users in the staff list")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.send_message("Listing all users in the staff list...")
        data = await interaction.client.staff.get_all()
        embed = discord.Embed(title="Staff List", color=discord.Color.blue())
        Head_admin = ""
        Admin = ""
        Moderator = ""
        Trial_Moderator = ""
        Partnership_Manager = ""
        Giveaway_Manager = ""
        Event_Manager = ""
        all_staff = ""
        for member in data:
            for post in member['post']:
                if post == "Head Admin":
                    Head_admin += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Admin":
                    Admin += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Moderator":
                    Moderator += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Trial Moderator":
                    Trial_Moderator += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Partnership Manager":
                    Partnership_Manager += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Giveaway Manager":
                    Giveaway_Manager += f"{interaction.guild.get_member(member['_id']).mention}\n"
                elif post == "Event Manager":
                    Event_Manager += f"{interaction.guild.get_member(member['_id']).mention}\n"
            all_staff += f"{interaction.guild.get_member(member['_id']).mention} **TimeZone:** {member['timezone']}\n"
        embed.add_field(name="Head Admin", value=Head_admin if Head_admin else "None", inline=False)
        embed.add_field(name="Admin", value=Admin if Admin else "None", inline=False)
        embed.add_field(name="Moderator", value=Moderator if Moderator else "None", inline=False)
        embed.add_field(name="Trial Moderator", value=Trial_Moderator if Trial_Moderator else "None", inline=False)
        embed.add_field(name="Partnership Manager", value=Partnership_Manager if Partnership_Manager else "None", inline=False)
        embed.add_field(name="Giveaway Manager", value=Giveaway_Manager if Giveaway_Manager else "None", inline=False)
        embed.add_field(name="Event Manager", value=Event_Manager if Event_Manager else "None", inline=False)
        embed.add_field(name="All Staff", value=all_staff if all_staff else "None", inline=False)
        await interaction.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="recovery", description="Set a recovery code for a user")
    async def recovery(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id not in [488614633670967307, 301657045248114690,651711446081601545,413651113485533194,562738920031256576]:
            await interaction.response.send_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | You do not have permission to use this command", color=discord.Color.red()))
            return

        data = await interaction.client.staff.find(member.id)
        await interaction.response.send_message("Setting recovery code...")
        if not data:
            await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | {member.mention} is not in the staff list", color=discord.Color.red()))
            return
        
        #create randonm code 
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        data['recovery_code'] = code
        embed = discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Successfully set a recovery code for {member.mention}", color=discord.Color.green())
        dm_embed = discord.Embed(description=f"You have received a recovery code incase you lost your current account password.\nNever share this code with anyone.\nHigher staff will never ask you for your recovery code.\nTo use your recovery code, type `-recovery {code}` in the DM with the bot.\nIf you did not request a recovery code, please ignore this message.", color=discord.Color.green())
        dm_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/999553621895155723/1003581466950783026/tgk.gif")
        await interaction.client.staff.update(data)
        msg = await member.send(embed=dm_embed)
        await msg.pin()
        await interaction.edit_original_message(content=None, embed=embed)
    
    @app_commands.command(name="set-timezone", description="Set Timezone of a user")
    @app_commands.describe(timezone="Your Timezone")
    async def set_timezone(self, interaction: discord.Interaction, timezone:str):
        data = await interaction.client.staff.find(interaction.user.id)
        await interaction.response.send_message("Setting timezone...")
        if not data:
            await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynoError:1000351802702692442> | {interaction.user.mention} is not in the staff list", color=discord.Color.red()))
            return
        data['timezone'] = timezone
        await interaction.client.staff.update(data)
        await interaction.edit_original_message(content=None, embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | Successfully set {interaction.user.mention}'s timezone to {timezone}", color=discord.Color.green()))

class Staff_mamagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(Staff(), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded")

    @commands.command(name="recovery", description="Use your recovery code")
    @commands.dm_only()
    async def recovery(self, ctx, code: str):
        await ctx.send("Checking recovery code...")
        data = await self.bot.staff.find_by_custom({'recovery_code': code})
        if not data:
            await ctx.send(embed=discord.Embed(description="<:dynoError:1000351802702692442> | Invalid recovery code", color=discord.Color.red()))
            return
        if data:
            data['recovery_account'] = ctx.author.id
            data['recovery_code'] = None
            await self.bot.staff.update(data)
            await ctx.send(embed=discord.Embed(description="<:dynosuccess:1000349098240647188> | Successfully recovered your account\nServer Owners are notified of your recovery request\nPlease wait for them to respond", color=discord.Color.green()))

            channel = self.bot.get_channel(792246185238069249)
            embed = discord.Embed(title="Recovery Request", color=discord.Color.blue())
            embed.add_field(name="Old Account", value=f"<@{data['_id']}>", inline=False)
            embed.add_field(name="New Account", value=f"<@{ctx.author.id}>", inline=False)
            embed.add_field(name="Staff Position", value=",".join(data['post']), inline=False)
            await channel.send(embed=embed)
    
    @commands.command(name="link-code", description="Link your account to a recovery code")
    @commands.dm_only()
    async def link_code(self, ctx, code: str):
        await ctx.send("Linking account...")
        data = await self.bot.staff.find(ctx.author.id)
        if not data:
            await ctx.send(embed=discord.Embed(description="<:dynoError:1000351802702692442> | You are not in the staff list", color=discord.Color.red()))
            return
        if data:
            data['recovery_code'] = code
            data['recovery_account'] = None
            await self.bot.staff.update(data)
            await ctx.send(embed=discord.Embed(description="<:dynosuccess:1000349098240647188> | Successfully linked your account", color=discord.Color.green()))
        

async def setup(bot):
    await bot.add_cog(Staff_mamagement(bot))
    