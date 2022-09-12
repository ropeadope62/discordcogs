
# Fun cog idea to give user their time left to live based on their current age and cause of death from a random list

# Required modules before bot
import discord
from redbot.core import commands
import random
from datetime import date
from time import sleep

from redbot.core import Config, checks, commands, bank
from redbot.core.errors import BalanceTooHigh
from redbot.core.utils.chat_formatting import (bold, box, humanize_list,humanize_number, pagify)
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.predicates import MessagePredicate

class Death(commands.Cog):
        def __init__(self, bot):     
            self.bot = bot
            self.causes_of_death = ['Freak gasoline fight accident',
                                    'Falling out of bed',
                                    'Impaled on the bill of a swordfish',
                                    'Falling off a ladder and landing head first in a water butt',
                                    'Killed by his own explosive while trying to steal from a condom dispenser',
                                    'Hit by a coconut falling off a tree',
                                    'Died after being stabbed in the eye with an umbrella',
                                    'Taking a selfie with a loaded handgun and shot themselves in the throat',
                                    'Shot themselves to death with gun carried in breast pocket',
                                    'Crushed to deathwhile moving a fridge freezer',
                                    'Crushed to death by their partner',
                                    'Laughed so hard which lead to cardiac arrest',
                                    'Run over by their own vehicle',
                                    'Died of a lethal Sherry enema',
                                    'Ate themselves to death',
                                    'Champagne Cork into the eye',
                                    'Strangled by necktie or scarf',
                                    'Trampled by cattle on a field in Derbyshire',
                                    'Trampled to death by Camel/Camels',
                                    'Eaten by a trove of Pigs',
                                    'Threatened to kill themselves and shot 43 times by Police',
                                    'Killed by their own remote-controlled airplane',
                                    'Stepping backwards off a cliff while the photographer tried to get them in frame',
                                    'Fell to their death from the top of a lighthouse',
                                    'Falling off an inflatable artwork',
                                    'Swung by the ankles by a Clown and hit their head',
                                    'Hit by their own bullets fired in celebration',
                                    'Asphyxia: Victim K-Holed face down on the couch',
                                    'Heading a Medicine Ball',
                                    'Drowned in the tub',
                                    'Stabbed during an argument over a game of UNO',
                                    'Penetration by Horse',
                                    'Kicked by a Horse',
                                    'Burned to death while hosting a family BBQ',
                                    'Dropped weights on themself in the gym',
                                    'Shot in the courtroom while showing the jury how his clients alleged murder victim had actually shot himself',
                                    'Fell onto a wine glass',
                                    'Auto-erotic Asphyxiation',
                                    'Drug Overdose - undetermined: Victim tested positive for Cocaine, Methamphetamine, MDMA, MDA, Fentanyl, GHB, Clonezepam, Lorezepam, Diazepam and Ketamine metabolytes',
                                    'Anal Fentanyl Overdose: Acute shock and ultimate cardiac arrest',
                                    'Acute tear of the colon via insertion of a foreign object', 
                                    'Shot by police after making a gun hand and drawing it during a traffic stop',
                                    'Run over by traffic while attempting to recover a baggie from the highway',
                                    'Massive heart attack after 72 hour Cocaine and Viagra bender',
                                    'Crashed their car into a bridge while masturbating on the highway',
                                    'Ingested Arsenic in a Cult mass-suicide',
                                    'Died in a fire which occured at a MarineLand dolphin exhibit',
                                    'Shot in the neck by their friend on a hunting trip',
                                    'Stabbed themselves accidentaly while preparing a Nicoise Salad',
                                    'Jumped into subway track to recover their baggie',
                                    'Accidental gunshot wound to the neck during a gun fight',
                                    'During a game of hide and seek, victim was locked in the cupboard and died from acute dehydration after several days',
                                    'Asphyxiated accidentaly while being Queened',
                                    'Victim drove their car into a wall while attempting to drive over school children',
                                    'Extreme face sitting']
        @commands.command()
        async def postmortem(self, ctx, age: int):
            """Welcome to Broad Street Labs 
            Post Mortem reads multiple user data points and returns an accurate assessment of how it ends. 
            Enter your current age to begin 
            """
            author = ctx.message.author
            age_as_int = (int(age))
            try:
                current_year = date.today().year
                years_remaining = random.randint(0, (100 - age_as_int))
                death_year = (current_year + years_remaining)
                death_cause = random.choice(self.causes_of_death)
                days_remaining = years_remaining * 365
                weeks_remaining = years_remaining * 52
                months_remaining = years_remaining * 12
                
            
            except ValueError:
                await ctx.send('You need to enter numbers...\n')

            await ctx.send('Analyzing User Data...\n') ; sleep(0.2)
            await ctx.send('Calculating Vitals...\n') ; sleep(0.2)
            await ctx.send('Analyzing Dietary Choices...\n') ; sleep(0.2)
            await ctx.send('Analyzing Life Choices...\n') ; sleep(0.2)
            await ctx.send('Analysis Completed Successfully\n') ; sleep(0.5)
            await ctx.send(f'You will die in the year {death_year}. The coroners report concluded: {death_cause}') ; sleep(0.2)
            await ctx.send(f"{author} has {days_remaining} days, {weeks_remaining} weeks, and {months_remaining} months left.\n")