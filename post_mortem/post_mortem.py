
# Fun cog idea to give user their time left to live based on their current age and cause of death from a random list

# Required modules before bot
import discord
import asyncio
from redbot.core import commands
import random
from random import choice
from datetime import datetime, date
from time import sleep
from typing import List
from redbot.core.i18n import Translator
from redbot.core import commands



_ = Translator("PostMortem", __file__)


class PostMortem(commands.Cog):
    """Broad Street Labs - Post Mortem"""
    
    __author__ = ["Slurms Mackenzie"]
    __version__ = "0.1.0"
    
    deaths: List[str] = [
    _('Freak gasoline fight accident'),
    _('Falling out of bed'),
    _('Impaled on the bill of a swordfish'),
    _('Falling off a ladder and landing head first in a water butt'),
    _('Killed by his own explosive while trying to steal from a condom dispenser'),
    _('Hit by a coconut falling off a tree'),
    _('Died after being stabbed in the eye with an umbrella'),
    _('Taking a selfie with a loaded handgun and shot themselves in the throat'),
    _('Shot themselves to death with gun carried in breast pocket'),
    _('Crushed to deathwhile moving a fridge freezer'),
    _('Crushed to death by their partner'),
    _('Laughed so hard which lead to cardiac arrest'),
    _('Run over by their own vehicle'),
    _('Died of a lethal Sherry enema'),
    _('Ate themselves to death'),
    _('Champagne Cork into the eye'),
    _('Strangled by necktie or scarf'),
    _('Trampled by cattle on a field in Derbyshire'),
    _('Trampled to death by Camel/Camels'),
    _('Eaten by a trove of Pigs'),
    _('Threatened to kill themselves and shot 43 times by Police'),
    _('Killed by their own remote-controlled airplane'),
    _('Stepping backwards off a cliff while the photographer tried to get them in frame'),
    _('Fell to their death from the top of a lighthouse'),
    _('Falling off an inflatable artwork'),
    _('Swung by the ankles by a Clown and hit their head'),
    _('Hit by their own bullets fired in celebration'),
    _('Asphyxia: Victim K-Holed face down on the couch'),
    _('Heading a Medicine Ball'),
    _('Drowned in the tub'),
    _('Stabbed during an argument over a game of UNO'),
    _('Penetration by Horse'),
    _('Kicked by a Horse'),
    _('Burned to death while hosting a family BBQ'),
    _('Dropped weights on themself in the gym'),
    _('Shot in the courtroom while showing the jury how his clients alleged murder victim had actually shot himself'),
    _('Fell onto a wine glass'),
    _('Auto-erotic Asphyxiation'),
    _('Drug Overdose - undetermined: Victim tested positive for Cocaine, Methamphetamine, MDMA, MDA, Fentanyl, GHB, Clonezepam, Lorezepam, Diazepam , Ketamine and Viagra metabolytes'),
    _('Anal Fentanyl Overdose: Acute shock and ultimate cardiac arrest'),
    _('Acute tear of the colon via insertion of a foreign object'), 
    _('Shot by police after making a gun hand and drawing it during a traffic stop'),
    _('Run over by traffic while attempting to recover a baggie from the highway'),
    _('Massive heart attack after 72 hour Cocaine and Viagra bender'),
    _('Crashed their car into a bridge while masturbating on the highway'),
    _('Ingested Arsenic in a Cult mass-suicide'),
    _('Died in a fire which occured at a MarineLand dolphin exhibit'),
    _('Shot in the neck by their friend on a hunting trip'),
    _('Stabbed themselves accidentaly while preparing a Nicoise Salad'),
    _('Jumped into subway track to recover their baggie'),
    _('Accidental gunshot wound to the neck during a gun fight'),
    _('During a game of hide and seek, victim was locked in the cupboard and died from acute dehydration after several days'),
    _('Asphyxiated accidentaly while being Queened'),
    _('Victim drove their car into a wall while attempting to drive over school children'),
    _('Extreme face sitting'),
    _('Declared themselves the reincarnation of David Koresh - Shot 193 times in an ATF shootout.'),
    _('Drowned in the toddler splash pool'),
    _('Hit a deer which bounced up into the windshield. Subject was kicked the shit out of until deceased.')
    ]


    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Slurms!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"


    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def get_str():
        return '100'

    @staticmethod
    def discord_id_to_timestamp(user_id: int) -> datetime:
        discord_epoch = 1420070400000
        timestamp = ((user_id >> 22) + discord_epoch) / 1000.0
        return datetime.fromtimestamp(timestamp)
    

    @commands.command()
    async def postmortem(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
          
        Post Mortem reads multiple user data points and returns an accurate assessment predicting their manner and time of death 

        `user` the user you would like to assess.
        """
        if user:
            timestamp = self.discord_id_to_timestamp(user.id)
            account_age = datetime.now() - timestamp
            account_age_years = account_age.days // 365
            approximate_age = account_age_years + random.randint(25, 32)
            print(f'Time: {timestamp}, Age: {account_age}, Years: {account_age_years}, Approximate Age: {approximate_age}')

        user_hash = hash(user)
        current_year = date.today().year
        random.random()

        await ctx.send('**Welcome to Broad Street Labs:tm: - Post Mortem:registered:**\n')
        await asyncio.sleep(1)
        await ctx.send('*Post Mortem reads multiple user data points and returns an accurate assessment of time and cause of death.*\n')
        await asyncio.sleep(1)
        msg = await ctx.send (f'Thank you, {ctx.author.mention}. Beginning Post Mortem for *{user}*...\n')
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content='Calculating Vitals...')
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content='Calculating Vitals...\nProcessing age covariates...')
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content=f"Calculating Vitals...\nProcessing age covariates...\n{user}'s approximate age is *{approximate_age}* years old.")
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content=f"Calculating Vitals...\nProcessing age covariates...\n{user}'s approximate age is *{approximate_age}* years old.\nAnalyzing *{user}'s* Life Choices...")
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content=f"Calculating Vitals...\nProcessing age covariates...\n{user}'s approximate age is *{approximate_age}* years old.\nAnalyzing *{user}'s* Life Choices...\nProcessing *{user}* mortality risk factors...")
        await asyncio.sleep(random.uniform(1, 2))
        await msg.edit(content=f"Calculating Vitals...\nProcessing age covariates...\n{user}'s approximate age is *{approximate_age}* years old.\nAnalyzing *{user}'s* Life Choices...\nProcessing *{user}* mortality risk factors...\nAnalysis Completed Successfully")
        await asyncio.sleep(random.uniform(1, 2))


        if user:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg = [
                    _(
                        " No Vital Signs detected. This test is not intended for robots.."
                    ),
                    _(
                        " I cannot die I am immortal."
                    ),
                ]
                await ctx.send(f"{ctx.author.mention}{choice(bot_msg)}")
            else:
                life_expectancy = random.randint(25, 90)
                approximate_death_age = life_expectancy if approximate_age < life_expectancy else approximate_age + random.randint(1, 30)
                years_left = approximate_death_age - approximate_age
                hash_result_asint = int(str(user_hash)[:2])
                days = years_left * 365
                weeks = years_left * 52
                months = years_left * 12
                death_year = current_year + years_left
                risk_factor = ""
                if years_left in range(10):
                    risk_factor = 'Extreme'
                elif years_left in range(10,20):
                    risk_factor = 'High'
                elif years_left in range(20,30):
                    risk_factor = 'Medium'
                elif years_left in range(30,40):
                    risk_factor = 'Low'
                elif years_left in range(40,50):
                    risk_factor = 'Minimal'
                elif years_left > 50: 
                    risk_factor = 'Negligible'


            progress = approximate_age / (approximate_age + years_left)
            progress_bar_length = 20  # length of the progress bar
            progress_bar_filled = int(progress * progress_bar_length)
            progress_bar = f"[{'=' * progress_bar_filled}{' ' * (progress_bar_length - progress_bar_filled)}]"

            progress_bar_green = "🟢" * progress_bar_filled
            progress_bar_yellow = "🟡" * (progress_bar_length - progress_bar_filled if progress_bar_length - progress_bar_filled <= progress_bar_length // 2 else progress_bar_length // 2)
            progress_bar_red = "🔴" * (progress_bar_length - len(progress_bar_green) - len(progress_bar_yellow))
            progress_bar = progress_bar_green + progress_bar_yellow + progress_bar_red



            embed = discord.Embed(
                title="**Broad Street Labs™ - Post Mortem®**",
                description="*Final Report Summary*",
                color=discord.Color.dark_red(),
            )
            
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="Subject", value=user.mention, inline=False)
            embed.add_field(name="Death Progress", value=f"{progress_bar} {progress * 100:.1f}%", inline=False)
            embed.add_field(name="Subject Risk Factors", value=f"{risk_factor}", inline=False)
            embed.add_field(name="Approximate Age", value=f"{approximate_age}", inline=False)
            embed.add_field(name="Death Year", value=f"{death_year}", inline=False)
            embed.add_field(name="Approximate Death Age", value=f"{approximate_age + years_left}", inline=False)
            embed.add_field(
                name="Time Left",
                value=f"{years_left} years... *or* {months} months... *or* {weeks} weeks... *or* {days} days",
                inline=False,
            )
            embed.add_field(
                name="*** Post Mortem® Likely result of death:***",
                value=choice(self.deaths),
                inline=False,
            )
            embed.set_footer(text="Sponsored by Empties")

            await ctx.send(embed=embed)
        else:
            await ctx.send("A subject is required for analysis... try postmortem @discorduser")


      

        
    

        