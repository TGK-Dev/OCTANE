import discord
from utils.converter import millify
from utils.functions import make_inv


class Booster_main(discord.ui.View):
    def __init__(self, bot, interaction: discord.Interaction):
        self.bot = bot
        self.interaction = interaction
        self.message = None
        super().__init__(timeout=30)

    @discord.ui.button(label="1x Booster", custom_id="1x", style=discord.ButtonStyle.green)
    async def onex(self, interaction: discord.Interaction, button: discord.ui.Button):

        bal = await self.bot.eco_api.get_user_bal(interaction.guild.id, self.interaction.user.id)
        self.add_item(onexbooster(self.bot, self.interaction, self.message, bal))    

        embed = discord.Embed(title="Select Exp booster",color=discord.Color.random())
        embed.add_field(name="Bank Info", value=f"Cash: `{millify(bal['cash'])}`\nBank: `{millify(bal['bank'])}`\nTotal: `{millify(bal['total'])}`", inline=False)
        embed.add_field(name="Duration: 12h", value="**Price** 14k", inline=True)
        embed.add_field(name="Duration: 24h", value="**Price** 26k", inline=True)
        embed.add_field(name="Duration: 48h", value="**Price** 50k", inline=True)
        embed.add_field(name="Duration: 72h", value="**Price** 74k", inline=True)
        button.disabled = True
        await interaction.response.edit_message(view=self, embed=embed)
    
    @discord.ui.button(label="2x Booster", custom_id="2x", style=discord.ButtonStyle.blurple, disabled=True)
    async def twox(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("This is not available yet", ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.interaction.user.id:
            return True
        else:
            await interaction.response.send_message("This is not your booster store", ephemeral=True)
        
    async def on_timeout(self):
        for i in self.children:
            i.disabled=True        
        await self.message.edit(view=self)

class onexbooster(discord.ui.Select):
    def __init__(self, bot,interaction:discord.Interaction, message: discord.Message, bal):
        self.bot = bot
        self.interaction = interaction
        self.message = message
        self.bal = bal

        options = [
            discord.SelectOption(label="Duration: 12 hours", value="12h"),
            discord.SelectOption(label="Duration: 24 hours", value="24h"),
            discord.SelectOption(label="Duration: 48 hours", value="48h"),
            discord.SelectOption(label="Duration: 72 hours", value="72h"),
        ]
        super().__init__(options=options, placeholder="Select a duration", max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        match self.values[0]:
            case "12h":

                if self.bal['cash'] < 14000:
                    await interaction.response.send_message(f"You don't have enough cash to buy this booster", ephemeral=True)
                    return
                elif self.bal['cash'] >= 14000:

                    data = await self.bot.inv.find(interaction.user.id)
                    if not data:
                        data = make_inv(interaction.user.id)
                        await self.bot.inv.insert(data)

                    for i in data["onex"]:
                        if i['name'] == '12 Hour':
                            if i['quantity'] == 10:
                                await interaction.response.send_message(f"You can't buy more than 10 boosters", ephemeral=True)
                                return
                            i['quantity'] += 1
                            await self.bot.inv.update(data)
                            await self.bot.eco_api.patch_user_bal(interaction.guild.id, interaction.user.id, -14000, 0, reason="bought onex booster for 12 hours")
                            break
                    await interaction.response.send_message(f"You have bought a booster for 12 hours", ephemeral=True)

            case "24h":
                if self.bal['cash'] < 26000:
                    await interaction.response.send_message(f"You don't have enough cash to buy this booster", ephemeral=True)
                    return
                elif self.bal['cash'] >= 26000:                    
                    data = await self.bot.inv.find(interaction.user.id)
                    if not data:
                        data = make_inv(interaction.user.id)
                        await self.bot.inv.insert(data)

                    for i in data["onex"]:
                        if i['name'] == '24 Hour':
                            if i['quantity'] == 10:
                                await interaction.response.send_message(f"You can't buy more than 10 boosters", ephemeral=True)
                                return
                            i['quantity'] += 1
                            await self.bot.inv.update(data)
                            await self.bot.eco_api.patch_user_bal(interaction.guild.id, interaction.user.id, -26000, 0, reason="bought onex booster for 24 hours")
                            break
                    await interaction.response.send_message(f"You have bought a booster for 24 hours", ephemeral=True)

            case "48h":
                if self.bal['cash'] < 50000:
                    await interaction.response.send_message(f"You don't have enough cash to buy this booster", ephemeral=True)
                    return
                elif self.bal['cash'] >= 50000:
                    data = await self.bot.inv.find(interaction.user.id)
                    if not data:
                        data = make_inv(interaction.user.id)
                        await self.bot.inv.insert(data)

                    for i in data["onex"]:
                        if i['name'] == '48 Hour':
                            if i['quantity'] == 10:
                                await interaction.response.send_message(f"You can't buy more than 10 boosters", ephemeral=True)
                                return
                            i['quantity'] += 1
                            await self.bot.inv.update(data)
                            await self.bot.eco_api.patch_user_bal(interaction.guild.id, interaction.user.id, -50000, 0, reason="bought onex booster for 48 hours")
                            break
                    await interaction.response.send_message(f"You have bought a booster for 48 hours", ephemeral=True)


            case "72h":
                if self.bal['cash'] < 74000:
                    await interaction.response.send_message(f"You don't have enough cash to buy this booster", ephemeral=True)
                    return
                elif self.bal['cash'] >= 74000:
                    data = await self.bot.inv.find(interaction.user.id)
                    if not data:
                        data = make_inv(interaction.user.id)
                        await self.bot.inv.insert(data)

                    for i in data["onex"]:
                        if i['name'] == '72 Hour':
                            if i['quantity'] == 10:
                                await interaction.response.send_message(f"You can't buy more than 10 boosters", ephemeral=True)
                                return
                            i['quantity'] += 1
                            await self.bot.inv.update(data)
                            print(self.bal['cash'] - 74000)
                            await self.bot.eco_api.patch_user_bal(interaction.guild.id, interaction.user.id, -74000, 0, reason="bought a booster onex 72h")
                    await interaction.response.send_message(f"You have bought a booster for 72 hours", ephemeral=True)
