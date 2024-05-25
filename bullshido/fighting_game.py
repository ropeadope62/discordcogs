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

        if player1_data['training_level'] >= player2_data['training_level']:
            self.current_turn = player1
        else:
            self.current_turn = player2

        self.strikes = {
            "karate": {
                "punch": (5, 10),
                "kick": (7, 12),
                "block": (2, 5),
                "chop": (6, 11),
                "knee_strike": (4, 9)
            },
            "muaythai": {
                "elbow": (8, 14),
                "knee": (6, 11),
                "clinch": (3, 7),
                "teep": (5, 10),
                "headbutt": (7, 12)
            },
            "aikido": {
                "throw": (4, 9),
                "lock": (3, 7),
                "redirect": (2, 5),
                "sweep": (5, 10),
                "joint_lock": (6, 11)
            },
            "boxing": {
                "jab": (4, 8),
                "cross": (6, 10),
                "hook": (5, 9),
                "uppercut": (7, 12),
                "weave": (3, 7)
            },
            "kungfu": {
                "palm_strike": (5, 9),
                "sweep": (4, 8),
                "dragon_strike": (6, 11),
                "tiger_palm": (7, 12)
            },
            "judo": {
                "throw": (7, 12),
                "pin": (5, 9),
                "sweep": (4, 8),
                "chokehold": (6, 11),
                "armbar": (8, 14)
            },
            "taekwondo": {
                "spin_kick": (8, 13),
                "front_kick": (6, 10),
                "roundhouse_kick": (7, 11),
                "axe_kick": (5, 9),
                "back_kick": (7, 12)
            },
            "wrestling": {
                "slam": (7, 12),
                "grapple": (5, 9),
                "takedown": (6, 10),
                "suplex": (8, 14),
                "arm_drag": (4, 8)
            },
            "kravmaga": {
                "strike": (8, 14),
                "kick": (7, 11),
                "knee_strike": (6, 10),
                "eye_gouge": (5, 9),
                "groin_strike": (7, 12)
            },
            "capoeira": {
                "kick": (7, 13),
                "sweep": (6, 10),
                "cartwheel": (4, 8),
                "headbutt": (5, 9),
                "spinning_kick": (8, 14)
            },
            "sambo": {
                "throw": (6, 11),
                "lock": (5, 9),
                "sweep": (4, 8),
                "chokehold": (7, 12),
                "ankle_lock": (8, 14)
            },
            "kickboxing": {
                "kick": (7, 12),
                "punch": (6, 10),
                "knee_strike": (5, 9),
                "spinning_backfist": (8, 13),
                "low_kick": (4, 8)
            },
            "mma": {
                "punch": (6, 11),
                "kick": (7, 12),
                "submission": (4, 8),
                "ground_and_pound": (8, 14),
                "rear_naked_choke": (5, 9)
            }
        }
    
        self.actions = ["throws", "slams", "nails", "brutalizes", "connects", "rips", "thuds", "crushes"]
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
        ]

    def get_strike_damage(self, style):
        strike, damage_range = random.choice(list(self.strikes[style].items()))
        base_damage = random.randint(*damage_range)
        modifier = random.uniform(0.8, 1.2)
        
        is_critical_hit = random.random() < 0.1
        if is_critical_hit:
            modified_damage = base_damage * 2
            message = random.choice(self.critical_messages)
            conclude_message = random.choice(self.critical_concludes)
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
            strike, damage, critical_message, conclude_message = self.get_strike_damage(style)
            self.player2_health -= damage
            message = f"{critical_message} {attacker} {action} a {strike} into {defender}'s body causing {damage} damage! {conclude_message}"
            self.current_turn = self.player2
        else:
            attacker = self.player2
            defender = self.player1
            style = self.player2_data["fighting_style"]
            strike, damage, critical_message, conclude_message = self.get_strike_damage(style)
            self.player1_health -= damage
            message = f"{critical_message} {attacker} {action} a {strike} into {defender}'s body causing {damage} damage! {conclude_message}"
            self.current_turn = self.player1

        health_status = f"{defender} has {self.player2_health if defender == self.player2 else self.player1_health} health left."
        await self.channel.send(f"{message} {health_status}")
        await asyncio.sleep(3)
        return self.player1_health <= 0 or self.player2_health <= 0

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
        while self.player1_health > 0 and self.player2_health > 0:
            game_over = await self.play_turn()
            if game_over:
                winner = self.player2 if self.player1_health <= 0 else self.player1
                await self.channel.send(f"Game over! The winner is {winner}.")
                return
