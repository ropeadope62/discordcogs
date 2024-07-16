import random
import asyncio
import discord
import math
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from .fighting_constants import (STRIKES, CRITICAL_RESULTS, CRITICAL_MESSAGES, BODY_PARTS, GRAPPLE_KEYWORDS, GRAPPLE_ACTIONS, 
                                 STRIKE_ACTIONS, TKO_MESSAGES, KO_MESSAGES, KO_VICTOR_MESSAGE, TKO_VICTOR_MESSAGE, REFEREE_STOPS, FIGHT_RESULT_LONG)
from .bullshido_ai import generate_hype
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
        self.user_config = {
            str(player1.id): player1_data,
            str(player2.id): player2_data
        }
        self.max_health = 100
        self.ACTION_COST = 10
        self.BASE_MISS_PROBABILITY = 0.15
        self.BASE_STAMINA_COST = 10
        self.FIGHT_TEMPLATE_URL = "https://i.ibb.co/MSprvBG/bullshido-template.png"
        self.embed_message = None
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
        template_url = self.FIGHT_TEMPLATE_URL
        response = requests.get(template_url)
        background = Image.open(BytesIO(response.content))
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

        background.paste(player1_avatar, (100, 75), player1_avatar)
        background.paste(player2_avatar, (375, 75), player2_avatar)

        draw = ImageDraw.Draw(background)

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

        player1_name_text_position = (100, 55)
        player2_name_text_position = (375, 55)
        player1_text_position = (100, 175)
        player2_text_position = (375, 175)

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

        intro_text_position = (80, 10)
        intro_subtitle_position = (20, 40)
        draw_text_with_shadow(draw, intro_text_position, intro_message, header_font, shadow_color, text_color)
        draw_text_with_shadow(draw, intro_subtitle_position, intro_subtitle, header_font, shadow_color, text_color)

        final_image_path = '/home/slurms/ScrapGPT/ScrapGPT/logs/fight_image.png'
        background.save(final_image_path)

        return final_image_path

    def create_health_bar(self, current_health, max_health):
        progress = current_health / max_health
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

    async def update_health_bars(self, round_number, latest_message, round_result, fight_over=False, final_result = None):
        player1_health_bar = self.create_health_bar(self.player1_health, self.max_health)
        player2_health_bar = self.create_health_bar(self.player2_health, self.max_health)
        player1_stamina_status = self.get_stamina_status(self.player1_stamina)
        player2_stamina_status = self.get_stamina_status(self.player2_stamina)

        if FightingGame.is_game_active(self.channel.id):
            title = f"Round {round_number} - {self.player1.display_name} vs {self.player2.display_name}"
        else:
            title = final_result if final_result else f"Fight Concluded - {self.player1.display_name} vs {self.player2.display_name}"
        embed = discord.Embed(
            title=title,
            color=0xFF0000
        )
        embed.add_field(name=f"{self.player1.display_name}'s Health", value=f"{player1_health_bar} {self.player1_health}", inline=False)
        embed.add_field(name=f"{self.player1.display_name}'s Stamina", value=player1_stamina_status, inline=False)
        if self.player1_critical_injuries:
            embed.add_field(name=f"{self.player1.display_name} Injuries", value=", ".join(self.player1_critical_injuries), inline=False)
        if self.player1_data.get("permanent_injuries"):
            embed.add_field(name=f"{self.player1.display_name} Permanent Injuries", value=", ".join(self.player1_data["permanent_injuries"]), inline=False)

        embed.add_field(name=f"{self.player2.display_name}'s Health", value=f"{player2_health_bar} {self.player2_health}", inline=False)
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

    def calculate_adjusted_damage(self, base_damage, training_level, diet_level):
        training_bonus = math.log10(training_level + 1) * self.training_weight
        diet_bonus = math.log10(diet_level + 1) * self.diet_weight
        adjusted_damage = base_damage * (1 + training_bonus + diet_bonus)
        return round(adjusted_damage)

    def get_strike_damage(self, style, attacker, defender):
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
            modified_damage = self.calculate_adjusted_damage(base_damage, attacker['training_level'], attacker['nutrition_level'])
            modifier = random.uniform(0.8, 1.3)

            is_critical_hit = random.random() < self.CRITICAL_CHANCE
            if is_critical_hit:
                modified_damage = base_damage * 2
                critical_result_key, critical_injury = random.choice(list(CRITICAL_RESULTS.items()))
                conclude_message = critical_result_key.format(defender=defender.display_name)
                message = random.choice(CRITICAL_MESSAGES)

                if random.random() < self.PERMANENT_INJURY_CHANCE:
                    critical_injury = f"Permanent Injury: {critical_injury}"

            else:
                modified_damage = round(modified_damage * modifier)
            return strike, modified_damage, message, conclude_message, critical_injury, critical_result_key
        except Exception as e:
            print(f"Error during get_strike_damage: {e}")
            print(f"Attacker: {attacker}, Defender: {defender}, Style: {style}")
            return strike, modified_damage, message, conclude_message, critical_injury, critical_result_key

    async def target_bodypart(self):
        bodypart = random.choice(BODY_PARTS)
        return bodypart

    def is_grapple_move(self, strike):
        return any(keyword.lower() in strike.lower() for keyword in GRAPPLE_KEYWORDS)

    def calculate_miss_probability(self, attacker_stamina, attacker_training, defender_training, defender_stamina):
        miss_probability = self.BASE_MISS_PROBABILITY

        if attacker_stamina < 50:
            miss_probability += 0.05

        if defender_stamina > 50:
            miss_probability -= 0.05

        miss_probability -= 0.01 * math.log10(attacker_training + 1)
        miss_probability += 0.01 * math.log10(defender_training + 1)

        return min(max(miss_probability, 0.05), 0.5)

    def regenerate_stamina(self, current_stamina, training_level, diet_level):
        regeneration_rate = (training_level + diet_level) / 20
        return min(current_stamina + regeneration_rate, self.max_health)

    async def play_turn(self, round_message, round_number):
        if not FightingGame.is_game_active(self.channel.id):
            return True
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
                miss_message = f"{attacker.display_name} missed their attack on {defender.display_name}!"
                await self.update_health_bars(round_number, miss_message, None)
                self.current_turn = defender
                return False

            strike, damage, critical_message, conclude_message, critical_injury, critical_result_key = self.get_strike_damage(style, self.player1_data if attacker == self.player1 else self.player2_data, defender)
            if not strike:
                await self.update_health_bars(round_number, "An error occurred during the turn: Failed to determine strike.", None)
                return True

            bodypart = await self.target_bodypart()

            if self.is_grapple_move(strike):
                action = random.choice(GRAPPLE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} causing {damage} damage! {conclude_message}"
            else:
                action = random.choice(STRIKE_ACTIONS)
                message = f"{critical_message} {attacker.display_name} {action} a {strike} into {defender.display_name}'s {bodypart} causing {damage} damage! {conclude_message}"

            if self.current_turn == self.player1:
                self.player2_health -= damage
                self.player1_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player2
                if critical_injury:
                    self.player2_critical_injuries.append(critical_injury)
                    if "Permanent Injury" in critical_injury:
                        permanent_injury = critical_injury.split(": ")[1]
                        body_part = CRITICAL_RESULTS[critical_result_key]
                        await self.add_permanent_injury(defender, permanent_injury, body_part)
            else:
                self.player1_health -= damage
                self.player2_stamina -= self.BASE_STAMINA_COST
                self.current_turn = self.player1
                if critical_injury:
                    self.player1_critical_injuries.append(critical_injury)
                    if "Permanent Injury" in critical_injury:
                        permanent_injury = critical_injury.split(": ")[1]
                        body_part = CRITICAL_RESULTS[critical_result_key]
                        await self.add_permanent_injury(defender, permanent_injury, body_part)

            sleep_duration = random.uniform(1, 2) + (3 if critical_message else 0)
            await asyncio.sleep(sleep_duration)

            if "Permanent Injury" in critical_injury:
                message += f"\n**Permanent Injury:** {critical_injury.split(': ')[1]}"

            await self.update_health_bars(round_number, message, None)

            if self.player1_health <= 0 or self.player2_health <= 0:
                await self.declare_winner_by_ko(round_message)
                return True

            if (self.player1_health < 20 or self.player2_health < 20) and random.random() < 0.5:
                if self.player1_health < 20:
                    await self.declare_winner_by_tko(round_message, self.player1)
                else:
                    await self.declare_winner_by_tko(round_message, self.player2)
                return True

            return False
        except Exception as e:
            print(f"Error during play_turn: {e}")
            print(f"Attacker: {attacker.display_name}, Defender: {defender.display_name}")
            await self.update_health_bars(round_number, f"An error occurred during the turn: {e}", None)
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
        await self.update_health_bars(0, final_message, "KO Victory!", final_result=f"KO Victory for {winner.display_name}!")  # Update embed with KO result
        await self.record_result(winner, loser, "KO")
        FightingGame.set_game_active(self.channel.id, False)
        
    async def add_permanent_injury(self, user: discord.Member, injury, body_part):
        """ Add a permanent injury to a user. """
        user_data = self.user_config[str(user.id)]
        if "permanent_injuries" not in user_data:
            user_data["permanent_injuries"] = []
        user_data["permanent_injuries"].append(f"{injury}")
        await self.bullshido_cog.config.user(user).permanent_injuries.set(user_data["permanent_injuries"])

    async def declare_winner_by_tko(self, round_message, loser):
        winner = self.player1 if loser == self.player2 else self.player2
        tko_message_flavor = random.choice(TKO_MESSAGES).format(loser=loser.display_name)
        referee_stop_flavor = random.choice(REFEREE_STOPS)
        tko_victor_message = random.choice(TKO_VICTOR_MESSAGE)

        final_message = (
            f"{tko_message_flavor} {referee_stop_flavor}, {winner.display_name} wins the fight by TKO!\n"
            f"{winner.display_name} {tko_victor_message}, Wow!"
        )
        await self.update_health_bars(0, final_message, "TKO Victory!", final_result=f"TKO Victory for {winner.display_name}!")  # Update embed with TKO result
        await self.record_result(winner, loser, "TKO")
        FightingGame.set_game_active(self.channel.id, False)

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
            ko_or_tko_occurred = await self.play_turn(self.embed_message, round_number)
            if ko_or_tko_occurred:
                return True

            strike_count += 1
            await asyncio.sleep(random.uniform(3, 4))

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

        guild = self.channel.guild
        self.rounds = await self.bullshido_cog.config.guild(guild).rounds()
        self.max_strikes_per_round = await self.bullshido_cog.config.guild(guild).max_strikes_per_round()
        self.training_weight = await self.bullshido_cog.config.guild(guild).training_weight()
        self.diet_weight = await self.bullshido_cog.config.guild(guild).diet_weight()
        self.max_health = await self.bullshido_cog.config.guild(guild).max_health()
        self.ACTION_COST = await self.bullshido_cog.config.guild(guild).action_cost()
        self.BASE_MISS_PROBABILITY = await self.bullshido_cog.config.guild(guild).base_miss_probability()
        self.BASE_STAMINA_COST = await self.bullshido_cog.config.guild(guild).base_stamina_cost()
        self.CRITICAL_CHANCE = await self.bullshido_cog.config.guild(guild).critical_chance()
        self.PERMANENT_INJURY_CHANCE = await self.bullshido_cog.config.guild(guild).permanent_injury_chance()

        self.player1_health = self.max_health
        self.player2_health = self.max_health

        FightingGame.set_game_active(channel_id, True)
        fight_image_path = await self.generate_fight_image()
        user_config = await self.bullshido_cog.config.all_users()
        print(f"user_config: {user_config}")  # Debug log
        print(f"player1 ID: {self.player1.id}, player2 ID: {self.player2.id}")  # Debug log
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
            await self.play_round(round_number)

        if FightingGame.is_game_active(channel_id):
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
                    await self.update_health_bars(round_number, final_message, "Draw", final_result="The Fight Ended in A Draw!")
                    FightingGame.set_game_active(channel_id, False)
                    return

            result_description = FIGHT_RESULT_LONG[result_type]
            final_message = (
                f"The fight is over!\n"
                f"After 3 rounds, we go to the judges' scorecard for a decision.\n"
                f"The judges scored the fight {self.player1_score if winner == self.player1 else self.player2_score} - {self.player1_score if winner == self.player2 else self.player2_score} for the winner, by {result_description}, {winner.display_name}!"
            )
            await self.update_health_bars(round_number, final_message, "Decision Victory", final_result=f"Decision Victory for {winner.display_name}!")
            await self.record_result(winner, loser, result_type)

        FightingGame.set_game_active(channel_id, False)
