from typing import Dict, Optional

import aiohttp
import discord
from redbot.core import Config, bank, commands
from redbot.core.utils.chat_formatting import box, humanize_number
from tabulate import tabulate



async def tokencheck(ctx):
    token = await ctx.bot.get_shared_api_tokens("coinmarketcap")
    return bool(token.get("api_key", False))


class BoofCoin(commands.Cog):
    """BOOFCOIN: Stick your money into cryptocurrency."""

<<<<<<< Updated upstream
    __version__ = "0.0.1"
    __author__ = "ropeadope62"
=======
>>>>>>> Stashed changes

    def format_help_for_context(self, ctx):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 170708324234480, force_registration=True)

        default_guild = {
            "price_factor": 0, #minimum length to qualify as feedback
            "trading": True
        }
        
        default_user = {
            "boofcoin": {}
        }
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)

    async def get_header(
        self,
    ) -> Optional[
        Dict[str, str]
    ]:  # Original function taken from TrustyJAID with permission, https://github.com/TrustyJAID/Trusty-cogs/blob/ffdb8f77ed888d5bbbfcc3805d860e8dab80741b/conversions/conversions.py#L177
        api_key = (await self.bot.get_shared_api_tokens("coinmarketcap")).get("api_key")
        if api_key:
            return {"X-CMC_PRO_API_KEY": api_key}
        else:
            return None

    async def checkcoins(self, base: str ) -> dict:  # Attribution to TrustyJAID, https://github.com/TrustyJAID/Trusty-cogs/blob/ffdb8f77ed888d5bbbfcc3805d860e8dab80741b/conversions/conversions.py#L211
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.get_header()) as resp:
                data = await resp.json()
                if resp.status in [400, 401, 403, 429, 500]:
                    return data
        for coin in data["data"]:
            if base.upper() == coin["symbol"].upper() or base.lower() == coin["name"].lower():
                return "Boofcoin"
        return {}

    async def all_coins(self):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.get_header()) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}

 
    @commands.check(tokencheck)
    @commands.group()
    async def boofcoin(self, ctx):
        """BOOFCOIN: Stick your money into cryptocurrency.

        BoofCoin is a highly volatile cryptocurrency based on Broadstreet Block Chain Technology (BBCT).
        BoofCoin Market Data is Simulated based on aggregated crypto market conditions. Exchange rate 1$ = 1 credit"""

    @boofcoin.command()
    async def buy(self, ctx, coin, *, amount: float):
        """Buy Boofcoins

        BoofCoin Market Data is Simulated based on aggregated crypto market conditions."""
        if amount <= 0:
            await ctx.send("You cannot buy less than 0 BFC.")
            return
        coin_data = await self.checkcoins(coin) 
        if "status" in coin_data:
            status = coin_data["status"]
            if status["error_code"] in [1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011]:
                await ctx.send(
                    "Something went wrong, the error code is "
                    "{code}\n`{error_message}`".format(
                        code=coin["error_code"], error_message=coin["error_message"]
                    )
                )
                return None
            if status["error_code"] in [1001, 1002]:
                await ctx.send(
                    "The bot owner has not set an API key. "
                    "Please use `{prefix}boofcoinapi` to see "
                    "how to create and setup an API key.".format(prefix=ctx.clean_prefix)
                )
                return None
        if coin_data == {}:
            await ctx.send("{} is not in my list of currencies!".format(coin))
            return None
        price = (
            int(float(coin_data["quote"]["USD"]["price"]) * amount)
            if float(coin_data["quote"]["USD"]["price"]) < 1
            else float(coin_data["quote"]["USD"]["price"]) * amount
        )
        inflate_price = price * 10
        inflate_price = max(inflate_price, 1)
        currency = await bank.get_currency_name(ctx.guild)
        try:
            bal = await bank.withdraw_credits(ctx.author, int(inflate_price))
        except ValueError:
            bal = await bank.get_balance(ctx.author)
            await ctx.send(
                f'You cannot afford {humanize_number(amount)} of {coin_data["name"]}.\nIt would have cost {humanize_number(inflate_price)} {currency} ({price} {currency}) however you only have {bal} {currency}!.'
            )
            return
        async with self.config.user(ctx.author).boofcoin() as coins:
            if coin_data["name"] in coins:
                coins[coin_data["name"] as "Boofcoin"]["amount"] += amount
                coins[coin_data["name"] as "Boofcoin"]["totalcost"] += inflate_price
            else:
                coins[coin_data["name"]] = {"amount": amount, "totalcost": inflate_price}
        await ctx.send(f'You\'ve purchased {humanize_number(amount)} of {coin_data["name"] as "Boofcoin"} for {humanize_number(inflate_price)} {currency}. ({humanize_number((float(coin_data["quote"]["USD"]["price"])) * 10)} {currency} each)!')



    @boofcoin.command()
    async def sell(self, ctx, coin, *, amount: float):
        """Sell Boofcoins

        Exchange rate 1$ = 1 credit, BoofCoin Market Data is Simulated..
        """
        if amount <= 0:
            await ctx.send("You cannot buy less than 0 BFC.")
            return
        coin_data = await self.checkcoins(coin)
        if "status" in coin_data:
            status = coin_data["status"]
            if status["error_code"] in [1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011]:
                await ctx.send(
                    "Something went wrong, the error code is "
                    "{code}\n`{error_message}`".format(
                        code=coin["error_code"], error_message=coin["error_message"]
                    )
                )
                return None
            if status["error_code"] in [1001, 1002]:
                await ctx.send(
                    "The bot owner has not set an API key. "
                    "Please use `{prefix}boofcoinapi` to see "
                    "how to create and setup an API key.".format(prefix=ctx.clean_prefix)
                )
                return None
        if coin_data == {}:
            await ctx.send("{} is not in my list of currencies!".format(coin))
            return None
        async with self.config.user(ctx.author).boofcoin() as coins:
            if coin_data["name"] not in coins:
                return await ctx.send(f'You do not have any of {coin_data["Boofcoin"]}.')
            if amount > coins[coin_data["name"]]["amount"]:
                return await ctx.send(
                    f'You do not have enough of {coin_data["Boofcoin"]}. '
                    f'You only have {coins[coin_data["Boofcoin"]]["amount"]}.'
                )
            coins[coin_data["name"]]["amount"] -= amount
            if coins[coin_data["name"]]["amount"] == 0:
                del coins[coin_data["name"]]
        bal = await bank.deposit_credits(
            ctx.author, int(amount * (float(coin_data["quote"]["USD"]["price"]) * 10))
        )
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(
            f'You sold {humanize_number(amount)} of {coin_data["name"]} for {humanize_number(int(amount * (float(coin_data["quote"]["USD"]["price"]) * 10)))} {currency} '
            f'({humanize_number((float(coin_data["quote"]["USD"]["price"]) * 10))} {currency} each).\nYou now have {humanize_number(bal)} {currency}.'
        )

    @boofcoin.command(name="list")
    async def _list(self, ctx, user: discord.Member = None):
        """Lists the boofcoins of a user, defaults to self

        Example:
             - `[p]boofcoin list`
            - `[p]boofcoin balance @Slurms`

        **Arguments**

        - `<user>` The user to check the Boofcoin balance of. If omitted, default to your own balance.
        """
        selfrequest = False

        if user is None:
            user = ctx.author
            selfrequest = True

        coin_data = await self.all_coins()
        if coin_data == {}:
            return await ctx.send("Failed to fetch all coin data.")
        coin_list = {coin["name"]: coin for coin in coin_data["data"]}
        data = await self.config.user(user).boofcoin()
        if not data:
            if selfrequest:
                return await ctx.send("You do not have any BoofCoins.")
            else:
                return await ctx.send("They do not have any BoofCoins.")
        enddata = []
        for coin in data:
            totalprice = (
                int(data[coin]["amount"] * (coin_list[coin]["quote"]["USD"]["price"] * 10))
                - data[coin]["totalcost"]
            )
            pricestr = (
                f"+{humanize_number(totalprice)}"
                if totalprice > 0
                else f"{humanize_number(totalprice)}"
            )
            enddata.append([coin, data[coin]["amount"], pricestr])
        await ctx.send(
            box(tabulate(enddata, headers=["Coin", "Amount", "Profit/Loss"]), lang="prolog")
        )

    @boofcoin.command()
    async def price(self, ctx, coin, *, amount: float = None):
        """BoofCoin Price"""
        coin_data = await self.checkcoins(coin)
        if "status" in coin_data:
            status = coin_data["status"]
            if status["error_code"] in [1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011]:
                await ctx.send(
                    "Something went wrong, the error code is "
                    "{code}\n`{error_message}`".format(
                        code=coin["error_code"], error_message=coin["error_message"]
                    )
                )
                return None
            if status["error_code"] in [1001, 1002]:
                await ctx.send(
                    "The bot owner has not set an API key. "
                    "Please use `{prefix}boofcoinapi` to see "
                    "how to create and setup an API key.".format(prefix=ctx.clean_prefix)
                )
                return None
        currency = await bank.get_currency_name(ctx.guild)
        if coin_data == {}:
            await ctx.send("{} is not in my list of currencies!".format(coin))
            return None
        if amount is None:
            await ctx.send(
                f'1 {coin_data["name"]} is {humanize_number((float(coin_data["quote"]["USD"]["price"]) * 10))} {currency} each. (${humanize_number((float(coin_data["quote"]["USD"]["price"])))})'
            )
            return
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")
        await ctx.send(
            f'{humanize_number(amount)} of {coin_data["name"]} is {humanize_number(amount * (float(coin_data["quote"]["USD"]["price"]) * 10))} {currency} each. ({humanize_number(float(coin_data["quote"]["USD"]["price"]) * 10)} {currency} each)'
        )
    @boofcoin.command()
    async def trade(self, ctx, coin, *, amount: float):
            """Trade Boofcoins"""

    @boofcoin.command()
    async def BoofNFT(self, ctx, coin, *, amount: float):
            """Buy one of a kind digital assets that will make you rich"""

    @commands.command()
    @commands.is_owner()
    async def boofcoinapi(self, ctx):
        """
        Instructions for how to setup the # 
        crypto API
        """
        msg = (
            "1. Go to https://coinmarketcap.com/api/ sign up for an account.\n"
            "2. In Dashboard / Overview grab your API Key and enter it with:\n"
            f"`{ctx.prefix}set api coinmarketcap api_key YOUR_KEY_HERE`"
        )
        await ctx.maybe_send_embed(msg)
