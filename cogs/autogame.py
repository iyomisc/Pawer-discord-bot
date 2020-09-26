"""
Autogame related cog
"""

import discord
from discord.ext import commands
from modules.helpers import User, async_get


class Autogame(commands.Cog):
    """Autogame Cogs"""

    def __init__(self):
        pass

    @commands.group()
    async def autogame(self, ctx):
        """Autogame commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Commands for Autogame')

    @autogame.command()
    async def list(self, ctx):
        """List your games"""
        user = User(ctx.author.id)
        user_info = user.info()
        address = user_info['address']
        hashes = await async_get("http://autogame.bismuth.live:6060/api/seed/{}".format(address), is_json=True)
        msg = ""
        if hashes is None or len(hashes) == 0:
            msg = 'You are not registered to any game yet :('

        for hash in hashes:
            info = await async_get("http://autogame.bismuth.live:6060/api/db/{}".format(hash), is_json=True)
            try:
                if info['finished']:
                    url = "http://autogame.bismuth.live:6060/replay/{}".format(hash)
                    about = f"Finished - {info['league']}, start block {info['block_start']}, Experience {info['experience']} - {url}"
                else:
                    url = "http://autogame.bismuth.live:6060/unfinished/{}".format(hash)
                    about = f"*Ongoing* {info['league']}, start block {info['block_start']}, Experience {info['experience']}  - {url}"
            except:
                about = 'N/A'
            msg += "- {} - {}\n".format(hash, about)
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Games of {}".format(address))
        await ctx.send(embed=em)

    @autogame.command()
    async def register(self, ctx, league: str, amount: str='0'):
        """Register to a league, with an optional amount - Amount has to match the league entry ticket."""
        user = User(ctx.author.id)
        amount = float(amount)

        msg = ''
        if float(user.balance()) >= float(amount) + 0.01:
            result = user.send_bis_to(amount, "fefb575972cd8fdb086e2300b51f727bb0cbfc33282f1542e19a8f1d", data=league, operation='autogame')
            msg += "txid: {}".format(result['txid'])
        else:
            msg += "Not enough Bis to afford the fees ;("
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Autogame registration")
        await ctx.send(embed=em)

    @autogame.command()
    async def payreg(self, ctx, who_to_reg: discord.Member, league: str='tournament2', amount: str='0'):
        """Pay yourself to register another user to a league, with an optional amount - Amount has to match the league entry ticket."""
        user = User(ctx.author.id)
        amount = float(amount)

        msg = ''
        if float(user.balance()) <= amount + 0.01:
            msg += "Not enough Bis to afford the fees ;("
            em = discord.Embed(description=msg, colour=discord.Colour.green())
            em.set_author(name="Autogame registration")
            await ctx.send(embed=em)
            return

        user_to_reg_info = User(who_to_reg.id).info()
        print("to_reg", user_to_reg_info)
        if not user_to_reg_info or not user_to_reg_info['address']:
            print("user has no wallet")
            await ctx.message.add_reaction(ctx.message, '🤔')  # Thinking face purse
            return
        send = user.send_bis_to(amount, "fefb575972cd8fdb086e2300b51f727bb0cbfc33282f1542e19a8f1d",
                                data="{}:{}".format(league, user_to_reg_info['address']), operation='autogame')
        txid = send['txid']

        if txid:
            # answer by reaction not to pollute
            await ctx.message.add_reaction(ctx.message, '👍')  # Thumb up
        else:
            await ctx.message.add_reaction(ctx.message, '👎')


