import re
import discord
import datetime
#----------------------
from bson.objectid import ObjectId
from discord.ext import commands
from utils.util import Pag

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
description = "Warnings System"


class Warns(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot
		
    @commands.command(name="Warn", description="Gives an Warnings to user", usage="[member] [warn]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def warn(self, ctx, member: discord.Member, *, reason):
        await ctx.message.delete()
        if member.id in [self.bot.user.id, 488614633670967307, 301657045248114690]:
            return await ctx.send("You cannot warn bot or it's Creater because they are way too cool to be warned")

        if member.id == ctx.author.id:
            return await ctx.send("You cannot warn your self")
        

        
        current_warn_count = len(
            await self.bot.warns.find_many_by_custom(
                {
                    "user_id": member.id,
                    "guild_id": member.guild.id
                }
            )
        ) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}
        
        await self.bot.warns.upsert_custom(warn_filter, warn_data)  
            
        try:
            await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
            em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count}**")
            await ctx.send(embed=em)
        except discord.HTTPException:
            emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been Warned I couldn't DM them.| Warnings Count {current_warn_count}**")
            await ctx.send(embed=emb)
        
        try:
            log_channel = self.bot.get_channel(803687264110247987)

            embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
            embed.add_field(name="User", value=f"{member.name}", inline=False)
            embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
            embed.add_field(name="threshold Action", value="None")
            embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

            await log_channel.send(embed=embed)
        except:
            pass

    @commands.command(name="Warnings", description="Show All Warnings for User", usage="[member]")
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def Warnings(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)
        
        if not bool(warns):
            return await ctx.send(f"Couldn't find any warns for: `{member.display_name}`")
        
        warns = sorted(warns, key=lambda x: x["number"])
        
        pages = []
        for warn in warns:
            description = f"""
            Warn id: `{warn['_id']}`
            Warn Number: `{warn['number']}`
            Warn Reason: `{warn['reason']}`
            Warned By: <@{warn['warned_by']}>
            Warn Time: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)

        await Pag(
            title=f"Warns for `{member.display_name}`",
            colour=0xCE2029,
            entries=pages,
            length=2
        ).start(ctx)

    @commands.command(name="delwarn", description="Delete Warning For user", usage="[Warn_id]")
    @commands.has_any_role(785842380565774368, 799037944735727636)
    async def delwarn(self, ctx, *,_id):

        warns_filter = {"_id": ObjectId(_id)}

        await self.bot.warns.delete_by_custom(warns_filter)

        embed = discord.Embed(color=0x02ff06, description=f"Deleted Warning by ID `{_id}`")

        await ctx.send(embed=embed)

    @commands.command(name="clearwarn", description="Clear all warnings form user", usage="[member]")
    @commands.has_any_role(785842380565774368)
    async def clearwarn(self, ctx, member: discord.Member=None):
        member = member if member else ctx.author

        if member.id == ctx.author.id:
            await ctx.send("you can't clear your own warn")

        warn_filter = {"user_id": member.id}

        await self.bot.warns.delete_by_custom(warn_filter)

        await ctx.send(f"Cleared all warnings form the {member.display_name}")

    @commands.group(name="tasks" ,description="Simpal Task command" ,invoke_without_command = True)
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def tasks(self, ctx, member: discord.Member=None):
        member = member if member else ctx.author
        tasks_filter = {
        "user_id": member.id,
        "guild_id": ctx.guild.id

        }
        tasks = await self.bot.tasks.find_many_by_custom(tasks_filter)
        
        if not bool(tasks):
            return await ctx.send(f"No Taks is Left to do")
        
        tasks = sorted(tasks, key=lambda x: x["task_count"])
        
        pages = []
        for task in tasks:
            description = f"""
            Task id: `{task['_id']}`
            Task Number: `{task['task_count']}`
            Task : `{task['task']}`
            Task Status: `{task['status']}`
            Task By: <@{task['user_id']}>
            Task File: {task['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)

        await Pag(
            title=f"Showing the Task for the {member.display_name}",
            colour=0xCE2029,
            entries=pages,
            length=2
        ).start(ctx)

    @tasks.command(name="add", description="", usage=" [user] [task]")
    @commands.has_any_role(785842380565774368,799037944735727636)
    async def add(self, ctx, member: discord.Member=None, *,task):
        member = member if member else ctx.author
        #if member == ctx.author:
            #return await ctx.send("Your can't give task to your self or you can?")

        status = "Pending"
        current_task_count = len(
            await self.bot.tasks.find_many_by_custom(
            {   
                "user_id": member.id,
                "guild_id": ctx.guild.id
            }
            
            )
        )+1

        if current_task_count >= 10:
            return await ctx.send("User has maximum task reached")

        task_filter = {'user_id': member.id, 'guild_id': ctx.guild.id, 'task_count': current_task_count}
        task_data = {'task': task, 'timestamp': datetime.datetime.now(), 'status': status}

        await self.bot.tasks.upsert_custom(task_filter, task_data)
        embed = discord.Embed(description="Your Task is successfully assigned", color=0xFFFFFF)
        await ctx.message.delete()
        dm_embed = discord.Embed(description=f"You have Got New Task\nTask: {task}\nTotal Task: {current_task_count} \nTask By: {ctx.author.name}")
        try:
            await member.send(embed=dm_embed)
        except discord.HTTPException:
            pass
        await ctx.send(embed=embed)
 
    @tasks.command(name="update")       
    @commands.has_any_role(785842380565774368,799037944735727636, 785845265118265376, 787259553225637889)
    async def update(self, ctx, task_id, *,status=None):
        
        if status is None:
            await ctx.send("pleas Send Status for the Task")

        task_filter = { '_id': ObjectId(task_id), 'user_id': ctx.author.id}
        tasks = await self.bot.tasks.find_many_by_custom(task_filter)

        if not bool(tasks):
            return await ctx.send("please Send ckeck your task id and your can't cahnnge other's task status")
        task_data = {'status': status}
        await self.bot.tasks.update_by_custom(task_filter, task_data)
        await ctx.send("Task updated")
        await ctx.message.delete()

    @tasks.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *,tasks_id):
        task_filter = {
        '_id': ObjectId(tasks_id),
        }
        tasks = await self.bot.tasks.find_many_by_custom(task_filter)

        for task in tasks:
            await ctx.send(f"Are you Sure you want to remvoe the {task['task']} for the user <@{task['user_id']}> [y/n]")
            try:
                await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.content.startswith("y") or m.content.startswith("Y"), timeout=60)
                await self.bot.tasks.delete_by_custom(task_filter)
                await ctx.send("Task Removed")
            except asyncio.TimeoutError:
                await ctx.send("timeout try again")

    @tasks.command(nmae="purge",)
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, member: discord.Member=None):
        member = member if member else ctx.author

        task_filter = {
        'user_id': member.id,
        'status' : 'Done'
        }
        task = len(await self.bot.tasks.find_many_by_custom(task_filter))

        await ctx.send(f"You want to Clear {task} From the {member.mention}")
        try:
            await self.bot.wait_for("message", check=lambda m: m.author.id==ctx.author.id and m.channel.id== ctx.channel.id and m.content.startswith("y") or m.content.startswith("Y"), timeout=15)
            await self.bot.tasks.delete_by_custom(task_filter)
            await ctx.send("Tasks Removed")
        except asyncio.TimeoutError:
            await ctx.send("canceling The commands")


