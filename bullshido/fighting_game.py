# fighting_game.py
import random
import asyncio
import discord
import math
from .fighting_constants import STRIKES, BODY_PARTS, STRIKE_ACTIONS, GRAPPLE_ACTIONS, GRAPPLE_KEYWORDS, CRITICAL_MESSAGES, CRITICAL_CONCLUDES, KO_MESSAGES, TKO_MESSAGES, FIGHT_RESULT_LONG, REFEREE_STOPS, TKO_VICTOR_MESSAGE, KO_VICTOR_MESSAGE
from PIL import Image, ImageDraw, ImageFont

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
        self.max_health = 100

        if player1_data['training_level'] >= player2_data['training_level']:
            self.current_turn = player1
        else:
            self.current_turn = player2
            
    def create_health_bar(self, current_health, max_health):
        progress = current_health / max_health
        progress_bar_length = 30  # Length of the progress bar
        progress_bar_filled = int(progress * progress_bar_length)
        progress_bar = "[" + ("=" * progress_bar_filled)
        progress_bar += "=" * (progress_bar_length - progress_bar_filled) + "]"
        if progress_bar_filled < progress_bar_length:  # Only add marker if there is room
            marker = "🔴"
            progress_bar = progress_bar[:progress_bar_filled] + marker + progress_bar[progress_bar_filled + 1:]
        return progress_bar
    
    async def update_health_bars(self):
        player1_health_bar = self.create_health_bar(self.player1_health, self.max_health)
        player2_health_bar = self.create_health_bar(self.player2_health, self.max_health)

        embed = discord.Embed(title="Player Health", color=0x00ff00)
        embed.add_field(name=f"{self.player1.display_name}'s Health", value=player1_health_bar, inline=False)
        embed.add_field(name=f"{self.player2.display_name}'s Health", value=player2_health_bar, inline=False)

        await self.channel.send(embed=embed)

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

    def is_grapple_move(self, strike):
        # Check if the strike contains any grapple keywords
        return any(keyword.lower() in strike.lower() for keyword in GRAPPLE_KEYWORDS)

    async def play_turn(self, round_message, round_number):
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

            if self.is_grapple_move(strike):
                action = random.choice(GRAPPLE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} causing {damage} damage! {conclude_message}"
            else:
                action = random.choice(STRIKE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {bodypart} causing {damage} damage! {conclude_message}"

            if self.current_turn == self.player1:
                self.player2_health -= damage
                self.current_turn = self.player2
            else:
                self.player1_health -= damage
                self.current_turn = self.player1

            health_status = f"{defender.display_name} now has {self.player2_health if defender == self.player2 else self.player1_health} health left."
            sleep_duration = random.uniform(2, 3) + (2 if critical_message else 0)  # Add 2 extra seconds for critical hits
            await asyncio.sleep(sleep_duration)

            # Edit the round message with updated content
            await round_message.edit(content=f"Round {round_number} in progress: {message}\n{health_status}")

            # Check for KO
            if self.player1_health <= 0 or self.player2_health <= 0:
                await self.declare_winner_by_ko(round_message)
                return True

            # Check for TKO
            if (self.player1_health < 20 or self.player2_health < 20) and random.random() < 0.5:
                await self.declare_winner_by_tko(round_message, defender)
                return True

            return False
        except Exception as e:
            # Log detailed error information for debugging
            print(f"Error during play_turn: {e}")
            print(f"Attacker: {attacker.display_name}, Defender: {defender.display_name}")
            print(f"Strike: {strike}, Damage: {damage}, Bodypart: {bodypart}")
            print(f"Attacker data: {self.player1_data if attacker == self.player1 else self.player2_data}")
            await round_message.edit(content=f"An error occurred during the turn: {e}")
            return True

    async def declare_winner_by_ko(self, round_message):
        if self.player1_health <= 0:
            winner = self.player2
            loser = self.player1
        else:
            winner = self.player1
            loser = self.player2
        ko_message = random.choice(KO_MESSAGES).format(loser=loser.display_name)
        ko_victor_flavor = random.choice(KO_VICTOR_MESSAGE)
        final_message = (
            f"{ko_message} {winner.display_name} {ko_victor_flavor} "
        )
        await round_message.edit(content=final_message)
        await self.channel.send(final_message)

        await self.record_result(winner, loser, "KO")

    async def declare_winner_by_tko(self, round_message, loser):
        winner = self.player1 if loser == self.player2 else self.player2
        tko_message_flavor = random.choice(TKO_MESSAGES).format(loser=loser.display_name)
        referee_stop_flavor = random.choice(REFEREE_STOPS)

        final_message = (
            f"{tko_message_flavor} {referee_stop_flavor}, {winner.display_name} wins the fight by TKO!\n"
            f"{winner.display_name} {TKO_VICTOR_MESSAGE}, Wow!"
        )
        await round_message.edit(content=final_message)
        await self.channel.send(final_message)

        await self.record_result(winner, loser, "TKO")

    async def record_result(self, winner, loser, result_type):
        try:
            await self.bullshido_cog.update_player_stats(winner, win=True, result_type=result_type, opponent_name=loser.display_name)
            await self.bullshido_cog.update_player_stats(loser, win=False, result_type=result_type, opponent_name=winner.display_name)
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

    async def play_round(self, round_number):
        strike_count = 0
        player1_health_start = self.player1_health
        player2_health_start = self.player2_health


        round_message = await self.channel.send(f"Round {round_number}... *FIGHT!*")

        while strike_count < self.max_strikes_per_round and self.player1_health > 0 and self.player2_health > 0:
            ko_or_tko_occurred = await self.play_turn(round_message, round_number)
            if ko_or_tko_occurred:
                return

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

        for round_number in range(1, self.rounds + 1):
            await self.play_round(round_number)
            await self.update_health_bars()
            if self.player1_health <= 0 or self.player2_health <= 0:
                return

        if self.player1_health > self.player2_health:
            winner = self.player1
            loser = self.player2
            result_type = "UD" if abs(self.player1_score - self.player2_score) > 2 else "SD"
            result_description = FIGHT_RESULT_LONG[result_type]
        elif self.player2_health > self.player1_health:
            winner = self.player2
            loser = self.player1
            result_type = "UD" if abs(self.player2_score - self.player1_score) > 2 else "SD"
            result_description = FIGHT_RESULT_LONG[result_type]
        else:
            if self.player1_score > self.player2_score:
                winner = self.player1
                loser = self.player2
                result_type = "UD" if abs(self.player1_score - self.player2_score) > 2 else "SD"
                result_description = FIGHT_RESULT_LONG[result_type]
            else:
                winner = self.player2
                loser = self.player1
                result_type = "UD" if abs(self.player2_score - self.player1_score) > 2 else "SD"
                result_description = FIGHT_RESULT_LONG[result_type]

        final_message = (
            f"The fight is over!\n"
            f"After 3 rounds, we go to the judges' scorecard for a decision.\n"
            f"The judges scored the fight {self.player1_score if winner == self.player1 else self.player2_score} - {self.player1_score if winner == self.player2 else self.player2_score} for the winner, by {result_description}, {winner.display_name}!"
        )
        await self.channel.send(final_message)

        await self.record_result(winner, loser, result_type)
