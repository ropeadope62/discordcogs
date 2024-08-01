import random
import aiohttp
import asyncio
import discord
import math
import requests
from discord import File, Webhook
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from .fighting_constants import (
    STRIKES, CRITICAL_RESULTS, CRITICAL_MESSAGES, BODY_PARTS, GRAPPLE_KEYWORDS, GRAPPLE_ACTIONS, BODY_PART_INJURIES,
    STRIKE_ACTIONS, TKO_MESSAGES, KO_MESSAGES, KO_VICTOR_MESSAGE, TKO_VICTOR_MESSAGE, REFEREE_STOPS, FIGHT_RESULT_LONG,
    ROUND_RESULTS_WIN, ROUND_RESULTS_CLOSE, TKO_MESSAGE_FINALES, KO_VICTOR_FLAVOR
)
from .bullshido_ai import generate_hype, generate_hype_challenge
class FightingGame:
    active_games = {}
    WEBHOOK_URL = "https://ptb.discord.com/api/webhooks/1264078679026307133/C-mjG4H90DXpSdKT2FAXcVHLnZbQlIUUZE1SQFrajfLi2hZYvJnjE8cET0UcZvMBxiOR"

    def __init__(self, bot, channel: discord.TextChannel, player1: discord.Member, player2: discord.Member, player1_data: dict, player2_data: dict, bullshido_cog, wager=0, challenge=False):
        self.bot = bot
        self.channel = channel
        self.player1_avatar_url = None
        self.player2_avatar_url = None
        self.player1 = player1
        self.player2 = player2
        self.player1_data = player1_data
        self.player2_data = player2_data
        self.player1_stamina = self.player1_data.get('stamina_level', 100) + (self.player1_data.get('stamina_bonus', 0) * 5)
        self.player2_stamina = self.player2_data.get('stamina_level', 100) + (self.player2_data.get('stamina_bonus', 0) * 5)
        self.player1_health = 100 + (self.player1_data.get('health_bonus', 0) * 10)
        self.player2_health = 100 + (self.player2_data.get('health_bonus', 0) * 10)
        self.rounds = 3
        self.max_strikes_per_round = 5
        self.player1_score = 0
        self.player2_score = 0
        self.bullshido_cog = bullshido_cog
        self.winner = None
        self.wager = wager
        self.challenge = challenge
        self.training_weight = 0.15  # 15% contribution
        self.diet_weight = 0.15  # 15% contribution
        self.player1_critical_message = ""
        self.player2_critical_message = ""
        self.player1_critical_injuries = []
        self.player2_critical_injuries = []
        self.user_config = {
            str(player1.id): player1_data,
            str(player2.id): player2_data
        }
        self.base_health = 100
        self.ACTION_COST = 10
        self.BASE_MISS_PROBABILITY = 0.15
        self.BASE_STAMINA_COST = 10
        self.FIGHT_TEMPLATE_PATH = "/home/slurms/ScrapGPT/scrapgpt_data/cogs/Bullshido/bullshido_template.png"
        self.BASE_TKO_PROBABILITY = 0.5
        self.embed_message = None
        if self.determine_first_turn(player1_data['training_level'], player2_data['training_level']):
            self.current_turn = player1
        else:
            self.current_turn = player2

    @staticmethod
    def is_game_active(channel_id):
        return FightingGame.active_games.get(channel_id, False)

    @staticmethod
    def set_game_active(channel_id, status):
        FightingGame.active_games[channel_id] = status
        
    @staticmethod
    def adjust_red_channel(image, damage_percentage):
            image = image.convert("RGBA")
            r, g, b, a = image.split()
            r = r.point(lambda i: min(i + int(255 * (damage_percentage / 100)), 255))
            image = Image.merge('RGBA', (r, g, b, a))
            return image

    @staticmethod
    def split_text_into_lines(text, max_length):
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                if current_line:
                    current_line += ' ' + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return '\n'.join(lines)
    
    async def determine_first_turn(self, attacker_training, defender_training):
        # Determine who goes first based on training levels
        total_training = attacker_training + defender_training
        attacker_probability = attacker_training / total_training
        defender_probability = defender_training / total_training
        # If both training levels are equal, its a 50/50 chance
        return random.choices([True, False], [attacker_probability, defender_probability])[0]
    
    async def generate_fight_image(self):
        template_path = self.FIGHT_TEMPLATE_PATH
        background = Image.open(template_path)
        font_path = '/home/slurms/ScrapGPT/scrapgpt_data/cogs/CogManager/cogs/bullshido/osaka.ttf'
        font = ImageFont.truetype(font_path, size=20)
        header_font = ImageFont.truetype(font_path, size=34)

        player1_avatar_bytes = await self.player1.avatar.read()
        player2_avatar_bytes = await self.player2.avatar.read()
        player1_avatar = Image.open(BytesIO(player1_avatar_bytes)).convert("RGBA")
        player2_avatar = Image.open(BytesIO(player2_avatar_bytes)).convert("RGBA")
        player1_total_wins = sum(self.player1_data['wins'].values())
        player1_total_losses = sum(self.player1_data['losses'].values())
        player2_total_wins = sum(self.player2_data['wins'].values())
        player2_total_losses = sum(self.player2_data['losses'].values())

        player1_avatar = player1_avatar.resize((150, 150))
        player2_avatar = player2_avatar.resize((150, 150))

        player1_avatar = player1_avatar.rotate(-0, expand=True)
        player2_avatar = player2_avatar.rotate(-0, expand=True)

        background.paste(player1_avatar, (90, 75), player1_avatar)
        background.paste(player2_avatar, (365, 75), player2_avatar)

        draw = ImageDraw.Draw(background)

        player1_name = FightingGame.split_text_into_lines(f"{self.player1.display_name}", 18)
        player1_details = (
            f"Style: {self.player1_data['fighting_style']}\n"
            f"Record: {player1_total_wins} Wins \n {player1_total_losses} Losses"
        )
        player2_name = FightingGame.split_text_into_lines(f"{self.player2.display_name}", 18)
        player2_details = (
            f"Style: {self.player2_data['fighting_style']}\n"
            f"Record: {player2_total_wins} Wins \n {player2_total_losses} Losses"
        )

        player1_name_text_position = (80, 53)
        player2_name_text_position = (355, 53)
        player1_text_position = (80, 175)
        player2_text_position = (355, 175)

        def draw_text_with_shadow(draw, position, text, font, shadow_color, text_color, offset=(2, 2)):
            x, y = position
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
            draw.text(position, text, font=font, fill=text_color)
            

        shadow_color = (0, 0, 0)
        text_color = (249, 4, 43)

        draw_text_with_shadow(draw, player1_name_text_position, player1_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_name_text_position, player2_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player1_text_position, player1_details, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_text_position, player2_details, font, shadow_color, text_color)

        intro_message = (
            "Introducing the fighters!\n"
        )
        intro_subtitle = ("")

        intro_text_position = (80, 6)
        intro_subtitle_position = (20, 40)
        draw_text_with_shadow(draw, intro_text_position, intro_message, header_font, shadow_color, text_color)
        draw_text_with_shadow(draw, intro_subtitle_position, intro_subtitle, header_font, shadow_color, text_color)

        final_image_path = '/home/slurms/ScrapGPT/ScrapGPT/logs/fight_image.png'
        background.save(final_image_path)

        return final_image_path
    
    def create_health_bar(self, current_health, base_health):
        progress = current_health / base_health
        progress_bar_length = 30
        progress_bar_filled = int(progress * progress_bar_length)
        progress_bar = "[" + ("=" * progress_bar_filled)
        progress_bar += "=" * (progress_bar_length - progress_bar_filled) + "]"
        if progress_bar_filled < progress_bar_length:
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

    async def update_health_bars(self, round_number, latest_message, round_result, fight_over=False, final_result=None):

        player1_health_bar = self.create_health_bar(self.player1_health, self.base_health)
        player2_health_bar = self.create_health_bar(self.player2_health, self.base_health)
        player1_stamina_status = self.get_stamina_status(self.player1_stamina)
        player2_stamina_status = self.get_stamina_status(self.player2_stamina)

        if fight_over:
            title = final_result if final_result else f"Fight Concluded - {self.player1.display_name} vs {self.player2.display_name}"
        else:
            title = f"Round {round_number} - {self.player1.display_name} vs {self.player2.display_name}"
            
        embed = discord.Embed(
            title=title,
            color=0xFF0000
        )

        # Add player 1 information
        embed.add_field(name=f"{self.player1.display_name}'s Health", value=f"{player1_health_bar} {self.player1_health}HP", inline=True)

        # Add player 1 stamina and injuries
        embed.add_field(name=f"{self.player1.display_name}'s Stamina", value=player1_stamina_status, inline=False)
        if self.player1_critical_injuries:
            embed.add_field(name=f"{self.player1.display_name} Injuries", value=", ".join(self.player1_critical_injuries), inline=False)
        if self.player1_data.get("permanent_injuries"):
            embed.add_field(name=f"{self.player1.display_name} Permanent Injuries", value=", ".join(self.player1_data["permanent_injuries"]), inline=False)

        # Add player 2 information
        embed.add_field(name=f"{self.player2.display_name}'s Health", value=f"{player2_health_bar} {self.player2_health}HP", inline=True)

        # Add player 2 stamina and injuries
        embed.add_field(name=f"{self.player2.display_name}'s Stamina", value=player2_stamina_status, inline=False)
        if self.player2_critical_injuries:
            embed.add_field(name=f"{self.player2.display_name} Injuries", value=", ".join(self.player2_critical_injuries), inline=False)
        if self.player2_data.get("permanent_injuries"):
            embed.add_field(name=f"{self.player2.display_name} Permanent Injuries", value=", ".join(self.player2_data["permanent_injuries"]), inline=False)

        if round_result and not fight_over:
            embed.add_field(name="Round Result", value=round_result, inline=False)
        embed.add_field(name="Latest Strike", value=latest_message, inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/7KK90YH/bullshido.png")

        if self.embed_message:
            await self.embed_message.edit(embed=embed)
        else:
            self.embed_message = await self.channel.send(embed=embed)


    def calculate_adjusted_damage(self, base_damage, training_level, diet_level, damage_bonus):
        training_bonus = math.log10(training_level + 1) * self.training_weight
        diet_bonus = math.log10(diet_level + 1) * self.diet_weight
        total_damage_bonus = 1 + training_bonus + diet_bonus + (damage_bonus * 0.10)
        adjusted_damage = base_damage * total_damage_bonus
        return round(adjusted_damage)
    
    def is_critical_hit(self, attacker_data, defender_data):
        critical_chance = self.CRITICAL_CHANCE

        # Adjust critical chance based on attacker and defender stats
        attacker_training = attacker_data.get("training_level", 0)
        defender_training = defender_data.get("training_level", 0)
        attacker_intimidation = attacker_data.get("intimidation_level", 0)
        defender_intimidation = defender_data.get("intimidation_level", 0)

        # based on difference in training and intimidation, adjust as needed
        critical_chance += 0.01 * (attacker_training - defender_training)
        critical_chance += 0.01 * (attacker_intimidation - defender_intimidation)

        # Clamp critical chance to a reasonable rate 
        critical_chance = max(0, min(critical_chance, 0.3))

        return random.random() < critical_chance

    def get_strike_damage(self, style, attacker, defender, defender_data, body_part):
        strike = ""
        damage_range = (0, 0)
        base_damage = 0
        modified_damage = 0
        message = ""
        conclude_message = ""
        critical_injury = ""
        critical_result_key = ""

        try:
            strike, damage_range = random.choice(list(STRIKES[style].items()))
            base_damage = random.randint(*damage_range)
            damage_bonus = attacker.get('damage_bonus', 0)  # Get attacker's damage bonus from user config
            modified_damage = self.calculate_adjusted_damage(base_damage, attacker['training_level'], attacker['nutrition_level'], damage_bonus)
            modifier = random.uniform(0.8, 1.3)

            is_critical_hit = random.random() < self.CRITICAL_CHANCE
            if is_critical_hit:
                modified_damage = base_damage * 2
                if possible_injuries := BODY_PART_INJURIES.get(body_part, []):
                    critical_injury = random.choice(possible_injuries)
                    for result, injury in CRITICAL_RESULTS.items():
                        if injury == critical_injury:
                            critical_result_key = result
                            break
                    conclude_message = critical_result_key.format(defender=defender.display_name)
                    message = random.choice(CRITICAL_MESSAGES)
                    if random.random() < self.PERMANENT_INJURY_CHANCE:
                        critical_injury = f"Permanent Injury: {critical_injury}"
            if body_part in defender_data.get('permanent_injuries', []):
                modified_damage *= 2
            else:
                modified_damage = round(modified_damage * modifier)
            return strike, modified_damage, message, conclude_message, critical_injury, body_part
        except Exception as e:
            self.bullshido_cog.logger.error(f"Error during get_strike_damage: {e}")
            self.bullshido_cog.logger.debug(f"Attacker: {attacker}, Defender: {defender}, Style: {style}")
            return strike, modified_damage, message, conclude_message, critical_injury, body_part

    async def end_fight(self, winner, loser):
        self.bullshido_cog.logger.info(f"Ending fight between {winner} and {loser}.")
        await self.bullshido_cog.add_xp(winner, 100, self.channel)
        await self.bullshido_cog.add_xp(loser, 50, self.channel)

    async def target_bodypart(self):
        bodypart = random.choice(BODY_PARTS)
        return bodypart

    def is_grapple_move(self, strike):
        return any(keyword.lower() in strike.lower() for keyword in GRAPPLE_KEYWORDS)

    def calculate_miss_probability(self, attacker_stamina, attacker_training, defender_training, defender_stamina, attacker_intimidation, defender_intimidation):
        miss_probability = self.BASE_MISS_PROBABILITY

        if attacker_stamina < 50:
            miss_probability += 0.05

        if defender_stamina > 50:
            miss_probability += 0.05

        miss_probability -= 0.01 * math.log10(attacker_training + 1)
        miss_probability += 0.01 * math.log10(defender_training + 1)
        
        intimidation_factor = (defender_intimidation - attacker_intimidation) * 0.01
        miss_probability += intimidation_factor

        return min(max(miss_probability, 0.05), 0.20)

    def regenerate_stamina(self, current_stamina, training_level, diet_level):
        regeneration_rate = (training_level + diet_level) / 20
        return min(current_stamina + regeneration_rate, self.base_health)

    async def play_turn(self, round_message, round_number):
        try:
            attacker = self.player1 if self.current_turn == self.player1 else self.player2
            defender = self.player2 if self.current_turn == self.player1 else self.player1
            attacker_stamina = self.player1_stamina if self.current_turn == self.player1 else self.player2_stamina
            defender_stamina = self.player2_stamina if self.current_turn == self.player1 else self.player1_stamina
            attacker_training = self.player1_data["training_level"] if self.current_turn == self.player1 else self.player2_data["training_level"]
            defender_training = self.player2_data["training_level"] if self.current_turn == self.player1 else self.player1_data["training_level"]
            attacker_intimidation = self.player1_data["intimidation_level"] if self.current_turn == self.player1 else self.player2_data["intimidation_level"]
            defender_intimidation = self.player2_data["intimidation_level"] if self.current_turn == self.player1 else self.player1_data["intimidation_level"]
            style = self.player1_data["fighting_style"] if self.current_turn == self.player1 else self.player2_data["fighting_style"]

            defender_data = self.player2_data if self.current_turn == self.player1 else self.player1_data


            miss_probability = self.calculate_miss_probability(attacker_stamina, attacker_training, defender_training, defender_stamina, attacker_intimidation, defender_intimidation)
            if random.random() < miss_probability:
                miss_message = f"{attacker.display_name} missed their attack on {defender.display_name}!"
                await self.update_health_bars(round_number, miss_message, None)
                self.current_turn = defender
                return False

            bodypart = await self.target_bodypart()
            strike, damage, critical_message, conclude_message, critical_injury, targeted_bodypart = self.get_strike_damage(style, self.player1_data if attacker == self.player1 else self.player2_data, defender_data, bodypart)

            if not strike:
                await self.update_health_bars(round_number, "An error occurred during the turn: Failed to determine strike.", None)
                return True

            injury_message = ""
            if bodypart in defender_data.get('permanent_injuries', []):
                injury_message = f"{attacker}'s {strike} hits {defender}'s already injured {bodypart}, causing double damage!"

            if self.is_grapple_move(strike):
                action = random.choice(GRAPPLE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} causing {damage} damage! {conclude_message}. {injury_message}"
            else:
                action = random.choice(STRIKE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {targeted_bodypart} causing {damage} damage! {conclude_message}. {injury_message}"

            if self.current_turn == self.player1:
                self.player2_health -= damage
                self.player1_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player2
                if critical_injury:
                    self.player2_critical_injuries.append(critical_injury)
                    if "Permanent Injury" in critical_injury:
                        permanent_injury = critical_injury.split(": ")[1]
                        await self.add_permanent_injury(defender, permanent_injury, targeted_bodypart)
            else:
                self.player1_health -= damage
                self.player2_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player1
                if critical_injury:
                    self.player1_critical_injuries.append(critical_injury)
                    if "Permanent Injury" in critical_injury:
                        permanent_injury = critical_injury.split(": ")[1]
                        await self.add_permanent_injury(defender, permanent_injury, targeted_bodypart)

            sleep_duration = random.uniform(1, 2) + (3 if critical_message else 0)
            await asyncio.sleep(sleep_duration)

            if "Permanent Injury" in critical_injury:
                message += f"\n**Permanent Injury:** {critical_injury.split(': ')[1]}"

            await self.update_health_bars(round_number, message, None)

            # Check for KO
            if self.player1_health <= 0 or self.player2_health <= 0:
                await asyncio.sleep(2)
                await self.declare_winner_by_ko(round_message)
                return True

            # Check for TKO
            tko_probability = self.calculate_tko_probability(attacker_stamina, attacker_training, defender_training, defender_stamina, attacker_intimidation, defender_intimidation)
            if (self.player1_health < 20 or self.player2_health < 20) and random.random() < tko_probability:
                await asyncio.sleep(2)
                if self.player1_health < 20:
                    await self.declare_winner_by_tko(round_message, self.player1)
                else:
                    await self.declare_winner_by_tko(round_message, self.player2)
                return True

            return False
        except Exception as e:
            self.bullshido_cog.logger.error(f"Error during play_turn: {e}")
            self.bullshido_cog.logger.error(f"Attacker: {attacker.display_name}, Defender: {defender.display_name}")
            await self.update_health_bars(round_number, f"An error occurred during the turn: {e}", None)
            return True
        
    def calculate_tko_probability(self, attacker_stamina, attacker_training, defender_training, defender_stamina, attacker_intimidation, defender_intimidation):
        base_tko_chance = self.BASE_TKO_PROBABILITY
        stamina_factor = (attacker_stamina - defender_stamina) * 0.01
        training_factor = (attacker_training - defender_training) * 0.01
        intimidation_factor = (attacker_intimidation - defender_intimidation) * 0.01
        tko_probability = base_tko_chance + stamina_factor + training_factor + intimidation_factor

        # Probability clamped between 0 and 0.75 (75%)
        return max(0, min(0.75, tko_probability))

        
    async def add_permanent_injury(self, user: discord.Member, injury, body_part):
        """ Add a permanent injury to a user. """
        user_data = self.user_config[str(user.id)]
        if "permanent_injuries" not in user_data:
            user_data["permanent_injuries"] = []
        user_data["permanent_injuries"].append(f"{injury}")
        await self.bullshido_cog.config.user(user).permanent_injuries.set(user_data["permanent_injuries"])


    async def record_result(self, winner, loser, result_type):
        try:
            if result_type == "DRAW":
                
                await self.bullshido_cog.config.user(self.player1).draws.set(
                    await self.bullshido_cog.config.user(self.player1).draws() + 1
                )
                await self.bullshido_cog.config.user(self.player2).draws.set(
                    await self.bullshido_cog.config.user(self.player2).draws() + 1
                )
            else:
                await self.bullshido_cog.update_player_stats(winner, win=True, result_type=result_type, opponent_name=loser.display_name)
                await self.bullshido_cog.update_player_stats(loser, win=False, result_type=result_type, opponent_name=winner.display_name)
                current_loser_morale = await self.bullshido_cog.config.user(loser).morale()
                current_winner_morale = await self.bullshido_cog.config.user(winner).morale()
                new_loser_morale = max(0, current_loser_morale - 20)
                new_winner_morale = min(100, current_winner_morale + 20)
                await self.bullshido_cog.config.user(loser).morale.set(new_loser_morale)
                await self.bullshido_cog.config.user(winner).morale.set(new_winner_morale)
        except Exception as e:
            self.bullshido_cog.logger.error(f"An error occurred: {e}")

    async def play_round(self, round_number, ctx):
        strike_count = 0
        player1_health_start = self.player1_health
        player2_health_start = self.player2_health

        self.bullshido_cog.logger.info(f"Starting Round {round_number}")
        self.bullshido_cog.logger.info(f"Player1 Health: {self.player1_health}, Player2 Health: {self.player2_health}")

        while strike_count < self.max_strikes_per_round and self.player1_health > 0 and self.player2_health > 0:
            try:
                ko_or_tko_occurred = await self.play_turn(self.embed_message, round_number)
                if ko_or_tko_occurred:
                    return True

                strike_count += 1
                await asyncio.sleep(random.uniform(3, 4))
            except Exception as e:
                self.bullshido_cog.logger.error(f"Error during play_turn: {e}")
                raise e

        player1_health_end = self.player1_health
        player2_health_end = self.player2_health

        damage_player1 = player2_health_start - player2_health_end
        damage_player2 = player1_health_start - player1_health_end

        self.bullshido_cog.logger.info(f"Ending Round {round_number} - Player1 Health: {player1_health_end}, Player2 Health: {player2_health_end}")
        self.bullshido_cog.logger.info(f"Damage Player1: {damage_player1}, Damage Player2: {damage_player2}")  # Default round result

        self.bullshido_cog.logger.info("Evaluating round winner...")

        if damage_player1 > damage_player2:
            if damage_player1 - damage_player2 > 20:
                round_result = random.choice(ROUND_RESULTS_WIN).format(winner=self.player1.display_name)
                self.player1_score += 10
                self.player2_score += 8
            else:
                round_result = random.choice(ROUND_RESULTS_CLOSE).format(winner=self.player1.display_name)
                self.player1_score += 10
                self.player2_score += 9
            
        elif damage_player2 > damage_player1:
            if damage_player2 - damage_player1 > 20:
                round_result = random.choice(ROUND_RESULTS_WIN).format(winner=self.player2.display_name)
                self.player2_score += 10
                self.player1_score += 8
            else:
                round_result = random.choice(ROUND_RESULTS_CLOSE).format(winner=self.player2.display_name)
                self.player2_score += 10
                self.player1_score += 9
        elif damage_player1 == damage_player2:
            round_result = f"The round was a draw"
            self.player1_score += 9
            self.player2_score += 9
            self.bullshido_cog.logger.debug(f"Round was a draw")
        
        else: 
            round_result = None
            self.bullshido_cog.logger.warning("Round winner not determined correctly. Setting default value.")
            round_result = "No clear winner"

        await self.update_health_bars(round_number, "Round Ended", round_result)

        # Check for KO
        if self.player1_health <= 0 or self.player2_health <= 0:
            await self.declare_winner_by_ko(ctx)
            return True

        # Check for TKO
        tko_probability = self.calculate_tko_probability(self.player1_stamina, self.player1_data["training_level"], self.player2_data["training_level"], self.player2_stamina, self.player1_data["intimidation_level"], self.player2_data["intimidation_level"])
        if (self.player1_health < 20 or self.player2_health < 20) and random.random() < tko_probability:
            if self.player1_health < 20:
                await self.declare_winner_by_tko(ctx, self.player1)
            else:
                await self.declare_winner_by_tko(ctx, self.player2)
            return True
        else: 
            return False

    async def declare_winner_by_ko(self, ctx):
        if self.player1_health <= 0:
            self.winner = self.player2
            loser = self.player1
        else:
            self.winner = self.player1
            loser = self.player2
        ko_message = random.choice(KO_MESSAGES).format(loser=loser.display_name)
        ko_victor_message = random.choice(KO_VICTOR_MESSAGE)
        ko_victor_flavor = random.choice(KO_VICTOR_FLAVOR)
        final_message = (
            f"{ko_message} {self.winner.display_name} {ko_victor_message}. {ko_victor_flavor}"
        )
        await self.update_health_bars(0, final_message, "KO Victory!", fight_over=True, final_result=f"KO Victory for {self.winner.display_name}!")  # Update embed with KO result
        await self.record_result(self.winner, loser, "KO")
        FightingGame.set_game_active(self.channel.id, False)
        await self.end_fight(self.winner, loser)

    async def declare_winner_by_tko(self, ctx, loser):
        self.winner = self.player1 if loser == self.player2 else self.player2
        tko_message_flavor = random.choice(TKO_MESSAGES).format(loser=loser.display_name)
        referee_stop_flavor = random.choice(REFEREE_STOPS)
        tko_victor_message = random.choice(TKO_VICTOR_MESSAGE)
        tko_finale = random.choice(TKO_MESSAGE_FINALES)
        final_message = (
            f"{tko_message_flavor} {referee_stop_flavor}, {self.winner.display_name} wins the fight by TKO!\n"
            f"{self.winner.display_name} {tko_victor_message}, {tko_finale}"
        )
        await self.update_health_bars(0, final_message, "TKO Victory!", fight_over=True, final_result=f"TKO Victory for {self.winner.display_name}!")  # Update embed with TKO result
        await self.record_result(self.winner, loser, "TKO")
        FightingGame.set_game_active(self.channel.id, False)
        await self.end_fight(self.winner, loser)


    async def start_game(self, ctx):
        try:
            channel_id = self.channel.id

            if FightingGame.is_game_active(channel_id):
                await self.channel.send("A game is already in progress in this channel.")
                return

            guild = self.channel.guild
            self.rounds = await self.bullshido_cog.config.guild(guild).rounds()
            self.max_strikes_per_round = await self.bullshido_cog.config.guild(guild).max_strikes_per_round()
            self.training_weight = await self.bullshido_cog.config.guild(guild).training_weight()
            self.diet_weight = await self.bullshido_cog.config.guild(guild).diet_weight()
            self.base_health = await self.bullshido_cog.config.guild(guild).base_health()
            self.ACTION_COST = await self.bullshido_cog.config.guild(guild).action_cost()
            self.BASE_MISS_PROBABILITY = await self.bullshido_cog.config.guild(guild).base_miss_probability()
            self.BASE_STAMINA_COST = await self.bullshido_cog.config.guild(guild).base_stamina_cost()
            self.CRITICAL_CHANCE = await self.bullshido_cog.config.guild(guild).critical_chance()
            self.PERMANENT_INJURY_CHANCE = await self.bullshido_cog.config.guild(guild).permanent_injury_chance()
            
            player1_data = await self.bullshido_cog.config.user(self.player1).all()
            player2_data = await self.bullshido_cog.config.user(self.player2).all()

            # Get the bonus values from the user config for each player, default to 0 if not present
            player1_health_bonus = player1_data.get("health_bonus", 0)
            player1_stamina_bonus = player1_data.get("stamina_bonus", 0)
            player1_damage_bonus = player1_data.get("damage_bonus", 0)

            player2_health_bonus = player2_data.get("health_bonus", 0)
            player2_stamina_bonus = player2_data.get("stamina_bonus", 0)
            player2_damage_bonus = player2_data.get("damage_bonus", 0)

            # Apply bonuses to player stats
            self.player1_health = self.base_health + player1_health_bonus
            self.player2_health = self.base_health + player2_health_bonus

            self.player1_stamina = self.base_health + player1_stamina_bonus
            self.player2_stamina = self.base_health + player2_stamina_bonus

            self.player1_damage_bonus = player1_damage_bonus
            self.player2_damage_bonus = player2_damage_bonus

            FightingGame.set_game_active(channel_id, True)
            fight_image_path = await self.generate_fight_image()
            user_config = await self.bullshido_cog.config.all_users()
            if self.challenge: 
                narrative = generate_hype_challenge(self.user_config, str(self.player1.id), str(self.player2.id), self.player1.display_name, self.player2.display_name, self.wager)
            else: 
                narrative = generate_hype(self.user_config, str(self.player1.id), str(self.player2.id), self.player1.display_name, self.player2.display_name)
            
            embed = discord.Embed(
                title=f"{self.player1.display_name} vs {self.player2.display_name}",
                description=f"{narrative}",
                color=0xFF0000
            )
            file = discord.File(fight_image_path, filename="fight_image.png")
            embed.set_image(url="attachment://fight_image.png")

            self.embed_message = await self.channel.send(file=file, embed=embed)
            await asyncio.sleep(15)

            await self.update_health_bars(0, "The fight is about to begin!", "Ready? FIGHT!")

            for round_number in range(1, self.rounds + 1):
                if not FightingGame.is_game_active(channel_id):
                    break
                if await self.play_round(round_number, ctx):
                    return  # Exit if KO or TKO occurred

            winner, loser = None, None
            result_type = "DRAW"
            final_message = "The fight is over! The fight is declared a draw!"

            if self.player1_score > self.player2_score:
                winner = self.player1
                loser = self.player2
                result_type = "UD" if abs(self.player1_score - self.player2_score) > 2 else "SD"
            elif self.player2_score > self.player1_score:
                winner = self.player2
                loser = self.player1
                result_type = "UD" if abs(self.player2_score - self.player1_score) > 2 else "SD"
            else:
                winner, loser = None, None
                result_type = "DRAW"
                final_message = (
                    f"The fight is over!\n"
                    f"After {self.rounds} rounds, the fight is declared a draw!\n"
                )

            if winner and loser:
                result_description = FIGHT_RESULT_LONG[result_type]
                final_message = (
                    f"The fight is over!\n"
                    f"After {self.rounds} rounds, we go to the judges' scorecard for a decision.\n"
                    f"The judges scored the fight {self.player1_score if winner == self.player1 else self.player2_score} - {self.player1_score if winner == self.player2 else self.player2_score} for the winner, by {result_description}, {winner.display_name}!"
                )

            await self.update_health_bars(self.rounds, final_message, "Decision Victory", fight_over=True, final_result=f"Decision Victory for {winner.display_name if winner else 'No one'}!")
            await self.record_result(winner, loser, result_type)

            FightingGame.set_game_active(channel_id, False)
            await self.end_fight(winner, loser)

            self.winner = winner  # Set the winner attribute based on the fight score

        except Exception as e:
            self.bullshido_cog.logger.error(f"Error during start_game: {e}")
            raise e


