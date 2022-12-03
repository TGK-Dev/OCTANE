import discord
import datetime
from discord import app_commands
from discord.ext import commands, tasks
from typing import Literal, List
from utils.paginator import Paginator
from utils.db import Document
from discord.app_commands import Group
from ui.confirm import Confirm
import asyncio
import string
import random

staff_list = {
    'Head Administator': 785845265118265376,
    'Moderator': 787259553225637889,
    'TRIAL MODERATOR': 843775369470672916,
    'Partnership Manager': 831405039830564875,
    'Giveaway Manager': 803230347575820289,
    'Event Manager': 852125566802198528,
}

class Staff(commands.GroupCog, name="staff", description="Staff management commands"):
    def __init__(self, bot):
        self.bot = bot
        self.leave_task = self.leave_task.start()
        self.bot.staff = Document(bot.db, 'staff')

    leave = Group(name="leave", description="manage staff leaves")

    def cog_unload(self):
        self.leave_task.cancel()
    
    @tasks.loop(hours=1)
    async def leave_task(self):
        current_staff = await self.bot.staff.get_all()
        today = datetime.datetime.now()
        leave_log_channel = self.bot.get_channel(974913093266182144)
        main_guild = self.bot.get_guild(785839283847954433)
        leave_role = main_guild.get_role(787055415157850142)
        for staff in current_staff:
            if 'leave' not in staff.keys(): continue

            if staff['leave']['end'] < today:
                staff_member = main_guild.get_member(staff['_id'])

                try:
                    leave_message = await leave_log_channel.fetch_message(staff['leave']['message_id'])
                except discord.NotFound:
                    return

                embed = leave_message.embeds[0]
                embed.title = f"{embed.title} (Ended)"

                await leave_message.edit(embed=embed)
                for post in staff['post']:
                    role = discord.utils.get(main_guild.roles, id=staff_list[post])
                    await staff_member.add_roles(role, reason="Staff leave ended")
                await staff_member.remove_roles(leave_role, reason="Staff leave ended")
                await self.bot.staff.unset(staff['_id'], 'leave')
                try:
                    await staff_member.send("Your Staff leave in **The Gambler's Kingdom** has ended, if you want to extend your leave, please contact a Head Administator.")
                except discord.HTTPException:
                    pass
        
    @leave_task.before_loop
    async def before_leave_task(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="appoint", description="appoint staff to user")
    @app_commands.choices(post=[app_commands.Choice(name="Moderator", value=str(787259553225637889)),app_commands.Choice(name="TRIAL MODERATOR", value=str(843775369470672916)), app_commands.Choice(name="Partnership Manager", value=str(831405039830564875)), app_commands.Choice(name="Giveaway Manager", value=str(803230347575820289)), app_commands.Choice(name="Event Manager", value=str(852125566802198528))])
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
                    if "Head Administator" in staff['post']:
                        hadmin.description += f"<@{staff['_id']}>\n"
                    if "Administator" in staff['post']:
                        admin.description += f"<@{staff['_id']}>\n"
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
                await Paginator(interaction, embeds).start(embeded=True, quick_navigation=False)
            if short:
                embed = discord.Embed(title=short.name, color=discord.Color.green(), description="")
                for staff in staff_list:
                    if staff['post'] == []:
                        continue
                    if short.name in staff['post']:
                        embed.description += f"<@{staff['_id']}>\n"
                await interaction.response.send_message(embed=embed)
    
    @leave.command(name="set", description="set leave for a staff member")
    @app_commands.describe(member="Member to set leave for", days="Days of leave", reason="Reason for leave")
    async def _set(self, interaction: discord.Interaction, member: discord.Member, days: app_commands.Range[int,1, 30], reason: str):
        data = await self.bot.staff.find(member.id)
        if not data:
            await interaction.response.send_message(f"{member.mention} is not staff", ephemeral=True)
            return
        if 'leave' in data.keys():
            await interaction.response.send_message(f"{member.mention} already on leave", ephemeral=True)
            return

        await interaction.response.send_message(f"Setting leave for {member.mention}", ephemeral=False, allowed_mentions=discord.AllowedMentions(users=False))
        data['leave'] = {'days': days, 'reason': reason, 'start': datetime.datetime.now(), 'end': datetime.datetime.now() + datetime.timedelta(days=days), 'approved_by': interaction.user.id}
        

        embed = discord.Embed(title=f"{member.name} is on leave", description=f"", color=discord.Color.green())
        embed.add_field(name="Days", value=days, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Start", value=datetime.datetime.now().strftime("%d %B %Y"), inline=False)
        embed.add_field(name="End", value=(datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%d %B %Y"), inline=False)
        embed.add_field(name="Approved by", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"Leave Ends")
        embed.timestamp = datetime.datetime.now() + datetime.timedelta(days=days)
        channel = self.bot.get_channel(974913093266182144)
        msg = await channel.send(embed=embed)
        data['leave']['message_id'] = msg.id
        await self.bot.staff.update(data)

        for post in data['post']:
            role = discord.utils.get(interaction.guild.roles, id=staff_list[post])
            await member.remove_roles(role, reason=f"Leave for {days} days")
        
        leave_role = discord.utils.get(interaction.guild.roles, id=787055415157850142)
        await member.add_roles(leave_role, reason=f"Leave for {days} days")
        await interaction.edit_original_response(content=f"Leave set for {member.mention}")
    
    @leave.command(name="remove", description="remove leave for a staff member")
    @app_commands.describe(member="Member to remove leave for")
    async def _remove(self, interaction: discord.Interaction, member: discord.Member):
        data = await self.bot.staff.find(member.id)
        if not data:
            await interaction.response.send_message(f"{member.mention} is not staff", ephemeral=True)
            return
        if 'leave' not in data.keys():
            await interaction.response.send_message(f"{member.mention} is not on leave", ephemeral=True)
            return

        await interaction.response.send_message(f"Removing leave for {member.mention}", ephemeral=False, allowed_mentions=discord.AllowedMentions(users=False))
        await self.bot.staff.unset(data, 'leave')

        embed = discord.Embed(title=f"{member.name} leave removed", description=f"Leave removed by {interaction.user.name}", color=discord.Color.green())
        channel = self.bot.get_channel(974913093266182144)
        await channel.send(embed=embed)

        for post in data['post']:
            role = discord.utils.get(interaction.guild.roles, id=staff_list[post])
            await member.add_roles(role, reason=f"Leave removed")
        
        leave_role = discord.utils.get(interaction.guild.roles, id=787055415157850142)
        await member.remove_roles(leave_role, reason=f"Leave removed")
        await interaction.edit_original_response(content=f"Leave removed for {member.mention}")
    
    @app_commands.command(name='gen-key', description="Generate a key for a staff member")
    @app_commands.describe(member="Member to generate key for")
    async def _gen_key(self, interaction: discord.Interaction, member: discord.Member):
        #generate key of 10 random characters and numbers with uppercase and lowercase letters
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        data = await self.bot.staff.find(member.id)
        if not data:
            await interaction.response.send_message(f"{member.mention} is not staff", ephemeral=True)
            return
        if data['recovery_code'] != None:
            await interaction.response.send_message(f"{member.mention} already has a recovery code", ephemeral=True)
            return
        
        data['recovery_code'] = key
        await self.bot.staff.update(data)
        await interaction.response.send_message(f"Recovery code for {member.mention} successfully generated", ephemeral=True)
        try:
            embed = discord.Embed(title="Recovery Code", description=f"", color=discord.Color.green())
            embed.description = "You have received a recovery code incase you lost access to your current discord account,"
            embed.description += "If you have lost access to your current discord account, you can use this code to recover your staff account,"
            embed.description += "To recover your account use the command `-recover <code>` in my DMs with account your other account."
            embed.description += "\n\n**Please keep this code safe and do not share it with anyone.**"
            embed.description += "\n**Higer staff members/owners or anyone will never ask you for this code.**"
            embed.add_field(name="Recovery Code", value=key, inline=False)
            await member.send(embed=embed)
            await interaction.edit_original_response(content=f"Recovery code for {member.mention} successfully generated and sent to them")
        except:
            await interaction.edit_original_response(content=f"Recovery code for {member.mention} successfully generated but could not send to them")
            data['recovery_code'] = None
            await self.bot.staff.update(data)

    @commands.command(name='recover', description="Recover a staff account")
    @commands.dm_only()
    async def _recover(self, ctx, code):
        #check if channel is DMs
        if ctx.guild:
            return
        #check if code is valid
        data = await self.bot.staff.find_by_custom({'recovery_code': code})
        if not data:
            await ctx.message.add_reaction('❌')
            return
        staff_member = self.bot.get_user(data['_id'])
        embed = discord.Embed(title="Recovery Code", description=f"", color=discord.Color.green())
        embed.description += f"Do you want to recover {staff_member.name}#{staff_member.discriminator} account?\n"
        embed.description += "Using this code will invalidate the code and you will not be able to use it again.\n"
        embed.description += "you need to have request new code after successful recovery."
        embed.set_footer(text=f"reply with yes or no")
        await ctx.send(embed=embed)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send('Timed out, please try again.')
            return
        if msg.content.lower() == 'yes':
            data['recovery_code'] = None
            data['recovery_user'] = ctx.author.id
            await self.bot.staff.update(data)
            await ctx.send(f"Your account recovery request has been sent to server owners. Please wait for them to accept your request.")
        else:
            return await ctx.send(f"Recovery request cancelled")
        
        admin_channel = self.bot.get_channel(792246185238069249)
        embed = discord.Embed(title="Recovery Code", description=f"", color=discord.Color.green())
        embed.description += f"User {ctx.author.mention} wants to recover {staff_member.mention} account."
        await admin_channel.send(embed=embed, content="@here")

        
async def setup(bot):
    await bot.add_cog(Staff(bot), guilds=[discord.Object(785839283847954433)])
    