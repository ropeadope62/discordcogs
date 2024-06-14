import random
import asyncio
import discord
import math
from .fighting_constants import STRIKES, BODY_PARTS, ACTIONS, CRITICAL_MESSAGES, CRITICAL_CONCLUDES

class FightingGame:
    def __init__(self, bot, channel: discord.TextChannel, player1: discord.Member, player2: discord.Member, player1_data: dict, player2_data: dict, bullshido_cog):
        self.bot = bot
        self.channel = channel
        self.player1 = player1
        self.player2 = player2
        self.player1_data = player1_data
        self.player2_data = player2_data
        self.player1_health = 100
        self.player2_health = 100
        self.rounds = 3
        self.max_strikes_per_round = 5
        self.player1_score = 0
        self.player2_score = 0
        self.bullshido_cog = bullshido_cog
        self.training_weight = 0.15  # 15% contribution
        self.diet_weight = 0.15  # 15% contribution

        if player1_data['training_level'] >= player2_data['training_level']:
            self.current_turn = player1
        else:
            self.current_turn = player2

    def calculate_adjusted_damage(self, base_damage, training_level, diet_level):
        training_bonus = math.log10(training_level + 1) * self.training_weight
        diet_bonus = math.log10(diet_level + 1) * self.diet_weight
        adjusted_damage = base_damage * (1 + training_bonus + diet_bonus)
        return round(adjusted_damage)

    def get_strike_damage(self, style, attacker, defender):
        strike, damage_range = random.choice(list(STRIKES[style].items()))
        base_damage = random.randint(*damage_range)
        modified_damage = self.calculate_adjusted_damage(base_damage, attacker['training_level'], attacker['nutrition_level'])
        modifier = random.uniform(0.8, 1.2)
        
        is_critical_hit = random.random() < 0.1
        if is_critical_hit:
            modified_damage = base_damage * 2
            message = random.choice(CRITICAL_MESSAGES)
            conclude_message = random.choice(CRITICAL_CONCLUDES).format(defender=defender.display_name)
        else:
            modified_damage = round(modified_damage * modifier)
            message = ""
            conclude_message = ""
        
        return strike, modified_damage, message, conclude_message

    async def target_bodypart(self):
        bodypart = random.choice(BODY_PARTS)
        return bodypart

    async def play_turn(self, round_message):
        action = random.choice(ACTIONS)
        if self.current_turn == self.player1:
            attacker = self.player1
            defender = self.player2
            style = self.player1_data["fighting_style"]
        else:
            attacker = self.player2
            defender = self.player1
            style = self.player2_data["fighting_style"]

        try:
            strike, damage, critical_message, conclude_message = self.get_strike_damage(style, self.player1_data if attacker == self.player1 else self.player2_data, defender)
            bodypart = await self.target_bodypart()  
            if self.current_turn == self.player1:
                self.player2_health -= damage
                self.current_turn = self.player2
            else:
                self.player1_health -= damage
                self.current_turn = self.player1

            message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {bodypart} causing {damage} damage! {conclude_message}"
            health_status = f"{defender.display_name} now has {self.player2_health if defender == self.player2 else self.player1_health} health left."
            sleep_duration = random.uniform(2, 3) + (2 if critical_message else 0)  # Add 2 extra seconds for critical hits
            await asyncio.sleep(sleep_duration)

            # Edit the round message with updated content
            await round_message.edit(content=f"Round in progress: {message}\n{health_status}")
            return
        except Exception as e:
            print(f"Error during play_turn: {e}")
            await round_message.edit(content="An error occurred during the turn.")
            return
        
    async def play_round(self, round_number):
        strike_count = 0
        player1_health_start = self.player1_health
        player2_health_start = self.player2_health

        print(f"Starting Round {round_number}")

        round_message = await self.channel.send(f"Round {round_number} is starting...")

        while strike_count < self.max_strikes_per_round and self.player1_health > 0 and self.player2_health > 0:
            await self.play_turn(round_message)
            strike_count += 1
            await asyncio.sleep(random.uniform(2, 3))

        player1_health_end = self.player1_health
        player2_health_end = self.player2_health

        health_diff_player1 = player1_health_start - player1_health_end
        health_diff_player2 = player2_health_start - player2_health_end

        print(f"Ending Round {round_number} - Player1 Health: {player1_health_end}, Player2 Health: {player2_health_end}")

        if abs(health_diff_player1 - health_diff_player2) > 20:
            if health_diff_player1 < health_diff_player2:
                self.player1_score += 10
                self.player2_score += 8
                round_result = f"{self.player1.display_name} won the round handily!"
            else:
                self.player1_score += 8
                self.player2_score += 10
                round_result = f"{self.player2.display_name} won the round handily!"
        else:
            if health_diff_player1 < health_diff_player2:
                self.player1_score += 10
                self.player2_score += 9
                round_result = f"{self.player1.display_name} had the edge this round!"
            else:
                self.player1_score += 9
                self.player2_score += 10
                round_result = f"{self.player2.display_name} had the edge this round!"

        await self.channel.send(round_result)
        return round_result

    async def start_game(self):
        intro_message = (
            f"Introducing the fighters!\n"
            f"{self.player1.display_name} with the fighting style {self.player1_data['fighting_style']}!\n"
            f"Versus\n"
            f"{self.player2.display_name} with the fighting style {self.player2_data['fighting_style']}!\n"
            "The match will begin in 10 seconds..."
        )
        await self.channel.send(intro_message)
        await asyncio.sleep(10)

        await self.channel.send("Ready? FIGHT!")

        for round_number in range(1, self.rounds + 1):
            print(f"Round {round_number} is starting...")
            round_result = await self.play_round(round_number)
            if self.player1_health <= 0 or self.player2_health <= 0:
                break

        if self.player1_health > self.player2_health:
            winner = self.player1
            loser = self.player2
        elif self.player2_health > self.player1_health:
            winner = self.player2
            loser = self.player1
        else:
            if self.player1_score > self.player2_score:
                winner = self.player1
                loser = self.player2
            else:
                winner = self.player2
                loser = self.player1

        final_message = (
            f"The fight is over!\n"
            f"After 3 rounds, we go to the judges' scorecard for a decision.\n"
            f"The judges scored the fight {self.player1_score if winner == self.player1 else self.player2_score} - {self.player1_score if winner == self.player2 else self.player2_score} for the winner, by unanimous decision, {winner.display_name}!\n"
            f"{loser.display_name} fought valiantly but was defeated."
        )
        await self.channel.send(final_message)

        try:
            await self.bullshido_cog.update_player_stats(winner, win=True)
            await self.bullshido_cog.update_player_stats(loser, win=False)
            current_loser_morale = await self.bullshido_cog.config.user(loser).morale()
            current_winner_morale = await self.bullshido_cog.config.user(winner).morale()
            new_loser_morale = max(0, current_loser_morale - 20)
            new_winner_morale = min(100, current_winner_morale + 20)
            await self.bullshido_cog.config.user(loser).morale.set(new_loser_morale)
            await self.bullshido_cog.config.user(winner).morale.set(new_winner_morale)
            await self.channel.send(f"{loser.display_name}'s morale has been reduced!")
            await self.channel.send(f"{winner.display_name}'s morale has increased!")
        except Exception as e:
            print(f"An error occurred: {e}")
