import discord
import datetime
from discord import app_commands
from discord.ext import commands
from typing import Literal, List
from utils.paginator import Paginator

staff_list = {
    'Moderator': 787259553225637889,
    'TRIAL MODERATOR': 843775369470672916,
    'Partnership Manager': 831405039830564875,
    'Giveaway Manager': 803230347575820289,
    'Event Manager': 852125566802198528,
}

class Staff(commands.GroupCog, name="staff", description="Staff management commands"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="appoint", description="appoint staff to user")
    @app_commands.choices(post=[app_commands.Choice(name="TRIAL MODERATOR", value=str(843775369470672916)), app_commands.Choice(name="Partnership Manager", value=str(831405039830564875)), app_commands.Choice(name="Giveaway Manager", value=str(803230347575820289)), app_commands.Choice(name="Event Manager", value=str(852125566802198528))])
    @app_commands.checks.has_permissions(administrator=True)
    async def appoint_user(self, interaction: discord.Interaction, user: discord.Member, post: app_commands.Choice[str]):
        staff_role = discord.utils.get(interaction.guild.roles, id=int(post.value))
        base_role = discord.utils.get(interaction.guild.roles, id=818129661325869058)
        data = await self.bot.staff.find(user.id)
        if not data:
            data = {
                '_id': user.id,
                'post': [],
                'recovery_code': None,
                'timezone': None,
                'vacation': {'last_vacation': None, 'days': 0, 'reason': None, 'start': None, 'end': None, 'approved_by': None},
            }
            await self.bot.staff.insert(data)
        if post.name in data['post']:
            await interaction.response.send_message(f"{user.mention} already has `{staff_role.name}`")
            return
        data['post'].append(post.name)
        await self.bot.staff.update(data)
        print(await self.bot.staff.find(user.id))
        await user.add_roles(staff_role, base_role, reason=f"{interaction.user.name} appoint {user.name} to {staff_role.name}")
        embed = discord.Embed(description=f"{user.mention} has been appoint to {staff_role.name}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="remove", description="remove staff from user")
    @app_commands.choices(post=[app_commands.Choice(name="TRIAL MODERATOR", value=str(843775369470672916)), app_commands.Choice(name="Partnership Manager", value=str(831405039830564875)), app_commands.Choice(name="Giveaway Manager", value=str(803230347575820289)), app_commands.Choice(name="Event Manager", value=str(852125566802198528))])
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member, post: app_commands.Choice[str]):
        staff_role = discord.utils.get(interaction.guild.roles, id=int(post.value))
        base_role = discord.utils.get(interaction.guild.roles, id=818129661325869058)
        data = await self.bot.staff.find(user.id)
        if not data:
            await interaction.response.send_message(f"{user.mention} is not staff")
            return
        if post.name not in data['post']:
            await interaction.response.send_message(f"{user.mention} is not {staff_role.name}")
            return
        data['post'].remove(post.name)
        if data['post'] == []:
            await self.bot.staff.delete(user.id)
            await user.remove_roles(staff_role, base_role, reason=f"{interaction.user.name} remove staff team")
            embed = discord.Embed(description=f"{user.mention} has been removed from staff team all post", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            await self.bot.staff.update(data)
            await user.remove_roles(staff_role, reason=f"{interaction.user.mention} remove {user.name} from {staff_role.name}")
            embed = discord.Embed(description=f"{user.mention} has been removed from {staff_role.name}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list", description="list staff")
    @app_commands.choices(short=[app_commands.Choice(name="TRIAL MODERATOR", value=str(843775369470672916)), app_commands.Choice(name="Partnership Manager", value=str(831405039830564875)), app_commands.Choice(name="Giveaway Manager", value=str(803230347575820289)), app_commands.Choice(name="Event Manager", value=str(852125566802198528))])
    @app_commands.describe(short="Short list of staff on base of post")
    async def list_staff(self, interaction: discord.Interaction, short: app_commands.Choice[str] = None):
        staff_list = await self.bot.staff.get_all()
        if not staff_list:
            await interaction.response.send_message("No staff", ephemeral=True)
            return
        hadmin = discord.Embed(title="Head Administrator", color=discord.Color.green(), description="")
        admin = discord.Embed(title="Administrator", color=discord.Color.green(), description="")
        moderator = discord.Embed(title="Moderator", color=discord.Color.green(), description="")
        trial_moderator = discord.Embed(title="Trial Moderator", color=discord.Color.green(), description="")
        partnership_manager = discord.Embed(title="Partnership Manager", color=discord.Color.green(), description="")
        giveaway_manager = discord.Embed(title="Giveaway Manager", color=discord.Color.green(), description="")
        event_manager = discord.Embed(title="Event Manager", color=discord.Color.green(), description="")

        if staff_list:
            if not short:
                for staff in staff_list:
                    if staff['post'] == []:
                        continue
                    if 'Moderator' in staff['post']:
                        moderator.description += f"<@{staff['_id']}>\n"
                    if 'TRIAL MODERATOR' in staff['post']:
                        trial_moderator.description += f"<@{staff['_id']}>\n"
                    if 'Partnership Manager' in staff['post']:
                        partnership_manager.description += f"<@{staff['_id']}>\n"
                    if 'Giveaway Manager' in staff['post']:
                        giveaway_manager.description += f"<@{staff['_id']}>\n"
                    if 'Event Manager' in staff['post']:
                        event_manager.description += f"<@{staff['_id']}>\n"
            
                embeds = [hadmin, admin, moderator, trial_moderator, partnership_manager, giveaway_manager, event_manager]
                await Paginator(interaction, embeds).start(embeded=True, quick_navigation=True)
            if short:
                embed = discord.Embed(title=short.name, color=discord.Color.green(), description="")
                for staff in staff_list:
                    if staff['post'] == []:
                        continue
                    if short.name in staff['post']:
                        embed.description += f"<@{staff['_id']}>\n"
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vacation", description="Set leave of days")
    @app_commands.describe(days="Number of days", reason="Reason for vacation", user="User to request vacation")
    @app_commands.checks.has_permissions(administrator=True)
    async def leave_of_days(self, interaction: discord.Interaction, user: discord.Member, days: int, reason: str):
        data = await self.bot.staff.find(user.id)
        if not data:
            await interaction.response.send_message(f"{user.mention} is not staff", ephemeral=True)
            return
        if data['vacation']['days'] != 0:
            await interaction.response.send_message(f"{interaction.user.mention} already has {data['vacation']['days']} days of leave", ephemeral=True)
            return
        data['vacation']['days'] = days
        data['vacation']['reason'] = reason
        data['vacation']['start'] = datetime.datetime.now()
        data['vacation']['last_vacation'] = datetime.datetime.now()
        data['vacation']['approvaed'] = interaction.user.id
        data['vacation']['end'] = data['vacation']['start'] + datetime.timedelta(days=days)

        await self.bot.staff.update(data)
        await interaction.response.send_message(f"<a:loading:1004658436778229791> | Setting up leave of days for {user.mention}")
        for post in data['post']:
            staff_role = discord.utils.get(interaction.guild.roles, id=staff_list[post])
            await user.remove_roles(staff_role, reason=f"User has stared leave of {days}")
        
        base_role = discord.utils.get(interaction.guild.roles, id=818129661325869058)
        leave_role = discord.utils.get(interaction.guild.roles, id=787055415157850142)
        await user.remove_roles(base_role, reason=f"User has started leave of {days}")
        await user.add_roles(leave_role, reason=f"User has started leave of {days}")

        await interaction.edit_original_response(content=None, embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | {user.mention} has been set up leave of days for {days} days", color=discord.Color.green()))
        channel = interaction.client.get_channel(974913093266182144)
        embed = discord.Embed(title=f"Info for {user.name}", color=discord.Color.green())
        embed.add_field(name="Days", value=days, inline=True)
        embed.add_field(name="Start", value=data['vacation']['start'].strftime("%d %B %Y"), inline=True)
        embed.add_field(name="End", value=data['vacation']['end'].strftime("%d %B %Y"), inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Approved by", value=f"<@{interaction.user.id}>", inline=True)
        await channel.send(embed=embed)

    @app_commands.command(name="endvacation", description="Remove leave of days")
    @app_commands.describe(user="User to remove leave of days")
    @app_commands.checks.has_permissions(administrator=True)
    async def end_vacation(self, interaction: discord.Interaction, user: discord.Member):
        data = await self.bot.staff.find(user.id)
        if not data:
            await interaction.response.send_message(f"{user.mention} is not staff", ephemeral=True)
            return
        if data['vacation']['days'] == 0:
            await interaction.response.send_message(f"{interaction.user.mention} does not have any leave of days", ephemeral=True)
            return
        data['vacation']['days'] = 0
        data['vacation']['reason'] = None
        data['vacation']['start'] = None
        data['vacation']['approvaed'] = None

        await self.bot.staff.update(data)
        await interaction.response.send_message(f"<a:loading:1004658436778229791> | Removing leave of days for {user.mention}")
        for post in data['post']:
            staff_role = discord.utils.get(interaction.guild.roles, id=staff_list[post])
            await user.add_roles(staff_role, reason=f"User has ended leave")
        
        await interaction.edit_original_response(content=None, embed=discord.Embed(description=f"<:dynosuccess:1000349098240647188> | {user.mention} has been removed leave of days", color=discord.Color.green()))

    @app_commands.command(name="currentvacation", description="Get current leaves")
    @app_commands.describe(user="User to get current leaves")
    @app_commands.checks.has_permissions(administrator=True)
    async def current_vacation(self, interaction: discord.Interaction, user: discord.Member):
        data = await self.bot.staff.find(user.id)
        if not data:
            await interaction.response.send_message(f"{user.mention} is not staff", ephemeral=True)
            return
        if data['vacation']['days'] == 0:
            await interaction.response.send_message(f"{interaction.user.mention} does not have any leave of days", ephemeral=True)
            return
        embed = discord.Embed(title=f"{user.name}'s current leave", color=discord.Color.green(), description=f"")
        embed.description += f"Days: {data['vacation']['days']}\n"
        embed.description += f"Reason: {data['vacation']['reason']}\n"
        embed.description += f"Start: <t:{round(data['vacation']['start'].timestamp())}:F> | <t:{round(data['vacation']['start'].timestamp())}:R>\n"
        embed.description += f"End: <t:{round(data['vacation']['end'].timestamp())}:F> | <t:{round(data['vacation']['end'].timestamp())}:R>\n"
        embed.description += f"Approved by: <@{data['vacation']['approvaed']}>\n"
        embed.description += f"Last vacation: <t:{round(data['vacation']['last_vacation'].timestamp())}:R>\n"
        await interaction.response.send_message(embed=embed)
        channel = self.bot.get_channel(974913093266182144)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Staff(bot), guilds=[discord.Object(785839283847954433)])
    