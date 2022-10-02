
# Fun cog idea to give user their time left to live based on their current age and cause of death from a random list

# Required modules before bot
import discord
from redbot.core import commands
import random
from random import choice
from datetime import date
from time import sleep
from typing import List

from redbot.core.i18n import Translator, cog_i18n
from redbot.core import Config, checks, commands, bank
from redbot.core.errors import BalanceTooHigh
from redbot.core.utils.chat_formatting import (bold, box, humanize_list,humanize_number, pagify)
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.predicates import MessagePredicate

_ = Translator("PostMortem", __file__)

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
    _('Extreme face sitting')
]
    
#@cog_i18n(_)
class PostMortem(commands.Cog):
    """Broad Street Labs - Post Mortem"""
    
    __author__ = ["Slurms Mackenzie"]
    __version__ = "0.1.0"

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
    

             
    @commands.command()
    async def postmortem(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
          
        Post Mortem reads multiple user data points and returns an accurate assessment predicting their manner and time of death 

        `user` the user you would like to assess.
        """
        current_year = date.today().year
        years_generate = 0
        years_generate = int(user.id)
        age = 10
        msg = "***Post Mortem:registered:***  "
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
                
                #userid_as_int = int(user.id)
                #age.append(userid_as_int)
                
                if age in range(1,100):
                    years = str(years_generate)[-2:]
                    years_as_int = int(years)
                    days = years_as_int * 365
                    weeks = years_as_int * 52
                    months = years_as_int * 12 
                    death_year = current_year + years_as_int
                
                    await ctx.send('**Welcome to Broad Street Labs:tm: - Post Mortem:registered:**\n') ; sleep(1)
                    await ctx.send('*Post Mortem reads multiple user data points and returns an accurate assessment of time and cause of death.*\n') ; sleep(1)
                    await ctx.send(f'Thank you, {ctx.author.mention}. Beginning Post Mortem for *{user}*...\n') ; sleep(0.5)
                    await ctx.send('Calculating Vitals...\n') ; sleep(0.2)
                    await ctx.send(f"Analyzing *{user}'s* Dietary Choices...\n") ; sleep(0.2)
                    await ctx.send(f"Analyzing *{user}'s* Life Choices...\n") ; sleep(0.2)
                    await ctx.send('Analysis Completed Successfully\n') ; sleep(1) 
                    await ctx.send(f"*{user}'s* death will occur in {death_year}.\n") ; sleep(0.2)
                    await ctx.send(f"*{user}* has {years} years... *or* {months} months... *or* {weeks} weeks... *or* {days} days left to live.\n") ; sleep(0.2)
                    await ctx.send(f"***Generating Final Report...***") ; sleep(1)
                    await ctx.send(user.mention + msg + choice(deaths))
                    #await ctx.send(days_remaining)
                    #await ctx.send(weeks_remaining)
                    #await ctx.send(months_remaining)    
                else: 
                    raise Exception('Error #2414: User IQ too low.\n')                    
        else:
            await ctx.send(ctx.message.author.mention + msg + choice(deaths))
      

        
        

        