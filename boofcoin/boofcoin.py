from typing import Dict, Optional
import io
import aiohttp
import discord
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from redbot.core import Config, bank, commands
from redbot.core.utils.chat_formatting import box, humanize_number
from tabulate import tabulate


async def tokencheck(ctx):
    token = await ctx.bot.get_shared_api_tokens("coinmarketcap")
    return bool(token.get("api_key", False))


class BoofCoin(commands.Cog):
    """Buy and Sell BoofCoin"""
    __author__ = "ropeadope65/Slurms Mackenzie"
    __version__ = "1.0.0"
    
    custom_name_mapping = {
        "BOOF": "BTC",
        "BNFT": "ETH",
        "BETF": "XMR",
        "BSTAKE": "DOGE",
        }
    
    wallet_name_mapping = {
        "Bitcoin": "Boofcoin",
        "Ethereum": "BoofNFT",
        "Dogecoin": "BoofStake",
        "Monero": "BoofETF"
    }

    def format_help_for_context(self, ctx):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 2938473984564884215564732, force_registration=True)
        self.config.register_user(boofcoin={})
        self.inverse_name_mapping = {v: k for k, v in self.custom_name_mapping.items()}

    async def get_header(
        self,
    ) -> Optional[
        Dict[str, str]
    ]:  # Original function taken from TrustyJAID with permission, https://github.com/TrustyJAID/Trusty-cogs/blob/ffdb8f77ed888d5bbbfcc3805d860e8dab80741b/conversions/conversions.py#L177
        api_key = (await self.bot.get_shared_api_tokens("coinmarketcap")).get("api_key")
        return {"X-CMC_PRO_API_KEY": api_key} if api_key else None

    async def checkcoins(
        self, base: str
    ) -> dict:  # Attribution to TrustyJAID, https://github.com/TrustyJAID/Trusty-cogs/blob/ffdb8f77ed888d5bbbfcc3805d860e8dab80741b/conversions/conversions.py#L211
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        real_symbol = self.custom_name_mapping.get(base.upper(), base)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.get_header()) as resp:
                data = await resp.json()
                if resp.status in [400, 401, 403, 429, 500]:
                    return data
                
            coin_data = next(
            (
                coin
                for coin in data["data"]
                if real_symbol.upper() == coin["symbol"].upper() or real_symbol.lower() == coin["name"].lower()
            ),
            {},
            )
            return coin_data


    async def all_coins(self):
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=await self.get_header()) as resp:
                return await resp.json() if resp.status == 200 else {}

    @commands.hybrid_group()
    @commands.check(tokencheck)
    async def boofcoin(self, ctx):
        """Group command for buying/selling boofcoin

        Prices are based on aggregate market data. """

    @boofcoin.command()
    async def graph(self, ctx, coin: str, days: int = 30):
        """Show historical price graph for a cryptocurrency."""
        

        
        data = await self.fetch_historical_data(coin, days)
        if "error" in data:
            await ctx.send(data["error"])
            return

        fig = self.plot_historical_data(data)
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer, filename=f"{coin}_history.png"))
        plt.close(fig)
        
    async def fetch_historical_data(self, symbol: str, days: int) -> dict:
        """Fetch historical data for a given symbol and number of days."""
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical?symbol={symbol}&time_start={days}daysAgo"
        headers = await self.get_header()
        if not headers:
            return {"error": "API Key not set or invalid."}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": f"API error occurred with status {resp.status}."}
                
    def plot_historical_data(self, data: dict):
        """Generate a seaborn plot for the historical data."""
        df = pd.DataFrame(data['data']['quotes'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df, x='timestamp', y='price')
        plt.title('Historical Price Data')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        return plt

    @boofcoin.command()
    async def buy(self, ctx, coin, *, amount: float):
        """Buy Boofcoin, BoofNFT or BoofStake

        Exchange rate 1$ = 10 credits."""
        
        if coin.upper() not in self.custom_name_mapping:
            await ctx.send("You can only buy BOOF, BNFT, BETF or BSTAKE symbols.")
            return
        if amount <= 0:
            await ctx.send("You cannot buy less than 0 coin.")
            return
        
        real_symbol = self.custom_name_mapping.get(coin.upper(), None)
        if not real_symbol:
            await ctx.send(f"{coin} is not a supported currency.")
            return
        coin_data = await self.checkcoins(real_symbol)
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
                    "Please use `{prefix}boofapi` to see "
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
        inflate_price = price * 5
        inflate_price = max(inflate_price, 1)
        currency = await bank.get_currency_name(ctx.guild)
        try:
            bal = await bank.withdraw_credits(ctx.author, int(inflate_price))
        except ValueError:
            bal = await bank.get_balance(ctx.author)
            await ctx.send(
                f'You cannot afford {humanize_number(amount)} of {coin}.\nIt would have cost {humanize_number(inflate_price)} {currency} ({price} {currency}) however you only have {bal} {currency}!.'
            )
            return
        async with self.config.user(ctx.author).boofcoin() as coins:
            if coin_data["name"] in coins:
                coins[coin_data["name"]]["amount"] += amount
                coins[coin_data["name"]]["totalcost"] += inflate_price
            else:
                coins[coin_data["name"]] = {"amount": amount, "totalcost": inflate_price}
        await ctx.send(
            f'You\'ve purchased {humanize_number(amount)} of {coin} for {humanize_number(inflate_price)} {currency}.'
        )

    @boofcoin.command()
    async def sell(self, ctx, coin, *, amount: float):
        """Sell crypto

        Exchange rate 1$ = 10 credits."""
        
        if coin.upper() not in self.custom_name_mapping:
            await ctx.send("You can only sell BOOF, BNFT, BETF or BSTAKE.")
            return
        if amount <= 0:
            await ctx.send("You cannot sell 0 or less coin.")
            return
    
        real_symbol = self.custom_name_mapping.get(coin, coin)
        coin_data = await self.checkcoins(real_symbol)
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
                    "Please use `{prefix}boofapi` to see "
                    "how to create and setup an API key.".format(prefix=ctx.clean_prefix)
                )
                return None
        if coin_data == {}:
            await ctx.send("{} is not in my list of currencies!".format(coin))
            return None
        async with self.config.user(ctx.author).boofcoin() as coins:
            if coin_data["name"] not in coins:
                return await ctx.send(f'You do not have any of {coin_data["name"]}.')
            if amount > coins[coin_data["name"]]["amount"]:
                return await ctx.send(
                f'You do not have enough crypto to sell {amount}. '
                f'You only have {coins[coin_data["name"]]["amount"]}.'
                )
            coins[coin_data["name"]]["amount"] -= amount
            if coins[coin_data["name"]]["amount"] == 0:
                del coins[coin_data["name"]]
        bal = await bank.deposit_credits(
            ctx.author, int(amount * (float(coin_data["quote"]["USD"]["price"]) * 5))
        )
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(
            f'You sold {humanize_number(amount)} of {coin} for {humanize_number(int(amount * (float(coin_data["quote"]["USD"]["price"]) * 5)))} {currency} '
            f'({humanize_number((float(coin_data["quote"]["USD"]["price"]) * 5))} {currency} each).\nYou now have {humanize_number(bal)} {currency}.'
        )

    @boofcoin.command(name="wallet")
    async def _list(self, ctx, user: discord.Member = None):
        selfrequest = False

        if user is None:
            user = ctx.author
            selfrequest = True

        # No need to fetch all coins data if you're fetching individual prices dynamically
        data = await self.config.user(user).boofcoin()
        if not data:
            if selfrequest:
                return await ctx.send("You do not have any crypto bought.")
            else:
                return await ctx.send(f"{user.display_name} does not have any crypto bought.")

        enddata = []
        for custom_name, details in data.items():
            # Convert custom name back to real symbol for price fetching
            real_symbol = self.custom_name_mapping.get(custom_name, custom_name)
            coin_data = await self.checkcoins(real_symbol)
            current_price = coin_data.get("quote", {}).get("USD", {}).get("price", 0)

            # Calculate the total value of the holding
            totalvalue = details["amount"] * current_price
            profit_loss = totalvalue - details["totalcost"]
            pricestr = f"+{humanize_number(profit_loss)}" if profit_loss > 0 else f"{humanize_number(profit_loss)}"
            enddata.append([self.wallet_name_mapping.get(custom_name, custom_name), details["amount"], pricestr, totalvalue])

        if enddata:
            await ctx.send(
                box(tabulate(enddata, headers=["Crypto Asset", "Amount", "Net Investment Value", "Relative Profit/Loss"]), lang="prolog")
            )
        else:
            await ctx.send("There was an issue fetching your wallet data.")

    @boofcoin.command()
    async def price(self, ctx, coin, *, amount: float = None):
        """Price of a crypto"""
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
                    "Please use `{prefix}cryptoapi` to see "
                    "how to create and setup an API key.".format(prefix=ctx.clean_prefix)
                )
                return None
        currency = await bank.get_currency_name(ctx.guild)
        if coin_data == {}:
            await ctx.send("{} is not in my list of currencies!".format(coin))
            return None
        if amount is None:
            await ctx.send(
                f'1 {coin} is {humanize_number((float(coin_data["quote"]["USD"]["price"]) * 5))} {currency} each. (${humanize_number((float(coin_data["quote"]["USD"]["price"])))})'
            )
            return
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")
        await ctx.send(
            f'{humanize_number(amount)} of {coin} is {humanize_number(amount * (float(coin_data["quote"]["USD"]["price"]) * 10))} {currency} each. ({humanize_number(float(coin_data["quote"]["USD"]["price"]) * 5)} {currency} each)'
        )

    @commands.command()
    @commands.is_owner()
    async def boofcoinapi(self, ctx):
        """
        Instructions for how to setup the crypto API
        """
        msg = (
            "1. Go to https://coinmarketcap.com/api/ sign up for an account.\n"
            "2. In Dashboard / Overview grab your API Key and enter it with:\n"
            f"`{ctx.prefix}set api coinmarketcap api_key YOUR_KEY_HERE`"
        )
        await ctx.maybe_send_embed(msg)
