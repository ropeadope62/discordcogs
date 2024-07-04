import random
import asyncio
import discord
import math
import requests
from .fighting_constants import STRIKES, BODY_PARTS, STRIKE_ACTIONS, GRAPPLE_ACTIONS, GRAPPLE_KEYWORDS, CRITICAL_MESSAGES, KO_MESSAGES, TKO_MESSAGES, FIGHT_RESULT_LONG, REFEREE_STOPS, TKO_VICTOR_MESSAGE, KO_VICTOR_MESSAGE, CRITICAL_RESULTS
from PIL import Image, ImageDraw, ImageFont, ImageTransform
from io import BytesIO
import os

class FightingGame:
    active_games = {}
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
            
    @staticmethod
    def is_game_active(channel_id):
        return FightingGame.active_games.get(channel_id, False)
    
    @staticmethod
    def set_game_active(channel_id, status):
        FightingGame.active_games[channel_id] = status
    
    async def generate_fight_image(self):
        # Load the background template
        template_url = self.FIGHT_TEMPLATE_URL
        response = requests.get(template_url)
        background = Image.open(BytesIO(response.content))
        font_path ='/home/slurms/ScrapGPT/scrapgpt_data/cogs/CogManager/cogs/bullshido/osaka.ttf'
        font = ImageFont.truetype(font_path, size=18)
        header_font = ImageFont.truetype(font_path, size=32)
        
        # Load player avatars
        player1_avatar_bytes = await self.player1.avatar.read()
        player2_avatar_bytes = await self.player2.avatar.read()
        player1_avatar = Image.open(BytesIO(player1_avatar_bytes)).convert("RGBA")
        player2_avatar = Image.open(BytesIO(player2_avatar_bytes)).convert("RGBA")        
        player1_total_wins = sum(self.player1_data['wins'].values())
        player1_total_losses = sum(self.player1_data['losses'].values())
        player2_total_wins = sum(self.player2_data['wins'].values())
        player2_total_losses = sum(self.player2_data['losses'].values())

        # Resize avatars to fit the template (assuming size 200x200 for the example)
        player1_avatar = player1_avatar.resize((150, 150))
        player2_avatar = player2_avatar.resize((150, 150))

        # Rotate avatars 90 degrees clockwise
        player1_avatar = player1_avatar.rotate(-0, expand=True)
        player2_avatar = player2_avatar.rotate(-0, expand=True)

        # Paste avatars onto the template
        background.paste(player1_avatar, (100, 75), player1_avatar)
        background.paste(player2_avatar, (375, 75), player2_avatar)

        # Add text to the image
        draw = ImageDraw.Draw(background)

        # Player details
        player1_name = (
            f"{self.player1.display_name}\n")
        player1_details = (
            f"Style: {self.player1_data['fighting_style']}\n"
            f"Record: {player1_total_wins} Wins \n {player1_total_losses} Losses"
        )
        player2_name = (
            f"{self.player2.display_name}\n")
        player2_details = (
            f"Style: {self.player2_data['fighting_style']}\n"
            f"Record: {player2_total_wins} Wins \n {player2_total_losses} Losses"
        )

        # Define text positions
        player1_name_text_position = (100, 55)
        player2_name_text_position = (375, 55)
        player1_text_position = (100, 175)
        player2_text_position = (375, 175)

        def draw_text_with_shadow(draw, position, text, font, shadow_color, text_color, offset=(2, 2)):
            x, y = position
            # Draw shadow
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
            # Draw text
            draw.text(position, text, font=font, fill=text_color)

        shadow_color = (0, 0, 0)
        text_color = (249,4,43)

        # Add player details text to the image
        draw_text_with_shadow(draw, player1_name_text_position, player1_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_name_text_position, player2_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player1_text_position, player1_details, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_text_position, player2_details, font, shadow_color, text_color)

        # Intro message
        intro_message = (
            "Introducing the fighters!\n"
        )
        # Intro subtitle
        intro_subtitle = ("")

        # Define text position for intro message
        intro_text_position = (80, 10)
        intro_subtitle_position = (20,40)
        # Add intro message to the image
        draw_text_with_shadow(draw, intro_text_position, intro_message, header_font, shadow_color, text_color)
        draw_text_with_shadow(draw, intro_subtitle_position, intro_subtitle, header_font, shadow_color, text_color)


        # Save the final image
        final_image_path = '/home/slurms/ScrapGPT/ScrapGPT/logs/fight_image.png'
        background.save(final_image_path)

        return final_image_path

            
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

    
    def get_stamina_status(self, stamina):
        if stamina >= 75:
            return "Fresh"
        elif stamina >= 50:
            return "Winded"
        elif stamina >= 25:
            return "Gassed"
        else:
            return "Exhausted" 
    
    async def update_health_bars(self, round_number, latest_message, round_result):
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
        
        if round_result:
            embed.add_field(name="Round Result", value=round_result, inline=False)
        embed.add_field(name="Latest Strike", value=latest_message, inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")

        await self.embed_message.edit(embed=embed)


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

    async def play_turn(self, round_number):
        fight_ended = False
        attacker = self.player1 if self.current_turn == self.player1 else self.player2
        defender = self.player2 if self.current_turn == self.player1 else self.player1
        attacker_stamina = self.player1_stamina if self.current_turn == self.player1 else self.player2_stamina
        defender_stamina = self.player2_stamina if self.current_turn == self.player1 else self.player1_stamina
        attacker_training = self.player1_data["training_level"] if self.current_turn == self.player1 else self.player2_data["training_level"]
        defender_training = self.player2_data["training_level"] if self.current_turn == self.player1 else self.player1_data["training_level"]
        defender_diet = self.player2_data.get("diet_level", 1) if self.current_turn == self.player1 else self.player1_data.get("diet_level", 1)
        defender_morale = await self.bullshido_cog.config.user(defender).morale()
        style = self.player1_data["fighting_style"] if self.current_turn == self.player1 else self.player2_data["fighting_style"]

        try:
            miss_probability = self.calculate_miss_probability(attacker_stamina, attacker_training, defender_training, defender_stamina)
            if random.random() < miss_probability:
                # Misses the attack
                latest_message = f"{attacker.display_name} missed their attack on {defender.display_name}!"
                await self.update_health_bars(round_number, latest_message, "No significant events")  # Update health bars after each strike
                self.current_turn = defender  # Switch turn to the other player
                return False

            # Calculate block chance influenced by training, diet, and morale
            base_block_chance = 0.15  # 15% base block chance
            block_bonus_training = 0.01 * math.log10(defender_training + 1)  # Block bonus from training level
            block_bonus_diet = 0.01 * math.log10(defender_diet + 1)  # Block bonus from diet level
            block_bonus_morale = 0.01 * (defender_morale / 100)  # Block bonus from morale (scaled to 0-1 range)
            block_chance = base_block_chance + block_bonus_training + block_bonus_diet + block_bonus_morale

            if random.random() < block_chance:
                # Attack is blocked
                latest_message = f"{defender.display_name} blocked the attack from {attacker.display_name}!"
                await self.update_health_bars(round_number, latest_message, "No significant events")  # Update health bars after each strike
                self.current_turn = defender  # Switch turn to the other player
                return False

            # Proceed with calculating damage if the attack is not missed or blocked
            strike, damage, critical_message, conclude_message, critical_injury = self.get_strike_damage(style, self.player1_data if attacker == self.player1 else self.player2_data, defender)
            if not strike:
                latest_message = f"An error occurred during the turn: Failed to determine strike."
                await self.update_health_bars(round_number, latest_message, "No significant events")
                return True

            bodypart = await self.target_bodypart()

            if self.is_grapple_move(strike):
                action = random.choice(GRAPPLE_ACTIONS)
                latest_message = f"{critical_message} {attacker.display_name} {action} a {strike} causing {damage} damage! {conclude_message}"
            else:
                action = random.choice(STRIKE_ACTIONS)
                latest_message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {bodypart} causing {damage} damage! {conclude_message}"

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

            sleep_duration = random.uniform(2, 3) + (4 if critical_message else 0)  # Add extra seconds for critical hits
            await asyncio.sleep(sleep_duration)

            # Update the embed with the latest message and health bars
            await self.update_health_bars(round_number, latest_message, "No significant events")  # Update health bars after each strike

            # Check for KO
            if self.player1_health <= 0 or self.player2_health <= 0:
                await self.declare_winner_by_ko(round_number, latest_message)
                return True

            # Check for TKO
            if (self.player1_health < 20 or self.player2_health < 20) and random.random() < 0.5:
                await self.declare_winner_by_tko(round_number, latest_message, defender)
                return True

            return False
        except Exception as e:
            latest_message = f"An error occurred during the turn: {e}"
            print(f"Error during play_turn: {e}")
            print(f"Attacker: {attacker.display_name}, Defender: {defender.display_name}")
            await self.update_health_bars(round_number, latest_message, "No significant events")  # Update health bars with error message
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
        await self.update_health_bars(0, final_message, "KO Victory!")  # Update embed with KO result
        await self.record_result(winner, loser, "KO")


    async def declare_winner_by_tko(self, round_message, loser):
        winner = self.player1 if loser == self.player2 else self.player2
        tko_message_flavor = random.choice(TKO_MESSAGES).format(loser=loser.display_name)
        referee_stop_flavor = random.choice(REFEREE_STOPS)
        tko_victor_message = random.choice(TKO_VICTOR_MESSAGE)

        final_message = (
            f"{tko_message_flavor} {referee_stop_flavor}, {winner.display_name} wins the fight by TKO!\n"
            f"{winner.display_name} {tko_victor_message}, Wow!"
        )
        await round_message.edit(content=final_message)
        await self.update_health_bars(0, final_message, "TKO Victory!")  # Update embed with TKO result
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
        except Exception as e:
            print(f"An error occurred: {e}")

    async def play_round(self, round_number):
        strike_count = 0
        player1_health_start = self.player1_health
        player2_health_start = self.player2_health

        while strike_count < self.max_strikes_per_round and self.player1_health > 0 and self.player2_health > 0:
            ko_or_tko_occurred = await self.play_turn(round_number)
            if ko_or_tko_occurred:
                return True  # End the round early if a KO or TKO occurs

            strike_count += 1
            await asyncio.sleep(random.uniform(3))

        player1_health_end = self.player1_health
        player2_health_end = self.player2_health

        damage_player1 = player2_health_start - player2_health_end
        damage_player2 = player1_health_start - player1_health_end

        print(f"Ending Round {round_number} - Player1 Health: {player1_health_end}, Player2 Health: {player2_health_end}")

        if damage_player1 > damage_player2:
            if damage_player1 - damage_player2 > 20:
                self.player1_score += 10
                self.player2_score += 8
                round_result = f"{self.player1.display_name} won the round handily!"
            else:
                self.player1_score += 10
                self.player2_score += 9
                round_result = f"{self.player1.display_name} had the edge this round!"
        else:
            if damage_player2 > damage_player1 and damage_player2 - damage_player1 > 20:
                self.player1_score += 8
                self.player2_score += 10
                round_result = f"{self.player2.display_name} won the round handily!"
            else:
                self.player1_score += 9
                self.player2_score += 10
                round_result = f"{self.player2.display_name} had the edge this round!"

        await self.update_health_bars(round_number, "End of Round", round_result)

        return False


    async def start_game(self):
        channel_id = self.channel.id

        if FightingGame.is_game_active(channel_id):
            await self.channel.send("A game is already in progress in this channel.")
            return

        FightingGame.set_game_active(channel_id, True)
        fight_image_path = await self.generate_fight_image()

        embed = discord.Embed(
            title=f"{self.player1.display_name} vs {self.player2.display_name}",
            description="The fight is about to begin!",
            color=0xFF0000
        )
        file = discord.File(fight_image_path, filename="fight_image.png")
        embed.set_image(url="attachment://fight_image.png")

        self.embed_message = await self.channel.send(file=file, embed=embed)
        await asyncio.sleep(10)

        await self.update_health_bars(0, "The fight is about to begin!", "Initial Health")  # Initial health bar update before the first round

        fight_ended = False

        for round_number in range(1, self.rounds + 1):
            fight_ended = await self.play_round(round_number)
            if fight_ended:
                break  # End the fight early if a KO or TKO occurs

        if not fight_ended:
            if self.player1_health > self.player2_health:
                winner = self.player1
                loser = self.player2
                result_type = "UD" if abs(self.player1_score - self.player2_score) > 2 else "SD"
            elif self.player2_health > self.player1_health:
                winner = self.player2
                loser = self.player1
                result_type = "UD" if abs(self.player2_score - self.player1_score) > 2 else "SD"
            else:
                if self.player1_score > self.player2_score:
                    winner = self.player1
                    loser = self.player2
                    result_type = "UD" if abs(self.player1_score - self.player2_score) > 2 else "SD"
                elif self.player2_score > self.player1_score:
                    winner = self.player2
                    loser = self.player1
                    result_type = "UD" if abs(self.player2_score - self.player1_score) > 2 else "SD"
                else:
                    result_type = "DRAW"
                    final_message = (
                        f"The fight is over!\n"
                        f"After 3 rounds, the fight is declared a draw!\n"
                    )
                    await self.update_health_bars(round_number, final_message, "Draw")  # Update embed with final result
                    FightingGame.set_game_active(channel_id, False)
                    return

            result_description = FIGHT_RESULT_LONG[result_type]
            final_message = (
                f"The fight is over!\n"
                f"After 3 rounds, we go to the judges' scorecard for a decision.\n"
                f"The judges scored the fight {self.player1_score if winner == self.player1 else self.player2_score} - {self.player1_score if winner == self.player2 else self.player2_score} for the winner, by {result_description}, {winner.display_name}!"
            )
            await self.update_health_bars(round_number, final_message, "Decision Victory")  # Update embed with final result
            await self.record_result(winner, loser, result_type)


        FightingGame.set_game_active(channel_id, False)



