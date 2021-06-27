import discord
import discord.ext.commands
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
import asyncio


class Buttons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def is_me():
        def predicate(ctx):
            return ctx.message.author.id in [488614633670967307 , 301657045248114690]
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name="tictactoe", description="tictactoe game with buttons", aliases=["ttt"])
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def tictactoe(self, ctx, member: discord.Member):
        if ctx.author == member:
            return await ctx.send("You can't play against yourself!")
        embed = discord.Embed(color=0xF5F5F5, title=f"Hey, {ctx.author.name} wants to play tic-tac-toe with you!")
        acceptdenycomps = [
            [
                Button(style=ButtonStyle.green, label="Accept"),
                Button(style=ButtonStyle.red, label="Decline"),
            ]
        ]
        #
        board = [
            [
                Button(style=ButtonStyle.grey, label="⠀", id="0 0"),
                Button(style=ButtonStyle.grey, label="⠀", id="0 1"),
                Button(style=ButtonStyle.grey, label="⠀", id="0 2")

            ],
            [
                Button(style=ButtonStyle.grey, label="⠀", id="1 0"),
                Button(style=ButtonStyle.grey, label="⠀", id="1 1"),
                Button(style=ButtonStyle.grey, label="⠀", id="1 2")

            ],
            [
                Button(style=ButtonStyle.grey, label="⠀", id="2 0"),
                Button(style=ButtonStyle.grey, label="⠀", id="2 1"),
                Button(style=ButtonStyle.grey, label="⠀", id="2 2")
            ]
        ]
        selections = [
            [
                "unchosen",
                "unchosen",
                "unchosen"
            ],
            [
                "unchosen",
                "unchosen",
                "unchosen"
            ],
            [
                "unchosen",
                "unchosen",
                "unchosen"
            ]
        ]
        
        m = await ctx.send(embed=embed, components=acceptdenycomps, content=member.mention)
        def haswon(team):
            if selections[0][0] == team and selections[0][1] == team and selections[0][2] == team:
                return True
            if selections[1][0] == team and selections[1][1] == team and selections[1][2] == team:
                return True
            if selections[2][0] == team and selections[2][1] == team and selections[2][2] == team:
                return True
            if selections[0][0] == team and selections[1][0] == team and selections[2][0] == team:
                return True
            if selections[0][1] == team and selections[1][1] == team and selections[2][1] == team:
                return True
            if selections[0][2] == team and selections[1][2] == team and selections[2][2] == team:
                return True
            if selections[0][0] == team and selections[1][1] == team and selections[2][2] == team:
                return True
            if selections[0][2] == team and selections[1][1] == team and selections[2][0] == team:
                return True
            else:
                return False
        def istie(team):
            if not "unchosen" in str(selections):
                if not haswon(team):

                    return True
                else:

                    return False
            else:

                return False


        def confirmcheck(res):
            return res.user.id == member.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id)

        try:
            res = await self.bot.wait_for("button_click", check=confirmcheck, timeout=50)
        except asyncio.TimeoutError:
            await msg.edit(
                embed=Embed(color=0xED564E, title="Timeout!", description="No-one reacted. ☹️"),
                components=[
                    Button(style=ButtonStyle.red, label="Oh-no! Timeout reached!", disabled=True),
                ],
            )
            return
        await res.respond(type=6)
        if res.component.label == "Accept":
            accept = True
            embed = discord.Embed(color=discord.Colour.green(), title=f'{member.name} has accepted!', description="The game will now begin...")
            await m.edit(embed=embed)
            await asyncio.sleep(1)

        else:
            accept = False
            embed = discord.Embed(color=discord.Colour.red(), title=f'{member.name} has declined.')
            await m.edit(embed=embed)
            return
        
        async def winner(team):
            if team == "red":
                color = discord.Colour.red()
                user = member
            if team == "green":
                color = discord.Colour.green()
                user = ctx.author
            e = discord.Embed(color=color, title=f"{user.name} has won!")
            await m.edit(embed=e, components=board)
            return

            
        
        greensturnembed = discord.Embed(color=0xF5F5F5, title=f"{ctx.author.name}'s turn")
        redsturnembed = discord.Embed(color=0xF5F5F5, title=f"{member.name}'s turn")
        greenstatus = True
        # True = green False = red
        def greensturncheck(res):
            return res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and res.message.id == m.id
        def redsturncheck(res):
            return res.user.id == member.id and res.channel.id == ctx.channel.id and res.message.id == m.id
        while accept:
            if greenstatus:
                await m.edit(embed=greensturnembed, components=board)
                try:
                    res = await self.bot.wait_for("button_click", check=greensturncheck, timeout=50)
                    await res.respond(type=6)
                    listid = res.component.id
                    firstpart, secondpart = listid.split(' ')
                    board[int(firstpart)][int(secondpart)] = Button(style=ButtonStyle.green, label="⠀", id="1 0", disabled=True)
                    selections[int(firstpart)][int(secondpart)] = "green"
                    if haswon('green'):
                        await winner('green')
                        accept = False
                        return
                    if istie('green'):
                        e = discord.Embed(color=0xF5F5F5, title=f"Call it a tie!")
                        board.append(Button(style=ButtonStyle.URL, label="View creator", url="https://github.com/PythonSerious"))
                        await m.edit(embed=e, components=board)
                        accept = False
                        return
                    greenstatus = False
                    pass
                    

                except asyncio.TimeoutError:
                    await msg.edit(
                        embed=Embed(color=0xED564E, title="Timeout!", description="No-one reacted. ☹️"),
                        components=[
                            Button(style=ButtonStyle.red, label="Oh-no! Timeout reached!", disabled=True),
                        ],
                    )
                    return
            if not greenstatus:
                await m.edit(embed=redsturnembed, components=board)
                try:
                    res = await self.bot.wait_for("button_click", check=redsturncheck, timeout=50)
                    await res.respond(type=6)
                    listid = res.component.id
                    firstpart, secondpart = listid.split(' ')
                    board[int(firstpart)][int(secondpart)] = Button(style=ButtonStyle.red, label="⠀", id="1 0",
                                                                 disabled=True)
                    selections[int(firstpart)][int(secondpart)] = "red"
                    if haswon('red'):
                        await winner('red')
                        accept = False
                        return
                    if istie('red'):
                        e = discord.Embed(color=0xF5F5F5, title=f"Call it a tie!")
                        board.append(Button(style=ButtonStyle.URL, label="View creator", url="https://github.com/PythonSerious"))
                        await m.edit(embed=e, components=board)
                        accept = False
                        return
                        
                    greenstatus = True
                    pass


                except asyncio.TimeoutError:
                    await msg.edit(
                        embed=Embed(color=0xED564E, title="Timeout!", description="No-one reacted. ☹️"),
                        components=[
                            Button(style=ButtonStyle.red, label="Oh-no! Timeout reached!", disabled=True),
                        ],
                    )
                    return

    @commands.command(name="calculator", description="an Calculator made with ueing button", aliases=['cal'])
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def calculator(self, ctx):
        base_embed = discord.Embed(title=f"{ctx.author.display_name}'s calculator",
            color=0x2f3136,
            description=f"")
        button = [
            [
                Button(style=ButtonStyle.grey, label=1),
                Button(style=ButtonStyle.grey, label=2),
                Button(style=ButtonStyle.grey, label=3),
                Button(style=ButtonStyle.blue, label="*"),
                Button(style=ButtonStyle.red, label="Exit"),
            ],
            [
                Button(style=ButtonStyle.grey, label=4),
                Button(style=ButtonStyle.grey, label=5),
                Button(style=ButtonStyle.grey, label=6),
                Button(style=ButtonStyle.blue, label="/"),
                Button(style=ButtonStyle.red, label="⌫"),
            ],
            [
                Button(style=ButtonStyle.grey, label=7),
                Button(style=ButtonStyle.grey, label=8),
                Button(style=ButtonStyle.grey, label=9),
                Button(style=ButtonStyle.blue, label="+"),
                Button(style=ButtonStyle.red, label="Clear"),
            ],
            [
                Button(style=ButtonStyle.grey, label="00"),
                Button(style=ButtonStyle.grey, label="0"),
                Button(style=ButtonStyle.grey, label="."),
                Button(style=ButtonStyle.blue, label="-"),
                Button(style=ButtonStyle.green, label="="),
            ],
            [
                Button(style=ButtonStyle.grey, label="(",),
                Button(style=ButtonStyle.grey, label=")",),
                Button(style=ButtonStyle.grey, label="❌", disabled=True),
                Button(style=ButtonStyle.blue, label="❌", disabled=True),
                Button(style=ButtonStyle.green, label="❌", disabled=True),
            ]
        ]

        m = await ctx.send(embed=base_embed, components=button)
        embeds = m.embeds
        for embed in embeds:
          data = embed.to_dict()
        valid = ["1","2","3","4","5","6","7","8","9","00","0","-","+","*","/", "(", ")"]
        while True:
            try:
                res = await self.bot.wait_for("button_click", check=lambda res:res.user.id == ctx.author.id and res.channel.id == ctx.channel.id and str(res.message.id) == str(m.id), timeout=60)
                await res.respond(type=6)
                if str(res.component.label.lower()) == "exit":
                    await m.edit(content="Calculator Closed",components=[])

                if str(res.component.label.lower()) in valid:
                    try:
                        thing = data['description']
                        thing = thing.replace('`', '')
                        thing = thing.replace('\n', '')
                        thing = thing.replace('py', '')
                        data['description'] = f"```py\n{thing}{res.component.label.lower()}\n```"
                        thing = ""
                        await m.edit(embed=embed.from_dict(data))
                    except KeyError:
                        data['description'] = f"```py\n{res.component.label.lower()}\n```"
                        await m.edit(embed=embed.from_dict(data))

                if str(res.component.label.lower()) == "⌫":
                    string = str(data['description'])
                    index = len(string)-5
                    if len(string) > index:
                        string = string[0 : index : ] + string[index + 1 : :]
                    data['description'] = string
                    await m.edit(embed=embed.from_dict(data))

                if str(res.component.label.lower()) == "=":
                    try:
                        thing = data['description']
                    except KeyError:
                        data['description'] = "```\nYou can't calculator an empty value Calculator is Closed\n```"
                        return await m.edit(components=[], embed=embed.from_dict(data))
                    thing = thing.replace('py', '')
                    thing = thing.replace('`', '')
                    thing = thing.replace('\n', '')
                    try:
                        ans = eval(thing)
                        data["fields"] = []
                        fields = {'name': 'Answer', 'value': f'```\n{ans}\n```', 'inline':False}
                        data['fields'].append(fields)
                        await m.edit(embed=embed.from_dict(data))
                    except :
                        data["fields"] = []
                        fields = {'name': 'Answer', 'value': f'```\nMaybe Fix Your Maths but mybe try 3*(2+5) not 3(2+5)\n```', 'inline':False}
                        data['fields'].append(fields)
                        await m.edit(embed=embed.from_dict(data))

                if str(res.component.label.lower()) == "clear":
                    del data["description"]
                    del data["fields"]
                    data["fields"] = []
                    await m.edit(embed=embed.from_dict(data))

            except asyncio.TimeoutError:
                await m.edit(content="Calculator Closed",components=[])


def setup(bot):
    DiscordComponents(bot)
    bot.add_cog(Buttons(bot))