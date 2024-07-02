import random
import asyncio
import discord
import math
import requests
from .fighting_constants import STRIKES, BODY_PARTS, STRIKE_ACTIONS, GRAPPLE_ACTIONS, GRAPPLE_KEYWORDS, CRITICAL_MESSAGES, KO_MESSAGES, TKO_MESSAGES, FIGHT_RESULT_LONG, REFEREE_STOPS, TKO_VICTOR_MESSAGE, KO_VICTOR_MESSAGE, CRITICAL_RESULTS
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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
        self.player1_stamina = player1_data.get('stamina_level', 100)
        self.player2_stamina = player2_data.get('stamina_level', 100)
        self.rounds = 3
        self.max_strikes_per_round = 5
        self.player1_score = 0
        self.player2_score = 0
        self.bullshido_cog = bullshido_cog
        self.training_weight = 0.15  # 15% contribution
        self.diet_weight = 0.15  # 15% contribution
        self.player1_critical_message = ""
        self.player2_critical_message = ""
        self.player1_critical_injuries = []
        self.player2_critical_injuries = []
        self.max_health = 100
        self.ACTION_COST = 10
        self.BASE_MISS_PROBABILITY = 0.1
        self.BASE_STAMINA_COST = 10
        self.FIGHT_TEMPLATE_URL = "https://i.ibb.co/MSprvBG/bullshido-template.png"
        if player1_data['training_level'] >= player2_data['training_level']:
            self.current_turn = player1
        else:
            self.current_turn = player2
    def generate_fight_image(self):
        player1_avatar_url = self.player1.avatar_url
        player2_avatar_url = self.player2.avatar_url

        # Load the template image
        response_template = requests.get(self.template_url)
        template = Image.open(BytesIO(response_template.content))

        # Load the profile images
        response1 = requests.get(player1_avatar_url)
        player1_avatar = Image.open(BytesIO(response1.content)).convert("RGBA")

        response2 = requests.get(player2_avatar_url)
        player2_avatar = Image.open(BytesIO(response2.content)).convert("RGBA")

        # Resize the avatars
        avatar_size = (150, 150)
        player1_avatar = player1_avatar.resize(avatar_size, Image.ANTIALIAS)
        player2_avatar = player2_avatar.resize(avatar_size, Image.ANTIALIAS)

        # Calculate positions
        width, height = template.size
        player1_position = (50, (height - avatar_size[1]) // 2)
        player2_position = (width - avatar_size[0] - 50, (height - avatar_size[1]) // 2)

        # Paste the avatars onto the template
        template.paste(player1_avatar, player1_position, player1_avatar)
        template.paste(player2_avatar, player2_position, player2_avatar)

        # Save or return the final image
        output_path = '~/ScrapGPT/ScrapGPT/logs/fight_image.png'
        template.save(output_path)
        return output_path
            
    def create_health_bar(self, current_health, max_health):
        progress = current_health / max_health
        progress_bar_length = 50  # Length of the progress bar
        progress_bar_filled = int(progress * progress_bar_length)
        progress_bar = "[" + ("=" * progress_bar_filled)
        progress_bar += "=" * (progress_bar_length - progress_bar_filled) + "]"
        if progress_bar_filled < progress_bar_length:  # Only add marker if there is room
            marker = "🔴"
            progress_bar = progress_bar[:progress_bar_filled] + marker + progress_bar[progress_bar_filled + 1:]
        return progress_bar

    
    def get_stamina_status(self, stamina):
        if stamina >= 75:
            return "Fresh"
        elif stamina >= 50:
            return "Winded"
        elif stamina >= 25:
            return "Gassed"
        else:
            return "Exhausted" 
    
    async def update_health_bars(self, round_number):
        player1_health_bar = self.create_health_bar(self.player1_health, self.max_health)
        player2_health_bar = self.create_health_bar(self.player2_health, self.max_health)
        player1_stamina_status = self.get_stamina_status(self.player1_stamina)
        player2_stamina_status = self.get_stamina_status(self.player2_stamina)

        embed = discord.Embed(
            title=f"Round {round_number} - {self.player1.display_name} vs {self.player2.display_name}",
            color=0xFF0000
        )
        embed.add_field(name=f"{self.player1.display_name}'s Health", value=f"{player1_health_bar} {self.player1_health}", inline=False)
        embed.add_field(name=f"{self.player1.display_name}'s Stamina", value=player1_stamina_status, inline=False)
        if self.player1_critical_injuries:
            embed.add_field(name=f"{self.player1.display_name} Injuries", value=", ".join(self.player1_critical_injuries), inline=False)
        embed.add_field(name=f"{self.player2.display_name}'s Health", value=f"{player2_health_bar} {self.player2_health}", inline=False)
        embed.add_field(name=f"{self.player2.display_name}'s Stamina", value=player2_stamina_status, inline=False)
        if self.player2_critical_injuries:
            embed.add_field(name=f"{self.player2.display_name} Injuries", value=", ".join(self.player2_critical_injuries), inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")

        await self.channel.send(embed=embed)



    def calculate_adjusted_damage(self, base_damage, training_level, diet_level):
        training_bonus = math.log10(training_level + 1) * self.training_weight
        diet_bonus = math.log10(diet_level + 1) * self.diet_weight
        adjusted_damage = base_damage * (1 + training_bonus + diet_bonus)
        return round(adjusted_damage)

    def get_strike_damage(self, style, attacker, defender):
    # Initialize all variables to prevent reference errors
        strike = ""
        damage_range = (0, 0)
        base_damage = 0
        modified_damage = 0
        message = ""
        conclude_message = ""
        critical_injury = ""

        try:
            strike, damage_range = random.choice(list(STRIKES[style].items()))
            base_damage = random.randint(*damage_range)
            modified_damage = self.calculate_adjusted_damage(base_damage, attacker['training_level'], attacker['nutrition_level'])
            modifier = random.uniform(0.8, 1.2)

            is_critical_hit = random.random() < 0.1
            if is_critical_hit:
                modified_damage = base_damage * 2
                conclude_message, critical_injury = random.choice(list(CRITICAL_RESULTS.items()))
                conclude_message = conclude_message.format(defender=defender.display_name)
                message = random.choice(CRITICAL_MESSAGES)
            else:
                modified_damage = round(modified_damage * modifier)
            return strike, modified_damage, message, conclude_message, critical_injury
        except Exception as e:
            print(f"Error during get_strike_damage: {e}")
            print(f"Attacker: {attacker}, Defender: {defender}, Style: {style}")
            return strike, modified_damage, message, conclude_message, critical_injury

    async def target_bodypart(self):
        bodypart = random.choice(BODY_PARTS)
        return bodypart

    def is_grapple_move(self, strike):
        # Check if the strike contains any grapple keywords
        return any(keyword.lower() in strike.lower() for keyword in GRAPPLE_KEYWORDS)
    
    def calculate_miss_probability(self, attacker_stamina, attacker_training, defender_training, defender_stamina):
        miss_probability = self.BASE_MISS_PROBABILITY
        
        if attacker_stamina < 50:
            miss_probability += 0.05  # Increase miss chance if attacker's stamina is low
        
        if defender_stamina > 50:
            miss_probability -= 0.05  # Decrease miss chance if defender's stamina is high
        
        miss_probability -= 0.01 * math.log10(attacker_training + 1)  # Decrease miss chance with better training
        miss_probability += 0.01 * math.log10(defender_training + 1)  # Increase miss chance against better trained defender
        
        return min(max(miss_probability, 0.05), 0.5)  # Clamp the probability between 5% and 50%

    def regenerate_stamina(self, current_stamina, training_level, diet_level):
        regeneration_rate = (training_level + diet_level) / 20  # Simple formula for regeneration
        return min(current_stamina + regeneration_rate, self.max_stamina)

    async def play_turn(self, round_message, round_number):
        attacker = self.player1 if self.current_turn == self.player1 else self.player2
        defender = self.player2 if self.current_turn == self.player1 else self.player1
        attacker_stamina = self.player1_stamina if self.current_turn == self.player1 else self.player2_stamina
        defender_stamina = self.player2_stamina if self.current_turn == self.player1 else self.player1_stamina
        attacker_training = self.player1_data["training_level"] if self.current_turn == self.player1 else self.player2_data["training_level"]
        defender_training = self.player2_data["training_level"] if self.current_turn == self.player1 else self.player1_data["training_level"]
        style = self.player1_data["fighting_style"] if self.current_turn == self.player1 else self.player2_data["fighting_style"]

        try:
            miss_probability = self.calculate_miss_probability(attacker_stamina, attacker_training, defender_training, defender_stamina)
            if random.random() < miss_probability:
                # Misses the attack
                miss_message = f"{attacker.display_name} missed their attack on {defender.display_name}!"
                await round_message.edit(content=f"Round {round_number} in progress: {miss_message}")
                self.current_turn = defender  # Switch turn to the other player
                return False

            # Proceed with calculating damage if the attack is not missed
            strike, damage, critical_message, conclude_message, critical_injury = self.get_strike_damage(style, self.player1_data if attacker == self.player1 else self.player2_data, defender)
            if not strike:
                await round_message.edit(content=f"An error occurred during the turn: Failed to determine strike.")
                return True

            bodypart = await self.target_bodypart()

            if self.is_grapple_move(strike):
                action = random.choice(GRAPPLE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} causing {damage} damage! {conclude_message}"
            else:
                action = random.choice(STRIKE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {bodypart} causing {damage} damage! {conclude_message}"

            # Reduce defender's health and attacker's stamina
            if self.current_turn == self.player1:
                self.player2_health -= damage
                self.player1_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player2
                if critical_injury:
                    self.player2_critical_injuries.append(critical_injury)
            else:
                self.player1_health -= damage
                self.player2_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player1
                if critical_injury:
                    self.player1_critical_injuries.append(critical_injury)

            sleep_duration = random.uniform(1, 2) + (3 if critical_message else 0)  # Add extra seconds for critical hits
            await asyncio.sleep(sleep_duration)

            # Edit the round message with updated content
            await round_message.edit(content=f"Round {round_number} in progress: {message}\n")

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
            print(f"Error during play_turn: {e}")
            print(f"Attacker: {attacker.display_name}, Defender: {defender.display_name}")
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
            await asyncio.sleep(random.uniform(1, 3))

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

        await self.update_health_bars(round_number)

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
        fight_image_path = self.generate_fight_image()
        await self.channel.send(file=discord.File(fight_image_path))
        await asyncio.sleep(10)

        for round_number in range(1, self.rounds + 1):
            await self.play_round(round_number)

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
