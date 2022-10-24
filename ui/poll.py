import discord
from discord import Interaction
import discord.ui as ui
import datetime
from utils.converter import TimeConverter
from humanfriendly import format_timespan
from typing import Union

def bar():
    return (f"`┃          ┃`")

def update_bar(total, count):
    return (f"`┃{'█' * int(count/total*10)}{' ' * int(10-count/total*10)}┃`")

default_emoji = ['<a:Number1:1034099314877812818>', '<a:Number2:1034099538371280989>', '<a:Number3:1034099610886615110>', '<a:Number4:1034099702205005834>', '<a:Number5:1034099793544364103>', '<a:Number6:1034100138135797780>', '<a:Number7:1034100185539821608>', '<a:Number8:1034100344000618526>', '<a:Number9:1034100403387777045>']
booleanEmoji = ["✅", "❌"]

async def make_poll(interaction: discord.Interaction, title:str, options:str, duration:str, thread:bool=False):
    await interaction.response.defer(thinking=True)
    options = options.split("!")

    if len(options) < 2:
        await interaction.followup.send("You need at least 2 options to make a poll.")
        return
    elif len(options) > 9:
        await interaction.followup.send("You can only have 9 options max.")
        return
    
    #check if len of options is odd or even
    if len(options) % 2 == 0:
        inline=False
    else:
        inline=True

    poll_data = {'options': {}}
    for option in options:
        poll_data['options'][str(options.index(option))] = {'count': 0, 'users': []}
    poll_duration = await TimeConverter().convert(interaction, duration)
    poll_duration_seconds = poll_duration
    poll_duration = datetime.datetime.now() + datetime.timedelta(seconds=poll_duration)
    poll_duration_TIMESTAMP = round(poll_duration.timestamp())

    embed = discord.Embed(title=title, description="")
    for option in options:
        embed.add_field(name=f"{default_emoji[options.index(option)]} {option}", value=bar(), inline=inline)
    embed.description += "\n\n"
    embed.description += f"**Poll Duration:** {format_timespan(poll_duration_seconds)}\n"
    embed.description += f"**Poll Ends:** <t:{poll_duration_TIMESTAMP}:R>\n"
    embed.description += f"**Total Votes:** 0"
    embed.set_footer(text=f"Poll Started by {interaction.user}")
    embed.color = discord.Color.random()
    embed.timestamp = datetime.datetime.now()

    await interaction.followup.send(embed=embed , view=PollView(poll_data))
    poll_message = await interaction.original_response()
    if thread:
        await poll_message.create_thread(name=f"Poll: {title}", auto_archive_duration=60)
    
    poll_data['_id'] = poll_message.id
    poll_data['channel'] = poll_message.channel.id
    poll_data['guild'] = poll_message.guild.id
    poll_data['author'] = poll_message.author.id
    poll_data['total_votes'] = 0
    poll_data['end_time'] = poll_duration
    interaction.client.polls[poll_message.id] = poll_data
    await interaction.client.poll.insert(poll_data)

    await interaction.followup.send("Poll created successfully.", ephemeral=True)

