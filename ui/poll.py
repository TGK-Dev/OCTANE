import discord
from discord import Interaction
import discord.ui as ui
import datetime
from utils.converter import TimeConverter
def bar():
    return (f"`┃          ┃`")

def update_bar(total, count):
    return (f"`┃{'█' * int(count/total*10)}{' ' * int(10-count/total*10)}┃`")

default_emoji = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split(" ")
booleanEmoji = ["✅", "❌"]

async def make_poll(interaction: discord.Interaction, title:str, options:str, duration:str, thread:bool=False, one_vote:bool=True):
    await interaction.response.defer(thinking=True)
    options = options.split("!")

    if len(options) < 2:
        await interaction.followup.send("You need at least 2 options to make a poll.")
        return
    elif len(options) > 10:
        await interaction.followup.send("You can only have 10 options max.")
        return
    
    #check if len of options is odd or even
    if len(options) % 2 == 0:
        inline=False
    else:
        inline=True

    poll_data = {'options': {}}
    duration = await TimeConverter().convert(interaction, duration)
    duration = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    durationSTAMP = round(duration.timestamp())

    embed = discord.Embed(title=title)
    for i in range(len(options)):
        poll_data['options'][str(i)] = {'name': options[i], 'votes': 0, 'users': []}
        embed.add_field(name=f"{default_emoji[i]} {options[i]}", value=bar(), inline=inline)
    embed.set_footer(text=f"Asked by {interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
    embed.description = "• 0 votes\n"
    if one_vote == False:
        embed.description += "• Multiple votes\n"
    else:
        embed.description += "• One vote per user\n"
    embed.description += f"• Duration: <t:{durationSTAMP}:R>"
    embed.color = discord.Color.random()
    await interaction.followup.send(embed=embed, view=PollView(embed))

    msg = await interaction.original_response()
    poll_data['_id'] = msg.id
    poll_data['channel'] = msg.channel.id
    poll_data['author'] = msg.author.id
    poll_data['title'] = title
    poll_data['total_votes'] = 0
    poll_data['end_time'] = duration
    poll_data['one_vote'] = one_vote
    interaction.client.polls[msg.id] = poll_data

    await interaction.client.poll.insert(poll_data)

    if thread:
        await msg.create_thread(name=title, slowmode_delay=3)

class PollButton(discord.ui.Button):
    async def callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        if interaction.message.id not in interaction.client.polls:
            await interaction.followup.send("This poll has expired./invalid poll")
            return
        
        data = interaction.client.polls[interaction.message.id]
        index = default_emoji.index(self.emoji.name)

        if str(index) not in data['options']:
            await interaction.followup.send("This option does not exist.")
            return

        #check if user has already voted
        if interaction.user.id in data['options'][str(index)]['users']:
            await interaction.followup.send("You have already voted for this option.")
            return
        
        #check if user has voted for another option
        if data['one_vote'] == True:
            for i in data['options']:
                if interaction.user.id in data['options'][i]['users']:
                    data['options'][i]['users'].remove(interaction.user.id)
                    data['options'][i]['votes'] -= 1
                    data['total_votes'] -= 1
                    break

        
        option = data['options'][str(index)]
        option['users'].append(interaction.user.id)
        option['votes'] += 1
        data['total_votes'] += 1

        embed = interaction.message.embeds[0]
        #update embed with new bar
        k = 0
        for i in embed.fields:
            embed.set_field_at(k, name=i.name, value=update_bar(data['total_votes'], data['options'][str(k)]['votes']))
            k += 1
        #find • {number} votes and update
        description = embed.description.split("\n")
        for i in range(len(description)):
            if "votes" in description[i]:
                description[i] = f"• {data['total_votes']} votes"
                break
        embed.description = "\n".join(description)

        await interaction.message.edit(embed=embed)

        await interaction.followup.send(f"You have successfully voted for {option['name']}.")
        await interaction.client.poll.update(data)    

class PollView(discord.ui.View):
    def __init__(self, embed: discord.Embed=None):
        super().__init__(timeout=None)
        k = 0
        for i in embed.fields:
            name = i.name.split(" ")
            btn = PollButton(emoji=default_emoji[k], custom_id=f"POLL:BUTTON:{k}", style=discord.ButtonStyle.blurple)
            k += 1
            self.add_item(btn)