def setup(bot):
    bot.add_cog(Warns(bot))
"""
        embed = discord.Embed(
            title="You are being warned:",
            description=f"__**Reason**__:\n{reason}",
            colour=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Warn: {current_warn_count}")
"""



"""
    @commands.command(name="delwarn", description="Delete Warnings For User", usage="[warn_id]")
    @commands.has_permissions(administrator=True)
    async def delwarn(self, ctx, member: discord.Member, warn_id):



        warn_filter = {"_id": warn_id, "user_id": member.id}
        await self.bot.warns.delete(warn_filter)

        await ctx.send("Done")
    
        warn_filter = {"_id": f"{warn_id}"}
        await self.bot.warns.delete(warn_id)

        await ctx.send(f"{warns}")
        await ctx.send(f"---------\n")
        await ctx.send(f"{Warns}")

        embed = discord.Embed(color=0x06f79e,description=f'<:allow:819194696874197004> The Warnings is Deleted')

        await ctx.send(embed=embed)
"""







"""
if current_warn_count == 5:

            data = {
                '_id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': 1140,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }

            await self.bot.mutes.upsert(data)
            self.bot.muted_users[member.id] = data

            await member.add_roles(role)

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Frist threshold Reached Muted You have been muted for 1 Day")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Frist threshold Reached Muted User for 1 Day **")
                await ctx.send(embed=em)
                
                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Day")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Frist threshold Reached Muted User for 1 Day |Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Day")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

        elif current_warn_count == 10:

            data = {
                '_id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': 10080,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }

            await self.bot.mutes.upsert(data)
            self.bot.muted_users[member.id] = data

            await member.add_roles(role)

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Second threshold Reached Muted YOu have been for muted 1 Week")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Second threshold Reached Muted User for 1 Week **")
                await ctx.send(embed=em)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Week")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Second threshold Reached Muted User for 1 Day |Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Muted For Week")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


        elif current_warn_count == 15:
            
            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count} | Third threshold Reached You have Been Kicked")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Third threshold Reached user Has Been Kicked **")
                await ctx.send(embed=em)
                await ctx.guild.kick(user=member, reason=f"15 Warnings Reached")
                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Kicked")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)


            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Third threshold Reached user Has Been Kicked | Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)
                await ctx.guild.kick(user=member, reason=f"15 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Kicked")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)

        elif current_warn_count == 20:

            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count} | Third threshold Reached user Has Been Banned **")
                await ctx.send(embed=em)
                await ctx.guild.ban(user=member, reason=f"20 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Banned")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)
                
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} | {reason} | Warnings Count {current_warn_count} | Third threshold Reached user Has Been Banned | Has Been Warned I couldn't DM them.**")
                await ctx.send(embed=emb)
                await ctx.guild.ban(user=member, reason=f"20 Warnings Reached")

                log_channel = self.bot.get_channel(803687264110247987)

                embed = discord.Embed(color=0x06f79e, title=f"Warned | {member.name}")
                embed.add_field(name="User", value=f"{member.name}", inline=False)
                embed.add_field(name="Moderator", value=f"{ctx.author.mention}", inline=False)
                embed.add_field(name="Reason", value=f"{reason}", inline=False)
                embed.add_field(name="Warnings Count", value=f"{current_warn_count}")
                embed.add_field(name="threshold Action", value="Banned")
                embed.set_footer(text=f"{member.id}", icon_url=member.avatar_url)

                await log_channel.send(embed=embed)
        
        else:  
            
            try:
                await member.send(f"You Have Been Warned | {reason} | Warnings Count {current_warn_count}")
                em = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **{member.name} Has been Warned | {reason} |Warnings Count {current_warn_count}**")
                await ctx.send(embed=em)
            except discord.HTTPException:
                emb = discord.Embed(color=0x06f79e, description=f"<:allow:819194696874197004> **The User {member.name} Has Been Warned I couldn't DM them.| Warnings Count {current_warn_count}**")
                await ctx.send(embed=emb)
"""