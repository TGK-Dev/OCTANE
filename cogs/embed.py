from discord.ext import commands
import discord
import asyncio
from utils.checks import checks
from utils.util import Pag


class Save_embed(discord.ui.View):
    def __init__(self, ctx, data, button_data, embed_name,bot):
        super().__init__()
        self.ctx = ctx
        self.data = data
        self.bot = bot
        self.embed_name = embed_name
        self.button_data = button_data
    
    #make an button name Save Embed by using discord.ui.button decorator
    @discord.ui.button(label="Save Embed", style=discord.ButtonStyle.blurple)
    async def save_embed(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed_filter = {'guild_id': self.ctx.guild.id,'created_by': self.ctx.author.id, 'Key_name': self.embed_name}
        embed_data = {'embed': self.data, 'button_data': self.button_data}
        await self.bot.embeds.upsert_custom(embed_filter, embed_data)
        await interaction.followup.send("Embed saved!",ephemeral=True)
        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:            
            return True
        else:
            interaction.response.send_message("you didn't invoke this command", ephemeral=True)

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.group(name="Embed",description="Send Embed by it's Key Name",invoke_without_command=True)
    @commands.check_any(checks.can_use())
    async def embed(self, ctx, *,key_name:str):
        await ctx.message.delete()
        embed_filter = {'guild_id': ctx.guild.id,'Key_name': key_name}
        embed_data = await self.bot.embeds.find_by_custom(embed_filter)
        if not embed_data:
            await ctx.send("Embed not found")
            return
        embed = embed_data['embed']
        button = embed_data['button_data']    
        if button:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label=button['button_label'], url=button['button_url']))
            await ctx.send(embed=discord.Embed().from_dict(embed), view=view)
        else:
            await ctx.send(embed=discord.Embed().from_dict(embed))
        
    @embed.command(name="create", description="create an nice good looking Embed")
    @commands.check_any(checks.can_use())
    async def create(self, ctx):
        data = {'type': 'rich'}
        button_data = {}
        preview_embed = discord.Embed(title="This is a Preview Embed", description="This is a Preview Embed", color=0xE74C3C)
        preview_message = await ctx.send(embed=preview_embed)
        try:

            qestion_messge = await ctx.send("Send name of Embed which will be use to send embed later")
            embed_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)            
            embed_name = embed_name.content
            check_name = await self.bot.embeds.find_by_custom({"Key_name": embed_name})

            if check_name is None:
                pass
            else:
                return await ctx.send("Embed with this name already exist")
            await qestion_messge.edit(content="Send title of Embed")
            title = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
            data['title'] = title.content
            await preview_message.edit(embed=discord.Embed().from_dict(data))
            await title.delete()

            await qestion_messge.edit("Send color Hex for Embed")
            color = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
            data['color'] = int(color.content, base=16)
            await preview_message.edit(embed=discord.Embed().from_dict(data))
            await color.delete()

            await qestion_messge.edit("Send description for Embed")
            description = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
            data['description'] = description.content
            await preview_message.edit(embed=discord.Embed().from_dict(data))
            await description.delete()

            await qestion_messge.edit("Send url for Embed, Send None if you don't want to add a url")
            url = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
            if url.content.lower() == "none":
                pass
            else:
                data['thumbnail'] = {'url': url.content}
            await preview_message.edit(embed=discord.Embed().from_dict(data))
            await url.delete()

            await qestion_messge.edit("if You want to add Link button to message send 'Yes' else send 'No'")
            confrim = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)

            if confrim.content.lower() == "yes" or 'y':
                await confrim.delete()
                await qestion_messge.edit("Send Button lable")
                button_name = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
                button_data['button_label'] =  button_name.content
                await button_name.delete()
                await qestion_messge.edit("Send Button url")
                button_url = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
                button_data['button_url'] = button_url.content
                await button_url.delete()
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label=button_data['button_label'], url=button_data['button_url']))
                await preview_message.edit(view=view)

            await qestion_messge.delete()

            await preview_message.reply("Do you want to Save This Emebed", view=Save_embed(ctx, data, button_data, embed_name,self.bot))

        except asyncio.TimeoutError:
            return await ctx.send("TimeoutError")
    
def setup(bot):
    bot.add_cog(Embeds(bot))
