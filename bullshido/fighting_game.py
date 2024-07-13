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
        font_path ='/home/slurms/ScrapGPT/scrapgpt_data/cogs/CogManager/cogs/bullshido/osaka.ttf'
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
        text_color = (249,4,43)

        draw_text_with_shadow(draw, player1_name_text_position, player1_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_name_text_position, player2_name, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player1_text_position, player1_details, font, shadow_color, text_color)
        draw_text_with_shadow(draw, player2_text_position, player2_details, font, shadow_color, text_color)

        intro_message = (
            "Introducing the fighters!\n"
        )
        intro_subtitle = ("")

        intro_text_position = (80, 10)
        intro_subtitle_position = (20,40)
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
    
    async def update_health_bars(self, round_number, latest_message, round_result, fight_over=False):
        player1_health_bar = self.create_health_bar(self.player1_health, self.max_health)
        player2_health_bar = self.create_health_bar(self.player2_health, self.max_health)
        player1_stamina_status = self.get_stamina_status(self.player1_stamina)
        player2_stamina_status = self.get_stamina_status(self.player2_stamina)

        title = round_result if fight_over else f"Round {round_number} - {self.player1.display_name} vs {self.player2.display_name}"
        embed = discord.Embed(
            title=title,
            color=0xFF0000
        )
        embed.add_field(name=f"{self.player1.display_name}'s Health", value=f"{player1_health_bar} {self.player1_health}", inline=False)
        embed.add_field(name=f"{self.player1.display_name}'s Stamina", value=player1_stamina_status, inline=False)
        if self.player1_critical_injuries:
            embed.add_field(name=f"{self.player1.display_name} Injuries", value=", ".join(self.player1_critical_injuries), inline=False)
        if self.player1_data.get("permanent_injuries"):
            embed.add_field(name=f"{self.player1.display_name} Permanent Injuries", value=", ".join([f"{bp}: {', '.join(injs)}" for bp, injs in self.player1_data["permanent_injuries"].items()]), inline=False)
        
        embed.add_field(name=f"{self.player2.display_name}'s Health", value=f"{player2_health_bar} {self.player2_health}", inline=False)
        embed.add_field(name=f"{self.player2.display_name}'s Stamina", value=player2_stamina_status, inline=False)
        if self.player2_critical_injuries:
            embed.add_field(name=f"{self.player2.display_name} Injuries", value=", ".join(self.player2_critical_injuries), inline=False)
        if self.player2_data.get("permanent_injuries"):
            embed.add_field(name=f"{self.player2.display_name} Permanent Injuries", value=", ".join([f"{bp}: {', '.join(injs)}" for bp, injs in self.player2_data["permanent_injuries"].items()]), inline=False)
        
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
        bodypart = ""

        try:
            strike, damage_range = random.choice(list(STRIKES[style].items()))
            base_damage = random.randint(*damage_range)
            modified_damage = self.calculate_adjusted_damage(base_damage, attacker['training_level'], attacker['nutrition_level'])
            modifier = random.uniform(0.8, 1.3)

            bodypart = random.choice(BODY_PARTS)

            # Check for critical hit
            is_critical_hit = random.random() < self.CRITICAL_CHANCE
            if is_critical_hit:
                modified_damage = base_damage * 2
                conclude_message, critical_injury = random.choice(list(CRITICAL_RESULTS.items()))
                conclude_message = conclude_message.format(defender=defender.display_name)
                message = random.choice(CRITICAL_MESSAGES)

                if random.random() < self.PERMANENT_INJURY_CHANCE:
                    critical_injury = f"Permanent Injury: {critical_injury}"
            else:
                modified_damage = round(modified_damage * modifier)

            # Check for existing permanent injuries to apply additional damage
            if defender.get("permanent_injuries") and bodypart in defender["permanent_injuries"]:
                modified_damage *= 2

            return strike, modified_damage, message, conclude_message, critical_injury, bodypart
        except Exception as e:
            print(f"Error during get_strike_damage: {e}")
            print(f"Attacker: {attacker}, Defender: {defender}, Style: {style}")
            return strike, modified_damage, message, conclude_message, critical_injury, bodypart

    async def target_bodypart(self):
        bodypart = random.choice(BODY_PARTS)
        return bodypart

    def is_grapple_move(self, strike):
        return any(keyword.lower() in strike.lower() for keyword in GRAPPLE_KEYWORDS)
    
    def calculate_miss_probability(self, attacker_stamina, attacker_training, defender_training, defender_stamina):
        training_ratio = attacker_training / (defender_training + 1)
        stamina_ratio = attacker_stamina / (defender_stamina + 1)
        miss_probability = self.BASE_MISS_PROBABILITY / (training_ratio * stamina_ratio)
        return min(max(miss_probability, 0.05), 0.5)  # Ensure it's between 5% and 50%
    
    def calculate_stamina_cost(self, move):
        if move in STRIKE_ACTIONS:
            return self.BASE_STAMINA_COST
        elif move in GRAPPLE_ACTIONS:
            return self.BASE_STAMINA_COST * 2
        return self.BASE_STAMINA_COST
    
    async def execute_turn(self, attacker, defender, attacker_data, defender_data):
        move_type = await self.get_strike(attacker)
        move_name, base_damage = move_type
        
        # Calculate miss probability
        miss_probability = self.calculate_miss_probability(attacker_data['stamina_level'], attacker_data['training_level'], defender_data['training_level'], defender_data['stamina_level'])
        
        if random.random() < miss_probability:
            await self.channel.send(f"{attacker.display_name} attempted a {move_name} but missed!")
            return False, f"{attacker.display_name} missed with a {move_name}!", 0, None, "", None
        
        damage, bodypart = self.calculate_damage(attacker_data, defender_data, base_damage)
        defender_data['health'] -= damage
        critical_message = ""
        
        if damage > base_damage * 1.5:
            critical_message = random.choice(CRITICAL_MESSAGES).format(defender=defender.display_name)
            defender_data['injuries'].append(bodypart)

        await self.update_health_bars(self.rounds, f"{attacker.display_name} used {move_name} on {defender.display_name} for {damage} damage!", critical_message)
        return True, f"{attacker.display_name} hit {defender.display_name} with a {move_name} for {damage} damage!", damage, bodypart, critical_message, attacker.display_name

    async def get_strike(self, player):
        style = player.style
        strike = random.choice(list(STRIKES[style].items()))
        return strike

    def calculate_damage(self, attacker_data, defender_data, base_damage):
        adjusted_damage = self.calculate_adjusted_damage(base_damage, attacker_data['training_level'], attacker_data['nutrition_level'])
        modifier = random.uniform(0.8, 1.3)
        final_damage = round(adjusted_damage * modifier)
        
        bodypart = random.choice(BODY_PARTS)
        if bodypart in defender_data['injuries']:
            final_damage *= 2
        
        return final_damage, bodypart

    async def start_game(self):
        try:
            if FightingGame.is_game_active(self.channel.id):
                await self.channel.send("A game is already active in this channel.")
                return

            FightingGame.set_game_active(self.channel.id, True)
            fight_image_path = await self.generate_fight_image()
            await self.channel.send(file=discord.File(fight_image_path))

            for current_round in range(1, self.rounds + 1):
                await asyncio.sleep(2)  # Simulate a delay between rounds
                for _ in range(self.max_strikes_per_round):
                    attacker, defender = (self.player1, self.player2) if self.current_turn == self.player1 else (self.player2, self.player1)
                    attacker_data, defender_data = (self.player1_data, self.player2_data) if attacker == self.player1 else (self.player2_data, self.player1_data)

                    turn_successful, latest_message, damage, bodypart, critical_message, last_attacker = await self.execute_turn(attacker, defender, attacker_data, defender_data)
                    
                    if not turn_successful:
                        continue

                    if defender_data['health'] <= 0:
                        await self.update_health_bars(current_round, latest_message, critical_message, fight_over=True)
                        await self.channel.send(f"{attacker.display_name} wins by KO!")
                        await self.bullshido_cog.update_player_stats(attacker, True, "KO", defender.display_name)
                        await self.bullshido_cog.update_player_stats(defender, False, "KO", attacker.display_name)
                        FightingGame.set_game_active(self.channel.id, False)
                        return

                    if damage and bodypart:
                        if critical_message:
                            await self.channel.send(critical_message)
                            self.current_turn = defender

                round_result = f"Round {current_round} is over."
                await self.update_health_bars(current_round, latest_message, round_result)
                self.current_turn = self.player1 if self.current_turn == self.player2 else self.player2

            winner = self.player1 if self.player1_score > self.player2_score else self.player2
            loser = self.player1 if winner == self.player2 else self.player2

            await self.channel.send(f"The fight is over! The winner is {winner.display_name}!")
            await self.bullshido_cog.update_player_stats(winner, True, "UD", loser.display_name)
            await self.bullshido_cog.update_player_stats(loser, False, "UD", winner.display_name)
            FightingGame.set_game_active(self.channel.id, False)

        except Exception as e:
            print(f"Error during fight: {e}")
            await self.channel.send(f"Failed to start the fight due to an error: {e}")
            FightingGame.set_game_active(self.channel.id, False)
