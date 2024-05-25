import random
import asyncio
import discord

class FightingGame:
    def __init__(self, channel: discord.TextChannel, player1: discord.Member, player2: discord.Member, player1_data: dict, player2_data: dict):
        self.channel = channel
        self.player1 = player1
        self.player2 = player2
        self.player1_data = player1_data
        self.player2_data = player2_data
        self.player1_health = 100
        self.player2_health = 100
        self.rounds = 3
        self.max_strikes_per_round = 5 

        if player1_data['training_level'] >= player2_data['training_level']:
            self.current_turn = player1
        else:
            self.current_turn = player2

        self.strikes = {
        "Karate": {
            "straight right": (5, 7),
            "straight left": (6, 8),
            "left cross": (4, 6),
            "right cross": (4, 6),
            "hook": (5, 7),
            "uppercut": (6, 8),
            "backfist": (4, 6),
            "ridgehand": (5, 7),
            "knifehand": (5, 7),
            "palm strike": (4, 6),
            "hammerfist": (5, 7),
            "spearhand": (6, 8),
            "reverse punch": (7, 9),
            "reverse knifehand": (7, 9),
            "reverse hammerfist": (7, 9),
            "reverse spearhand": (8, 10),
            "reverse backfist": (7, 9),
            "reverse ridgehand": (7, 9),
            "chop": (4, 6),
            "knee strike": (5, 7)
        },
        "Muay-Thai": {
            "elbow": (6, 8),
            "knee": (5, 7),
            "clinch": (4, 6),
            "teep": (4, 6),
            "low kick": (5, 7),
            "high kick": (6, 8),
            "body kick": (5, 7),
            "uppercut": (5, 7),
            "spinning elbow": (7, 9),
            "spinning back elbow": (7, 9),
            "spinning back kick": (7, 9),
            "flying knee": (7, 9),
            "flying elbow": (7, 9),
            "flying kick": (7, 9),
            "superman punch": (7, 9),
            "jumping knee": (7, 9),
            "jumping elbow": (7, 9)
        },
        "Aikido": {
            "throw": (5, 7),
            "lock": (4, 6),
            "redirect": (3, 5),
            "sweep": (4, 6),
            "joint lock": (5, 7),
            "wrist lock": (4, 6),
            "arm lock": (5, 7),
            "shoulder throw": (5, 7),
            "hip throw": (5, 7)
        },
        "Boxing": {
            "jab": (4, 6),
            "cross": (5, 7),
            "hook": (5, 7),
            "uppercut": (6, 8),
            "weave": (3, 5),
            "body shot": (4, 6),
            "left hook": (5, 7),
            "right hook": (5, 7),
            "left straight": (5, 7),
            "right straight": (6, 8),
            "overhand": (6, 8),
            "counter": (5, 7)
        },
        "Kung-Fu": {
            "palm strike": (5, 7),
            "sweep": (4, 6),
            "dragon strike": (5, 7),
            "tiger palm": (5, 7),
            "crane kick": (6, 8),
            "mantis strike": (5, 7),
            "iron fist": (6, 8),
            "phoenix eye fist": (5, 7)
        },
        "judo": {
            "throw": (5, 7),
            "sweep": (4, 6),
            "chokehold": (5, 7),
            "armbar": (6, 8),
            "hip throw": (5, 7),
            "ankle pick": (4, 6),
            "leg sweep": (5, 7),
            "shoulder throw": (6, 8),
            "counter throw": (5, 7)
        },
        "Taekwondo": {
            "spin kick": (6, 8),
            "front kick": (5, 7),
            "roundhouse kick": (6, 8),
            "axe kick": (5, 7),
            "back kick": (6, 8),
            "side kick": (5, 7),
            "crescent kick": (6, 8),
            "hook kick": (5, 7),
            "reverse roundhouse": (6, 8),
            "reverse side kick": (6, 8),
            "reverse hook kick": (6, 8),
            "reverse crescent kick": (6, 8),
            "push kick": (4, 6)
        },
        "Wrestling": {
            "slam": (6, 8),
            "grapple": (5, 7),
            "takedown": (5, 7),
            "suplex": (6, 8),
            "arm drag": (4, 6),
            "double leg": (6, 8),
            "single leg": (5, 7),
            "neck crank": (5, 7),
            "leg lock": (6, 8)
        },
        "Kravmaga": {
            "palm strike": (6, 8),
            "low kick": (5, 7),
            "knee strike": (5, 7),
            "eye gouge": (4, 6),
            "groin strike": (5, 7),
            "headbutt": (5, 7),
            "short elbow": (4, 6),
            "hammerfist": (5, 7),
            "knee to the groin": (6, 8),
            "elbow to the face": (6, 8),
            "knee to the face": (6, 8)
        },
        "Capoeira": {
            "sweep": (5, 7),
            "cartwheel": (4, 6),
            "headbutt": (5, 7),
            "spinning kick": (6, 8),
            "elbow strike": (6, 8),
            "spinning elbow": (6, 8),
            "knee strike": (5, 7),
            "handstand": (4, 6),
            "backflip": (6, 8),
            "front kick": (5, 7),
            "roundhouse kick": (6, 8),
            "axe kick": (6, 8)
        },
        "Sambo": {
            "throw": (5, 7),
            "lock": (4, 6),
            "sweep": (4, 6),
            "chokehold": (5, 7),
            "ankle lock": (6, 8),
            "knee bar": (6, 8),
            "armbar": (6, 8),
            "leg lock": (6, 8),
            "wrist lock": (5, 7),
            "shoulder lock": (5, 7),
            "neck crank": (6, 8),
            "reverse armbar": (6, 8),
            "reverse leg lock": (6, 8)
        },
        "Kickboxing": {
            "kick": (6, 8),
            "straight punch": (5, 7),
            "hook": (5, 7),
            "knee strike": (5, 7),
            "spinning backfist": (6, 8),
            "low kick": (5, 7),
            "high kick": (6, 8),
            "body kick": (5, 7),
            "hook kick": (6, 8),
            "roundhouse kick": (6, 8),
            "axe kick": (6, 8),
            "side kick": (5, 7),
            "crescent kick": (6, 8),
            "reverse roundhouse": (6, 8),
            "reverse side kick": (6, 8)
        },
        "MMA": {
            "left straight": (6, 8),
            "right straight": (6, 8),
            "hook": (5, 7),
            "left uppercut": (6, 8),
            "right uppercut": (6, 8),
            "superman punch": (7, 9),
            "flying knee": (7, 9),
            "kick": (6, 8),
            "submission": (4, 6),
            "ground and pound": (7, 9),
            "rear naked choke": (5, 7)
        },
        "Brazilian Jiu-Jitsu": {
            "armbar": (6, 8),
            "triangle choke": (5, 7),
            "kimura": (6, 8),
            "omoplata": (6, 8),
            "rear naked choke": (6, 8),
            "sweep": (4, 6),
            "guard pass": (5, 7),
            "mount": (6, 8),
            "back take": (6, 8),
            "darce choke": (7, 9),
            "guillotine": (7, 9),
            "arm triangle": (6, 8),
            "heel hook": (7, 9),
            "toe hold": (7, 9),
            "knee bar": (7, 9),
            "straight ankle lock": (6, 8),
            "wrist lock": (5, 7),
            "crucifix": (6, 8),
            "loop choke": (7, 9),
            "bow and arrow choke": (7, 9),
            "clock choke": (6, 8),
            "paper cutter choke": (7, 9),
            "bread cutter choke": (8, 10)
        }
    }

    
        self.actions = ["throws", "slams", "nails", "whacks", "connects", "rips", "thuds", "crushes", "snaps", "smashes", "pounds", "cracks", "hits", "drives", "lands"]
        self.critical_messages = [
            "Channeling the power of the Dim Mak strike,",
            "Harnessing the technique bestowed upon them by the Black Dragon Fighting Society,",
            "Channeling the Grand Master Ashida Kim,",
            "Summoning the power of Count Dante,"
        ]
        self.critical_concludes = [
            "{defender} is left in a crumpled heap on the floor.",
            "{defender} is left gasping for air.",
            "{defender} is left with a broken nose.",
            "{defender} is left with a shattered rib."
            "{defender} is left with a dislocated shoulder.",
            "{defender} is left with a broken jaw.",
            "{defender} is left with a concussion.",
            "{defender} is left with a broken leg.",
            "{defender} is left with a broken arm.",
            "{defender} is left with a broken collarbone.",
            "{defender} is left with a broken wrist.",
            "{defender} is left with a broken ankle.",
            "{defender} is left with a broken finger.",
            "{defender} is left with a broken toe.",
            "{defender} is left with a broken nose.",
            "{defender} is left with a broken rib.",
            "{defender} is left with a broken shin.",
            "{defender} is left with a broken thigh.",
            "{defender} is left with a broken kneecap.",
            "{defender} is left with a broken foot.",
            "{defender} is left with a broken hand.",
            "{defender} is cut over the eye.",
            "{defender} is left with a black eye.",
            "{defender} is left with a bloody nose.",
            "{defender} is left with a bloody lip.",
            "{defender} is left with a bloody ear.",
            "{defender} is left with a bloody mouth.",
            "{defender} is left with a bloody forehead.",
            "{defender} is left with a bloody cheek."
            
        ]

    def get_strike_damage(self, style, defender):
        strike, damage_range = random.choice(list(self.strikes[style].items()))
        base_damage = random.randint(*damage_range)
        modifier = random.uniform(0.8, 1.2)
        
        is_critical_hit = random.random() < 0.1
        if is_critical_hit:
            modified_damage = base_damage * 2
            message = random.choice(self.critical_messages)
            conclude_message = random.choice(self.critical_concludes).format(defender=defender.display_name)
        else:
            modified_damage = int(base_damage * modifier)
            message = ""
            conclude_message = ""
        
        return strike, modified_damage, message, conclude_message

    async def play_turn(self):
        action = random.choice(self.actions)
        if self.current_turn == self.player1:
            attacker = self.player1
            defender = self.player2
            style = self.player1_data["fighting_style"]
            strike, damage, critical_message, conclude_message = self.get_strike_damage(style, defender)
            self.player2_health -= damage
            message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s body causing {damage} damage! {conclude_message}"
            self.current_turn = self.player2
        else:
            attacker = self.player2
            defender = self.player1
            style = self.player2_data["fighting_style"]
            strike, damage, critical_message, conclude_message = self.get_strike_damage(style, defender)
            self.player1_health -= damage
            message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s body causing {damage} damage! {conclude_message}"
            self.current_turn = self.player1

        return message, f"{defender.display_name} has {self.player2_health if defender == self.player2 else self.player1_health} health left."

    async def play_round(self, round_number):
        strike_count = 0
        player1_health_start = self.player1_health
        player2_health_start = self.player2_health
        
        # Send initial message for the round
        msg = await self.channel.send(f"Round {round_number} begins!")

        while strike_count < self.max_strikes_per_round and self.player1_health > 0 and self.player2_health > 0:
            strike_message, health_status = await self.play_turn()
            await msg.edit(content=f"{strike_message} {health_status}")
            strike_count += 1
            await asyncio.sleep(random.uniform(2, 3))

        player1_health_end = self.player1_health
        player2_health_end = self.player2_health

        health_diff_player1 = player1_health_start - player1_health_end
        health_diff_player2 = player2_health_start - player2_health_end

        if abs(health_diff_player1 - health_diff_player2) > 20:
            round_result = f"{self.player1.display_name} won the round handily!" if health_diff_player1 < health_diff_player2 else f"{self.player2.display_name} won the round handily!"
        else:
            round_result = f"{self.player1.display_name} had the edge this round!" if health_diff_player1 < health_diff_player2 else f"{self.player2.display_name} had the edge this round!"

        return round_result

    async def start_game(self):
        # Introduce the fighters
        intro_message = (
            f"Introducing the fighters!\n"
            f"{self.player1.display_name} with the fighting style {self.player1_data['fighting_style']}!\n"
            f"Versus\n"
            f"{self.player2.display_name} with the fighting style {self.player2_data['fighting_style']}!\n"
            "The match will begin in 10 seconds..."
        )
        await self.channel.send(intro_message)
        await asyncio.sleep(10)

        # Start the match
        await self.channel.send("Ready? FIGHT!")

        for round_number in range(1, self.rounds + 1):
            round_message = f"Round {round_number} begins!"
            await self.channel.send(round_message)
            round_result = await self.play_round(round_number)
            await self.channel.send(round_result)
            if self.player1_health <= 0 or self.player2_health <= 0:
                break

        # Announce the winner
        if self.player1_health > self.player2_health:
            winner = self.player1
        else:
            winner = self.player2
        
        await self.channel.send(f"Game over! The winner is {winner.display_name}.")