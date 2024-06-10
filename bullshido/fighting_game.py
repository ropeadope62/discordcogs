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
                "Straight Right": (5, 7),
                "Straight Left": (6, 8),
                "Left Cross": (4, 6),
                "Right Cross": (4, 6),
                "Hook": (5, 7),
                "Uppercut": (6, 8),
                "Backfist": (4, 6),
                "Ridgehand": (5, 7),
                "Knifehand": (5, 7),
                "Palm Strike": (4, 6),
                "Hammerfist": (5, 7),
                "Spearhand": (6, 8),
                "Reverse Punch": (7, 9),
                "Reverse Knifehand": (7, 9),
                "Reverse Hammerfist": (7, 9),
                "Reverse Spearhand": (8, 10),
                "Reverse Backfist": (7, 9),
                "Reverse Ridgehand": (7, 9),
                "Chop": (4, 6),
                "Knee Strike": (5, 7)
            },
            "Muay-Thai": {
                "Elbow": (6, 8),
                "Knee": (5, 7),
                "Clinch": (4, 6),
                "Teep": (4, 6),
                "Low Kick": (5, 7),
                "High Kick": (6, 8),
                "Body Kick": (5, 7),
                "Uppercut": (5, 7),
                "Spinning Elbow": (7, 9),
                "Spinning Back Elbow": (7, 9),
                "Spinning Back Kick": (7, 9),
                "Flying Knee": (7, 9),
                "Flying Elbow": (7, 9),
                "Flying Kick": (7, 9),
                "Superman Punch": (7, 9),
                "Jumping Knee": (7, 9),
                "Jumping Elbow": (7, 9)
            },
            "Aikido": {
                "Throw": (5, 7),
                "Lock": (4, 6),
                "Redirect": (3, 5),
                "Sweep": (4, 6),
                "Joint Lock": (5, 7),
                "Wrist Lock": (4, 6),
                "Arm Lock": (5, 7),
                "Shoulder Throw": (5, 7),
                "Hip Throw": (5, 7)
            },
            "Boxing": {
                "Jab": (4, 6),
                "Cross": (5, 7),
                "Hook": (5, 7),
                "Uppercut": (6, 8),
                "Weave": (3, 5),
                "Body Shot": (4, 6),
                "Left Hook": (5, 7),
                "Right Hook": (5, 7),
                "Left Straight": (5, 7),
                "Right Straight": (6, 8),
                "Overhand": (6, 8),
                "Counter": (5, 7)
            },
            "Kung-Fu": {
                "Palm Strike": (5, 7),
                "Sweep": (4, 6),
                "Dragon Strike": (5, 7),
                "Tiger Palm": (5, 7),
                "Crane Kick": (6, 8),
                "Mantis Strike": (5, 7),
                "Iron Fist": (6, 8),
                "Phoenix Eye Fist": (5, 7)
            },
            "Judo": {
                "Throw": (5, 7),
                "Sweep": (4, 6),
                "Chokehold": (5, 7),
                "Armbar": (6, 8),
                "Hip Throw": (5, 7),
                "Ankle Pick": (4, 6),
                "Leg Sweep": (5, 7),
                "Shoulder Throw": (6, 8),
                "Counter Throw": (5, 7)
            },
            "Taekwondo": {
                "Spin Kick": (6, 8),
                "Front Kick": (5, 7),
                "Roundhouse Kick": (6, 8),
                "Axe Kick": (5, 7),
                "Back Kick": (6, 8),
                "Side Kick": (5, 7),
                "Crescent Kick": (6, 8),
                "Hook Kick": (5, 7),
                "Reverse Roundhouse": (6, 8),
                "Reverse Side Kick": (6, 8),
                "Reverse Hook Kick": (6, 8),
                "Reverse Crescent Kick": (6, 8),
                "Push Kick": (4, 6)
            },
            "Wrestling": {
                "Slam": (6, 8),
                "Grapple": (5, 7),
                "Takedown": (5, 7),
                "Suplex": (6, 8),
                "Arm Drag": (4, 6),
                "Double Leg": (6, 8),
                "Single Leg": (5, 7),
                "Neck Crank": (5, 7),
                "Leg Lock": (6, 8)
            },
            "Kravmaga": {
                "Palm Strike": (6, 8),
                "Low Kick": (5, 7),
                "Knee Strike": (5, 7),
                "Eye Gouge": (4, 6),
                "Groin Strike": (5, 7),
                "Headbutt": (5, 7),
                "Short Elbow": (4, 6),
                "Hammerfist": (5, 7),
                "Knee to the Groin": (6, 8),
                "Elbow to the Face": (6, 8),
                "Knee to the Face": (6, 8)
            },
            "Capoeira": {
                "Sweep": (5, 7),
                "Cartwheel": (4, 6),
                "Headbutt": (5, 7),
                "Spinning Kick": (6, 8),
                "Elbow Strike": (6, 8),
                "Spinning Elbow": (6, 8),
                "Knee Strike": (5, 7),
                "Handstand": (4, 6),
                "Backflip": (6, 8),
                "Front Kick": (5, 7),
                "Roundhouse Kick": (6, 8),
                "Axe Kick": (6, 8)
            },
            "Sambo": {
                "Throw": (5, 7),
                "Lock": (4, 6),
                "Sweep": (4, 6),
                "Chokehold": (5, 7),
                "Ankle Lock": (6, 8),
                "Knee Bar": (6, 8),
                "Armbar": (6, 8),
                "Leg Lock": (6, 8),
                "Wrist Lock": (5, 7),
                "Shoulder Lock": (5, 7),
                "Neck Crank": (6, 8),
                "Reverse Armbar": (6, 8),
                "Reverse Leg Lock": (6, 8)
            },
            "Kickboxing": {
                "Kick": (6, 8),
                "Straight Punch": (5, 7),
                "Hook": (5, 7),
                "Knee Strike": (5, 7),
                "Spinning Backfist": (6, 8),
                "Low Kick": (5, 7),
                "High Kick": (6, 8),
                "Body Kick": (5, 7),
                "Hook Kick": (6, 8),
                "Roundhouse Kick": (6, 8),
                "Axe Kick": (6, 8),
                "Side Kick": (5, 7),
                "Crescent Kick": (6, 8),
                "Reverse Roundhouse": (6, 8),
                "Reverse Side Kick": (6, 8)
            },
            "MMA": {
                "Left Straight": (6, 8),
                "Right Straight": (6, 8),
                "Hook": (5, 7),
                "Left Uppercut": (6, 8),
                "Right Uppercut": (6, 8),
                "Superman Punch": (7, 9),
                "Flying Knee": (7, 9),
                "Kick": (6, 8),
                "Submission": (4, 6),
                "Ground and Pound": (7, 9),
                "Rear Naked Choke": (5, 7)
            },
            "Brazilian Jiu-Jitsu": {
                "Armbar": (6, 8),
                "Triangle Choke": (5, 7),
                "Kimura": (6, 8),
                "Omoplata": (6, 8),
                "Rear Naked Choke": (6, 8),
                "Sweep": (4, 6),
                "Guard Pass": (5, 7),
                "Mount": (6, 8),
                "Back Take": (6, 8),
                "Darce Choke": (7, 9),
                "Guillotine": (7, 9),
                "Arm Triangle": (6, 8),
                "Heel Hook": (7, 9),
                "Toe Hold": (7, 9),
                "Knee Bar": (7, 9),
                "Straight Ankle Lock": (6, 8),
                "Wrist Lock": (5, 7),
                "Crucifix": (6, 8),
                "Loop Choke": (7, 9),
                "Bow and Arrow Choke": (7, 9),
                "Clock Choke": (6, 8),
                "Paper Cutter Choke": (7, 9),
                "Bread Cutter Choke": (8, 10)
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
            "{defender} is left with a shattered rib.",
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

        message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s body causing {damage} damage! {conclude_message}"
        sleep_duration = random.uniform(2, 3) + (2 if critical_message else 0)  # Add 2 extra seconds for critical hits
        await asyncio.sleep(sleep_duration)
        return message, f"{defender.display_name} now has {self.player2_health if defender == self.player2 else self.player1_health} health left."

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
            loser = self.player2
        else:
            winner = self.player2
            loser = self.player1
            
        await self.channel.send(f"Game over! The winner is {winner.display_name}.")
            
        bullshido_cog = self.channel.guild.get_cog('Bullshido')
        if bullshido_cog:
            await bullshido_cog.update_player_stats(winner, win=True)
            await bullshido_cog.update_player_stats(loser, win=False)
        
       