async def update_poll(interaction: discord.Interaction, poll_data: dict, current_option: int,user: Union[discord.Member, discord.User]):
    poll_data_copy = poll_data.copy()
    embed = interaction.message.embeds[0]
    current_option_data = poll_data_copy['options'][str(current_option)]

    if user.id in current_option_data['users']:
        current_option_data['count'] -= 1
        current_option_data['users'].remove(user.id)
        poll_data_copy['total_votes'] -= 1

        embed_response = discord.Embed(description=f"You have successfully removed your vote from {embed.fields[int(current_option)].name}", color=discord.Color.red())

        for field in embed.fields:
            if poll_data_copy['options'][str(embed.fields.index(field))]['count'] > 0:
                embed.set_field_at(embed.fields.index(field), name=field.name, value=update_bar(poll_data_copy['total_votes'], poll_data_copy['options'][str(embed.fields.index(field))]['count']), inline=field.inline)
            else:
                embed.set_field_at(embed.fields.index(field), name=field.name, value=bar(), inline=field.inline)
        new_description = embed.description.replace(f"**Total Votes:** {poll_data['total_votes']}", f"**Total Votes:** {poll_data_copy['total_votes']}")
        embed.description = new_description

        await interaction.message.edit(embed=embed)
        await interaction.followup.send(embed=embed_response, ephemeral=True)
        await interaction.client.poll.update(poll_data_copy)
        interaction.client.polls[poll_data_copy['_id']] = poll_data_copy

    else:
        changed_option = False
        for option in poll_data_copy['options']:
            if user.id in poll_data_copy['options'][option]['users']:
                poll_data_copy['options'][option]['users'].remove(user.id)
                poll_data_copy['options'][option]['count'] -= 1
                poll_data_copy['total_votes'] -= 1

                poll_data_copy['options'][str(current_option)]['users'].append(user.id)
                poll_data_copy['options'][str(current_option)]['count'] += 1
                poll_data_copy['total_votes'] += 1

                for field in embed.fields:
                    if poll_data_copy['options'][str(embed.fields.index(field))]['count'] > 0:
                        embed.set_field_at(embed.fields.index(field), name=field.name, value=update_bar(poll_data_copy['total_votes'], poll_data_copy['options'][str(embed.fields.index(field))]['count']), inline=field.inline)
                    else:
                        embed.set_field_at(embed.fields.index(field), name=field.name, value=bar(), inline=field.inline)
                new_description = embed.description.replace(f"**Total Votes:** {poll_data['total_votes']}", f"**Total Votes:** {poll_data_copy['total_votes']}")
                embed.description = new_description
                
                embed_response = discord.Embed(description=f"You have successfully changed your vote from {embed.fields[int(option)].name} to {embed.fields[int(current_option)].name}", color=discord.Color.green())
                
                await interaction.message.edit(embed=embed)
                await interaction.followup.send(embed=embed_response, ephemeral=True)
                await interaction.client.poll.update(poll_data_copy)
                interaction.client.polls[poll_data_copy['_id']] = poll_data_copy
                changed_option = True
                break

        if changed_option == False:
            poll_data_copy['options'][str(current_option)]['users'].append(user.id)
            poll_data_copy['options'][str(current_option)]['count'] += 1
            poll_data_copy['total_votes'] += 1

            for field in embed.fields:
                if poll_data_copy['options'][str(embed.fields.index(field))]['count'] > 0:
                    embed.set_field_at(embed.fields.index(field), name=field.name, value=update_bar(poll_data_copy['total_votes'], poll_data_copy['options'][str(embed.fields.index(field))]['count']), inline=field.inline)
                else:
                    embed.set_field_at(embed.fields.index(field), name=field.name, value=bar(), inline=field.inline)
                    
            new_description = embed.description.replace(f"**Total Votes:** {poll_data['total_votes']}", f"**Total Votes:** {poll_data_copy['total_votes']}")
            embed.description = new_description

            embed_response = discord.Embed(description=f"You have successfully voted for {embed.fields[int(current_option)].name}", color=discord.Color.green())
            
            await interaction.message.edit(embed=embed)
            await interaction.client.poll.update(poll_data_copy)
            interaction.client.polls[poll_data_copy['_id']] = poll_data_copy
            await interaction.followup.send(embed=embed_response, ephemeral=True)
            

class PollButton(discord.ui.Button):
    async def callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.message.id not in interaction.client.polls:
            await interaction.followup.send("This poll has expired./invalid poll")
            return
        
        poll_data = interaction.client.polls[interaction.message.id]
        if not poll_data:
            poll_data = await interaction.client.poll.find(interaction.message.id)
            if not poll_data:
                await interaction.response.send_message("This poll has expired./invalid poll", ephemeral=True)
        
        print(interaction.data)
        poll_option = interaction.data['custom_id'].split(":")[-1]
        if poll_option not in poll_data['options'].keys():
            await interaction.followup.send("This poll has expired./invalid poll")
            return
        print("got option data")

        await update_poll(interaction, poll_data, poll_option, interaction.user)


class PollView(discord.ui.View):
    def __init__(self, poll_data: dict):
        print("loading poll view")
        super().__init__(timeout=None)
        k = 0
        for i in poll_data['options'].keys():
            self.add_item(PollButton(emoji=default_emoji[k], custom_id=f"POLL:BUTTON:{k}", style=discord.ButtonStyle.blurple))
            k += 1

