
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
from cachetools import TTLCache
from datetime import timedelta
from .reportembeds import ReportEmbeds


_ = Translator("PostMortem", __file__)


class PostMortem(commands.Cog):
    """Post Mortem"""
    
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
    _('Stabbed themselves accidentaly while preparing a Salad Nicoise'),
    _('Jumped into subway track to recover their baggie'),
    _('Accidental gunshot wound to the neck during a gun fight'),
    _('During a game of hide and seek, victim was locked in the cupboard and died from acute dehydration after several days'),
    _('Asphyxiated accidentaly while being Queened'),
    _('Victim drove their car into a wall while attempting to drive over school children'),
    _('Extreme face sitting'),
    _('Declared themselves the reincarnation of David Koresh - Shot 193 times in an ATF shootout.'),
    _('Drowned in the toddler splash pool'),
    _('Hit a deer which bounced up into the windshield. Subject was kicked the shit out of until deceased.'),
    _('While pulled over by the cops and in possession of pepper spray which is a violation of their parole, shoved the can into their anus which was accidentally discharged.\n Subject experienced disorientation, panic, and loss of control of motor activity before multiple organ failure.'),
    _('Heart failure: Connected car jumper cables from a wall socket to their genitalia while attempting "e-stimulation".'),
    _('Victim intended to fill their anus using a can of whipped cream. Nitrous Oxide resulted in flash freezing and immediate necrosis of the intestinal tissue'), 
    _('In an armed robbery gone wrong, subject hid in a drainage pipe and became stuck. Later that night, rats swarmed and start eating him alive, eventually eating into their brain'),
    _('After group Water Sports, urine penetration into an open scratch caused leptospirosis, patient died a week later.'),
    _('In an armed robbery gone wrong, subject hid in a drainage pipe and became stuck. Later that night, rats swarmed and start eating him alive, eventually eating into their brain'),
    _('Asked their spouse to punch them in the stomach after stating that their spouse was "a pussy ass bitch" Subject later died of internal bleeding.'),
    _('Allergic reaction to Latex after being placed into a latex gimp suit by their dominatrix.'),
    _('Crushed to death at a Taylor Swift concert.'),
    _('Drowned in a chemsex fueled Bukkake')
    ]


    use_cache = True

    def __init__(self, bot):
        self.bot = bot
        self.cache = TTLCache(maxsize=10000, ttl=timedelta(hours=24).total_seconds())

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
    async def postmortem(self, ctx: commands.Context, user: discord.Member = None, action_str: str = None):
        """
        Post Mortem reads multiple user data points and returns an accurate assessment predicting their manner and time of death.

        `user` the user you would like to assess.
        """
        try: 
            if user is None:
                    help_menu = (
                    "**Post Mortem Help Menu**\n"
                    "To use the command, mention a user.\n"
                    "Example: `>postmortem @username`\n\n"
                    "Available actions:\n"
                    "- `recalculate`: Recalculates the user's death assessment\n"
                )
                    await ctx.send(help_menu)
                    return

            use_cache = True

            # Calculate approx age
            timestamp = self.discord_id_to_timestamp(user.id)
            current_year = date.today().year
            account_age = datetime.now() - timestamp
            account_age_years = account_age.days // 365
            approximate_age = account_age_years + random.randint(29, 37)
            print(f'Time: {timestamp}, Age: {account_age}, Years: {account_age_years}, Approximate Age: {approximate_age}')

            if action_str == 'recalculate':
                use_cache = False
                if user.id in self.cache:
                    del self.cache[user.id]

            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg = [
                    _("No Vital Signs detected. This test is not intended for robots.."),
                    _("I cannot die I am immortal."),
                ]
                await ctx.send(f"{ctx.author.mention}{choice(bot_msg)}")
                return

            if user and use_cache and (action_str is None and user.id in self.cache):
                user_data = self.cache[user.id]
                await ctx.send(f'Existing report found for {user.name}, retrieving report from Post Mortem:registered: database...')
                await asyncio.sleep(2)
                final_report = ReportEmbeds(user, user_data)
                embed = final_report.report_embed()
                await ctx.send(embed=embed)
            else: 
                # Death calculations:
                life_expectancy = random.randint(25, 90)
                approximate_death_age = life_expectancy if approximate_age < life_expectancy else approximate_age + random.randint(1, 30)
                years_left = approximate_death_age - approximate_age
                days_left = years_left * 365
                weeks_left = years_left * 52
                months_left = years_left * 12
                death_year = current_year + years_left
                cause_of_death = random.choice(self.deaths)

                # Create the progress bar for the embed

                progress = approximate_age / (approximate_age + years_left)
                progress_bar_length = 30  # length of the progress bar
                progress_bar_filled = int(progress * progress_bar_length)
                progress_bar = "[" + ("=" * progress_bar_filled)
                progress_bar += "=" * (progress_bar_length - progress_bar_filled) + "]"
                if progress_bar_filled < progress_bar_length:  # only add marker if there is room
                    marker = "🔴"
                    progress_bar = progress_bar[:progress_bar_filled] + marker + progress_bar[progress_bar_filled + 1:]

                # The below  code is assigning a risk factor based on the number of years left until death

                risk_factor = ""
                if years_left <= 10:
                    risk_factor = 'Death Wish'
                elif years_left in range(10, 15):
                    risk_factor = 'Extreme'
                elif years_left in range(15, 20):
                    risk_factor = 'High'
                elif years_left in range(20, 35):
                    risk_factor = 'Medium'
                elif years_left in range(35, 45):
                    risk_factor = 'Low'
                elif years_left in range(45, 60):
                    risk_factor = 'Minimal'
                elif years_left > 60:
                    risk_factor = 'Negligible'

                user_data = {
                    "progress_bar": progress_bar,
                    "risk_factor": risk_factor,
                    "approximate_age": approximate_age,
                    "death_year": death_year,
                    "approximate_death_age": approximate_death_age,
                    "years_left": years_left,
                    "months_left": months_left,
                    "weeks_left": weeks_left,
                    "days_left": days_left,
                    "cause_of_death": cause_of_death,
                    "progress": progress
                }

                self.cache[user.id] = user_data
                use_cache = True
                await ctx.send('**Welcome to Post Mortem:tm:**\n')
                await asyncio.sleep(1)
                msg = await ctx.send('*Post Mortem reads multiple user data points and returns an accurate assessment of time and cause of death.*\n')
                await asyncio.sleep(2)
                await msg.edit(content=f'Thank you, {ctx.author.mention}. Beginning Post Mortem for *{user}*...\n')
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content='Calculating Vitals...')
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content='Processing age covariates...')
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content=f"{user}'s approximate age is *{approximate_age}* years old.")
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content=f"Analyzing *{user}'s* Life Choices...")
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content=f"Evaluating *{user}* sleep patterns...")
                await asyncio.sleep(random.uniform(1, 1))
                await msg.edit(content=f"Evaluating *{user}* sexual habits...")
                await asyncio.sleep(random.uniform(1, 1))
                await msg.edit(content=f"Evaluating *{user}* dietary intake...")
                await asyncio.sleep(random.uniform(1, 1))
                await msg.edit(content=f"Processing *{user}* overall mortality risk factors...")
                await asyncio.sleep(random.uniform(1, 2))
                await msg.edit(content="**Analysis Completed Successfully.**")
                await asyncio.sleep(random.uniform(1, 2))


                # Send the final report as an embed
                final_report = ReportEmbeds(user, user_data)
                embed = final_report.report_embed()
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")





        


