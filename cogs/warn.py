import datetime
import discord
import re
import asyncio
# ----------------------
from bson.objectid import ObjectId
from discord.ext import commands
from utils.util import Pag

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
description = "Warnings System"


class Warns(commands.Cog, description=description):
    def __init__(self, bot):
        self.bot = bot

    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307, 301657045248114690]
        return commands.check(predicate)

    def perm_check():
        async def predicate(ctx):
            mod_role = [785842380565774368, 803635405638991902, 799037944735727636,
                        785845265118265376, 787259553225637889, 843775369470672916]
            for mod in mod_role:
                role = discord.utils.get(ctx.guild.roles, id=mod)
                if role in ctx.author.roles:
                    permissions = await ctx.bot.config.find(role.id)
                    check = permissions['perm']
                    return (ctx.command.name in check)
        return commands.check(predicate)

    @commands.command(name="Warnings", description="Show All Warnings for User", usage="[member]")
    @commands.check_any(perm_check(), is_me())
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
    @commands.check_any(perm_check(), is_me())
    async def delwarn(self, ctx, *, _id):

        warns_filter = {"_id": ObjectId(_id)}

        await self.bot.warns.delete_by_custom(warns_filter)

        embed = discord.Embed(
            color=0x02ff06, description=f"Deleted Warning by ID `{_id}`")

        await ctx.send(embed=embed)

    @commands.command(name="clearwarn", description="Clear all warnings form user", usage="[member]")
    @commands.check_any(perm_check(), is_me())
    async def clearwarn(self, ctx, member: discord.Member = None):
        member = member if member else ctx.author

        if member.id == ctx.author.id:
            await ctx.send("you can't clear your own warn")

        warn_filter = {"user_id": member.id}

        await self.bot.warns.delete_by_custom(warn_filter)

        await ctx.send(f"Cleared all warnings form the {member.display_name}")

    @commands.group(name="tasks", description="Simpal Task command", invoke_without_command=True)
    @commands.check_any(commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916), is_me())
    async def tasks(self, ctx, member: discord.Member = None):
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
    @commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376)
    async def add(self, ctx, member: discord.Member = None, *, task):
        member = member if member else ctx.author
        # if member == ctx.author:
        # return await ctx.send("Your can't give task to your self or you can?")

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

        task_filter = {'user_id': member.id,
                       'guild_id': ctx.guild.id, 'task_count': current_task_count}
        task_data = {'task': task,
                     'timestamp': datetime.datetime.now(), 'status': status}

        await self.bot.tasks.upsert_custom(task_filter, task_data)
        embed = discord.Embed(
            description="Your Task is successfully assigned", color=0xFFFFFF)
        await ctx.message.delete()
        dm_embed = discord.Embed(
            description=f"You have Got New Task\nTask: {task}\nTotal Task: {current_task_count} \nTask By: {ctx.author.name}")
        try:
            await member.send(embed=dm_embed)
        except discord.HTTPException:
            pass
        await ctx.send(embed=embed)

    @tasks.command(name="update")
    @commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376, 787259553225637889, 843775369470672916)
    async def update(self, ctx, task_id, *, status=None):

        if status is None:
            await ctx.send("pleas Send Status for the Task")

        task_filter = {'_id': ObjectId(task_id), 'user_id': ctx.author.id}
        tasks = await self.bot.tasks.find_many_by_custom(task_filter)

        if not bool(tasks):
            return await ctx.send("please Send ckeck your task id and your can't cahnnge other's task status")
        task_data = {'status': status}
        await self.bot.tasks.update_by_custom(task_filter, task_data)
        await ctx.send("Task updated")
        await ctx.message.delete()

    @tasks.command(name="remove")
    @commands.has_any_role(785842380565774368, 803635405638991902, 799037944735727636, 785845265118265376)
    async def remove(self, ctx, *, tasks_id):
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
    @commands.has_any_role(785842380565774368, 803635405638991902)
    async def purge(self, ctx, member: discord.Member = None):
        member = member if member else ctx.author

        task_filter = {
            'user_id': member.id,
            'status': 'Done'
        }
        task = len(await self.bot.tasks.find_many_by_custom(task_filter))

        await ctx.send(f"You want to Clear {task} From the {member.mention}")
        try:
            await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.startswith("y") or m.content.startswith("Y"), timeout=15)
            await self.bot.tasks.delete_by_custom(task_filter)
            await ctx.send("Tasks Removed")
        except asyncio.TimeoutError:
            await ctx.send("canceling The commands")


def setup(bot):
    bot.add_cog(Warns(bot))
