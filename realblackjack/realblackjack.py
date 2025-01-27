from redbot.core import commands, Config, bank
import random
import asyncio
import discord
import logging

class Deck:
    def __init__(self, num_decks=2):
        self.cards = []
        self.num_decks = num_decks
        self.suits = [":clubs:", ":diamonds:", ":hearts:", ":spades:"]
        self.ranks = {
            "ace": 11,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "jack": 10,
            "queen": 10,
            "king": 10,
        }
        self.refill()

    def shuffle(self):
        random.shuffle(self.cards)
        print("Shuffled all decks...")

    def deal_card(self):
        if len(self.cards) == 0:
            print("No cards left in the deck. Refilling deck...")
            self.refill()
        return self.cards.pop()

    def refill(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in self.suits:
                for rank, value in self.ranks.items():
                    self.cards.append(Card(suit, rank, value))
        self.shuffle()

    def num_cards_remaining(self):
        return len(self.cards)


class Card:
    def __init__(self, suit, rank, value):
        self.suit = suit
        self.rank = rank
        self.value = value

    def __str__(self):
        # Unicode card representation
        suits_unicode = {
            ":clubs:": "♣️",
            ":diamonds:": "♦️",
            ":hearts:": "♥️",
            ":spades:": "♠️"
        }
        rank_display = {
            "ace": "A",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "10": "10",
            "jack": "J",
            "queen": "Q",
            "king": "K"
        }
        suit = suits_unicode[self.suit]
        rank = rank_display[self.rank]
        return f"{rank}{suit}"

    def __repr__(self):
        return f"{self.rank} of {self.suit} ({self.value})"


class Participant:
    def __init__(self):
        self.hand = []
        self.score = 0
        self.bust = False
        self.blackjack = False
        self.stands = False

    def draw_card(self, deck):
        card = deck.deal_card()
        self.hand.append(card)
        return card

    def calculate_score(self):
        for card in self.hand:
            print(f"Card in hand: {card}, Type: {type(card)}")
        self.score = sum(card.value for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == "ace")

        while self.score > 21 and aces:
            self.score -= 10
            aces -= 1

        if self.score > 21:
            self.bust = True
        elif self.score == 21:
            self.blackjack = True

    async def clear_hand(self):
        self.hand = []
        self.score = 0
        self.bust = False
        self.blackjack = False
        self.stands = False


class Player(Participant):
    def __init__(self, name, ctx):
        super().__init__()
        self.name = name  
        self.ctx = ctx
        self.bet = 0
        self.hands = [self.hand]  # Initialize hands with the main hand
        
    def can_split(self):
        """Check if the player can split their hand."""
        return (len(self.hands[0]) == 2 and 
                self.hands[0][0].rank == self.hands[0][1].rank)

    def split(self, deck):
        """Split the initial hand into two separate hands."""
        if not self.can_split():
            return False

        # Create a second hand with one card from the original hand
        second_hand = [self.hands[0].pop()]
        self.hands.append(second_hand)

        # Draw a new card for each hand
        self.hands[0].append(deck.deal_card())
        self.hands[1].append(deck.deal_card())

        return True

    async def async_init(self, ctx):
        self.balance = await bank.get_balance(ctx.author)
        print(f"Initialized player {self.name} with balance {self.balance}")

    def __str__(self):
        """Return a string representing the player's hand."""
        return f"{self.name}'s hand: " + ", ".join(str(card) for card in self.hand)

    def __repr__(self):
        """Return an 'official' representation of the player's hand."""
        hand_repr = ", ".join(repr(card) for card in self.hand)
        return f"Player('{self.name}', hand=[{hand_repr}])"

    def place_bet(self, amount, available_balance):
        if amount > available_balance:
            return False  
        self.bet = amount
        return True

    async def clear_hand(self):
        await super().clear_hand()  # Call parent's clear_hand first
        self.hands = [self.hand]    # Reset hands list to contain only the cleared main hand
        self.bet = 0                # Reset bet amount


class Dealer(Participant):
    def __init__(self):
        super().__init__()
        self.name = "Dealer"
        self.show_one_card = True
        self.stand_on_score = 17
        self.stand_on_soft_17 = True

    def reveal_cards(self):
        self.show_one_card = False

    def should_hit(self):
        """Determines if the dealer should hit."""
        if self.score < self.stand_on_score:
            return True
        if self.stand_on_soft_17 and self.score == 17:
            return any(card.rank == "ace" for card in self.hand)
        return False


class GameState:
    payouts = {"Win": 2, "Blackjack": 2.5}
    buy_in_amount = 100

    def __init__(self, bot, channel_id, games, config):
        self.bot = bot
        self.config = config # reference to our RealBlackJack config 
        self.channel_id = channel_id
        self.games = games
        self.deck = Deck(num_decks=2)
        self.player_objects = {}  # Active game players
        self.dealer = Dealer()
        self.end_game = False
        self.state = "Stopped"
        self.join_queue = [] # Players waiting to join the game
        self.leave_queue = [] # Players waiting to leave the game


    def has_active_players(self):
        """Check if there are any active players at the table."""
        return bool(self.player_objects)

    async def clear_states(self, ctx, channel_id):
        """Reset all game states for the next round"""
        for player in self.player_objects.values():
            await player.clear_hand()
        await self.dealer.clear_hand()
        self.end_game = False
        self.state = "Waiting for bets"
        
    async def process_queues(self, ctx):
        """Process join and leave queues at the start of each round."""
        # Handle players leaving
        # await ctx.send("DEBUG: Processing leave queue...") #! Debug print
        for player_id in self.leave_queue:
            if player_id in self.player_objects:
                del self.player_objects[player_id]
                member = ctx.guild.get_member(player_id)
                if member:
                    await ctx.send(f"{member.mention} has left the game.")

        # Clear the leave queue
        # await ctx.send("DEBUG: Clearing leave queue...") #! Debug print
        self.leave_queue.clear()

        # Handle players joining
        # await ctx.send("DEBUG: Processing join queue...") #! Debug print
        for player_id in self.join_queue:
            if player_id not in self.player_objects:
                member = ctx.guild.get_member(player_id)
                if member:
                    # await ctx.send(f"DEBUG: Initializing {member.mention} in the game.") #! Debug print
                    player = Player(member.display_name, ctx)
                    await player.async_init(ctx)
                    self.player_objects[player_id] = player
                    await ctx.send(f"{member.mention} has joined the game.")

        # Clear the join queue
        self.join_queue.clear()

    async def take_bets(self, ctx, channel_id):
        self.state = "Taking bets"
        for player_id, player in self.player_objects.items():
            member = ctx.guild.get_member(player_id)
            if member:
                player_balance = await bank.get_balance(member)
                await ctx.send(
                    f"{member.mention}, you have {player_balance} chips. How much do you want to bet? Enter '0' to skip."
                )

                def check_bet(msg):
                    return msg.author.id == player_id and msg.channel == ctx.channel

                while True:  # Ensure a single bet loop per player
                    try:
                        msg = await self.bot.wait_for("message", timeout=20.0, check=check_bet)
                        if msg.content.isdigit():  # Only delete if it's a number (bet amount)
                            try:
                                await msg.delete()
                            except discord.HTTPException:
                                pass
                            
                            bet = int(msg.content)
                            if 0 < bet <= player_balance:
                                player.bet = bet
                                await bank.withdraw_credits(member, bet)
                                await ctx.send(
                                    f"{member.mention}, your bet of {bet} chips has been placed."
                                )
                                break  # Exit loop after valid input
                            elif bet == 0:
                                await ctx.send(f"{member.mention}, you chose not to place a bet.")
                                break  # Exit loop if the player skips
                            else:
                                await ctx.send(
                                    f"{member.mention}, your bet must be more than 0 and no more than your balance."
                                )
                        else:
                            continue  # Don't delete non-bet messages
                    except asyncio.TimeoutError:
                        await ctx.send(
                            f"{member.mention}, you took too long to bet. Skipping your turn."
                        )
                        break  # Exit loop on timeout

    async def add_player(self, player_id, ctx):
        player = Player(self.bot.get_user(player_id).name, ctx)
        await player.async_init(ctx)
        self.player_objects[player_id] = player

    # The initial gameplay logic 
    async def setup_game(self, ctx, channel_id, embed):
        self.state = "Dealing cards"
        game = self.games.get(channel_id)
        if game is None:
            await ctx.send(f"No game found for channel ID: {channel_id}")
            return
        if game.state == "End Game":
            print("Game is ending, skipping setup...")
            game.state = "Stopped"
            return
        
        # Check if the shoe is empty and refill if necessary
        if game.deck.num_cards_remaining() == 0:
            await ctx.send("The shoe is empty! The Dealer reshuffles the decks and refills the shoe...")
            game.deck.refill()
            await asyncio.sleep(2)
        
        # Shuffle the deck
        game.deck.shuffle()  

        # Deal cards to players and the dealer
        for player_id, player in game.player_objects.items():
            user = self.bot.get_user(player_id)
            if user is None:
                continue  
            player.draw_card(game.deck)
            player.draw_card(game.deck)
            player.calculate_score()

        dealer = game.dealer
        dealer.draw_card(game.deck)
        dealer.draw_card(game.deck)
        dealer.score = dealer.hand[0].value

        game.state = "In Progress"
        await self.card_table_update_embed(embed, game, reveal_dealer=False)
        self.game_message = await ctx.send(embed=embed)

    async def reset_player_and_dealer_states(self):
        print(f"Clearing states for channel ID: {self.channel_id}")
        await self.dealer.clear_hand()  
        for player in self.player_objects.values():
            await player.clear_hand()

    async def player_turns(self, ctx, channel_id, embed):
        game = self.games[channel_id]
        game.state = "Player Turns"
        
        for player_id, player in game.player_objects.items():
            user = self.bot.get_user(player_id)
            
            hand_index = 0
            while hand_index < len(player.hands):
                current_hand = player.hands[hand_index]
                player.current_hand_index = hand_index
                
                # Calculate score for current hand
                player.score = sum(card.value for card in current_hand)
                aces = sum(1 for card in current_hand if card.rank == "ace")
                while player.score > 21 and aces:
                    player.score -= 10
                    aces -= 1

                # If player has 21, automatically end their turn
                if player.score == 21:
                    await self.card_table_update_embed(
                        embed, game, reveal_dealer=False,
                        status_message=f"🎯 {user.mention} has 21! Moving to next hand."
                    )
                    await self.game_message.edit(embed=embed)
                    hand_index += 1
                    continue

                hand_num = f" (Hand {hand_index + 1})" if len(player.hands) > 1 else ""
                status = (f"🎮 {user.mention}'s turn" + 
                         (f" (Hand {hand_index + 1})" if len(player.hands) > 1 else "") +
                         "\nOptions: " +
                         ("split, " if player.can_split() and hand_index == 0 else "") +
                         "hit, stand/stay, or double down/double")
                
                await self.card_table_update_embed(embed, game, reveal_dealer=False, status_message=status)
                await self.game_message.edit(embed=embed)

                hand_completed = False
                while not hand_completed:
                    def check(m):
                        valid_actions = ["hit", "stand", "stay", "double"]
                        if player.can_split() and hand_index == 0:
                            valid_actions.append("split")
                        # Only return True for valid game actions
                        return (
                            m.author.id == player_id
                            and m.channel.id == ctx.channel.id
                            and m.content.lower() in valid_actions
                        )

                    try:
                        msg = await self.bot.wait_for("message", timeout=15.0, check=check)
                        # Only delete valid game action messages
                        try:
                            await msg.delete()
                        except discord.HTTPException:
                            pass
                            
                        decision = msg.content.lower()

                        if decision == "split" and hand_index == 0:
                            # Handle splitting
                            member = ctx.guild.get_member(player_id)
                            player_balance = await bank.get_balance(member)
                            
                            if player.bet * 2 > player_balance:
                                await ctx.send(f"{user.mention}, you don't have enough chips to split.")
                                continue
                            
                            # Withdraw additional bet for the second hand
                            await bank.withdraw_credits(member, player.bet)
                            
                            # Perform the split
                            player.split(game.deck)
                            await ctx.send(f"{user.mention} splits their hand! Play out each hand separately.")
                            
                            # Update embed to reflect split hands
                            await self.card_table_update_embed(embed, game, reveal_dealer=False)
                            await self.game_message.edit(embed=embed)
                            # Don't break - let player continue with first hand
                            continue

                        elif decision == "hit":
                            # Handle empty shoe before dealing
                            if game.deck.num_cards_remaining() == 0:
                                await ctx.send("The shoe is empty! The Dealer reshuffles the decks and refills the shoe...")
                                game.deck.refill()
                                await asyncio.sleep(2)

                            # Draw card to the current hand
                            current_hand.append(game.deck.deal_card())
                            
                            # Recalculate score for the current hand
                            player.score = sum(card.value for card in current_hand)
                            aces = sum(1 for card in current_hand if card.rank == "ace")
                            while player.score > 21 and aces:
                                player.score -= 10
                                aces -= 1

                            # Update the embed with the new card and score
                            await self.card_table_update_embed(embed, game, reveal_dealer=False)
                            await self.game_message.edit(embed=embed)

                            if player.score > 21:  # Player busts
                                await ctx.send(f"{user.mention} has busted with a score of {player.score}!")
                                hand_completed = True

                        elif decision == "stand" or decision == "stay":
                            await ctx.send(f"{user.mention} stands on {player.score}.")
                            hand_completed = True

                        elif decision == "double":
                            # Handle empty shoe before dealing
                            if game.deck.num_cards_remaining() == 0:
                                await ctx.send("The shoe is empty! The Dealer reshuffles the decks and refills the shoe...")
                                game.deck.refill()
                                await asyncio.sleep(2)

                            # Check if player has enough balance to double their bet
                            member = ctx.guild.get_member(player_id)
                            player_balance = await bank.get_balance(member)
                            if player.bet * 2 > player_balance:
                                await ctx.send(f"{user.mention}, you don't have enough chips to double down.")
                                continue

                            # Double the bet and withdraw chips
                            await bank.withdraw_credits(member, player.bet)
                            player.bet *= 2

                            # Draw one card and add to current hand
                            current_hand.append(game.deck.deal_card())
                            
                            # Recalculate score for current hand
                            player.score = sum(card.value for card in current_hand)
                            aces = sum(1 for card in current_hand if card.rank == "ace")
                            while player.score > 21 and aces:
                                player.score -= 10
                                aces -= 1

                            # Update the embed with the new card and score
                            await self.card_table_update_embed(embed, game, reveal_dealer=False)
                            await self.game_message.edit(embed=embed)

                            # Inform the player of their final score
                            if player.score > 21:
                                await ctx.send(f"After doubling down, {user.mention} busted with {player.score}!")
                            else:
                                await ctx.send(f"{user.mention} doubled down, final score is {player.score}.")
                            hand_completed = True
                            
                    except asyncio.TimeoutError:
                        await ctx.send(f"{user.mention}, you took too long to make a decision. Standing on current hand.")
                        hand_completed = True

                # Move to next hand
                hand_index += 1

    async def card_table_update_embed(self, embed, game, reveal_dealer=True, status_message=""):
        embed.clear_fields()
        
        # Add game status/message field at the top
        if status_message:
            embed.add_field(
                name="Game Status",
                value=status_message,
                inline=False
            )

        # Add current phase
        embed.add_field(
            name="Current Phase",
            value=f"**{game.state}**",
            inline=False
        )

        # Add player hands and bets
        for player_id, player in game.player_objects.items():
            user = self.bot.get_user(player_id)
            
            for hand_index, hand in enumerate(player.hands):
                hand_str = ", ".join(str(card) for card in hand)
                score = sum(card.value for card in hand)
                
                # Adjust for aces
                aces = sum(1 for card in hand if card.rank == "ace")
                while score > 21 and aces:
                    score -= 10
                    aces -= 1
                
                score_str = f"Score: {score}" if score <= 21 else "Busted!"
                hand_name = f"{user.display_name}'s Hand {hand_index + 1}"
                bet_str = f"Bet: {player.bet}"
                
                embed.add_field(
                    name=hand_name,
                    value=f"{hand_str}\n{score_str}\n{bet_str}",
                    inline=False,
                )

        # Add dealer's hand
        if reveal_dealer:
            dealer_hand_str = ", ".join(str(card) for card in game.dealer.hand)
            dealer_score_str = f"Score: {game.dealer.score}" if game.dealer.score <= 21 else "Busted!"
            embed.add_field(
                name="Dealer's Hand",
                value=f"{dealer_hand_str}\n{dealer_score_str}",
                inline=False,
            )
        else:
            face_up_card = game.dealer.hand[0]
            embed.add_field(
                name="Dealer's Hand",
                value=f"{face_up_card} and a hidden card",
                inline=False,
            )

        # Add game info footer
        embed.add_field(
            name="Game Info",
            value=f"Cards in Shoe: {game.deck.num_cards_remaining()}\nActive Players: {len(game.player_objects)}",
            inline=False
        )

        embed.set_thumbnail(url="https://i.ibb.co/7vJ2Y2V/realblackjack-logo-transparent.png")
    
    async def dealer_turn(self, ctx, channel_id, embed):
        """Handle the dealer's turn."""
        self.state = "Dealer turn"
        game = self.games[channel_id]
        dealer = game.dealer
        dealer.calculate_score()

        # Initial embed update for the dealer's starting hand
        await self.card_table_update_embed(embed, game, reveal_dealer=True)
        dealer_message = await ctx.send(embed=embed)

        # Dealer rules: must hit until score is 17 or higher or reaches 21
        while dealer.score < 17:
            await asyncio.sleep(2)
            if game.deck.num_cards_remaining() == 0:
                            await ctx.send("The shoe is empty! The Dealer reshuffles the decks and refills the shoe...")
                            await asyncio.sleep(2)
            dealer.draw_card(game.deck)  # Dealer draws a card
            dealer.calculate_score()  # Recalculate the dealer's score
            
            await self.card_table_update_embed(embed, game, reveal_dealer=True)
            await dealer_message.edit(embed=embed)

            # Check for exact 21
            if dealer.score == 21:
                embed.add_field(
                    name="Blackjack!",
                    value=f"Dealer hit 21!.",
                    inline=False,
                )
                await self.card_table_update_embed(embed, game, reveal_dealer=True)
                await dealer_message.edit(embed=embed)
                return  # End the dealer's turn immediately

            # Check if dealer is busted
            if dealer.score > 21:
                embed.add_field(
                    name="Dealer Busts!",
                    value=f"The dealer has busted with a score of {dealer.score}.",
                    inline=False,
                )
                await self.card_table_update_embed(embed, game, reveal_dealer=True)
                await dealer_message.edit(embed=embed)
                return  # End the dealer's turn immediately

        # Final embed update if the dealer didn't bust or hit 21
        await self.card_table_update_embed(embed, game, reveal_dealer=True)
        await dealer_message.edit(embed=embed)
        
    async def payout(self, ctx, channel_id):
        game = self.games[channel_id]
        dealer = game.dealer

        for player_id, player in game.player_objects.items():
            member = ctx.guild.get_member(player_id)
            
            if not member: 
                continue

            # Process each hand separately
            for hand_index, hand in enumerate(player.hands):
                hand_score = sum(card.value for card in hand)
                
                # Adjust for aces
                aces = sum(1 for card in hand if card.rank == "ace")
                while hand_score > 21 and aces:
                    hand_score -= 10
                    aces -= 1

                # Existing payout logic, but applied to each hand
                if hand_score > 21:
                    # Hand is busted
                    await ctx.send(
                        f"{member.mention}, hand {hand_index + 1} is busted with {hand_score}. You lose your bet of {player.bet}."
                    )
                    await bank.withdraw_credits(member, player.bet)

                elif dealer.score > 21 or hand_score > dealer.score:
                    # Hand wins
                    win_amount = player.bet * self.payouts["Win"]
                    await ctx.send(f"{member.mention}, hand {hand_index + 1} wins with {hand_score}! You get {win_amount} chips.")
                    await bank.deposit_credits(member, win_amount)

                elif hand_score == dealer.score:
                    # Hand is a tie
                    await ctx.send(f"{member.mention}, hand {hand_index + 1} is a tie with {hand_score}. You get {player.bet} chips back.")

                else:
                    # Hand loses
                    await ctx.send(
                        f"{member.mention}, hand {hand_index + 1} loses to the dealer with {hand_score}. You lost {player.bet} chips."
                    )
                    await bank.withdraw_credits(member, player.bet)

                # Clear player's hand and states for the next round
                await player.clear_hand()

    async def build_game_state_embed(self, game):
        # Start creating the embed
        embed = discord.Embed(title="RealBlackjack", color=0X9A081B, description="Game Table")
        embed.set_author(name="Blackjack Dealer", icon_url="")

        # Update the embed with the current hands and scores
        await self.update_embed_with_hands(embed, game)

        
        embed.add_field(
            name="Cards Left in Shoe", value=str(len(game.deck.cards)), inline=False
        )

    
        return embed

    async def check_and_end_game(self, ctx, channel_id):
        """Check if there are active players; if none, end the game."""
        if not self.has_active_players():
            await ctx.send("No players remaining at the table. Ending the game.")
            self.state = "Stopped"
            del self.games[channel_id]

class RealBlackJack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.config = Config.get_conf(self, identifier=123452212232144515623667890)
        default_member = {
            "games_won": 0,
            "games_lost": 0,
            "total_chips_won": 0,
            "total_chips_lost": 0,
        }
        self.config.register_member(**default_member)
        self.join_state_timeout = 20
        self.bet_state_timeout = 15
        self.min_bet = 10
        self.max_bet = 10000
        self.payouts = {"Win": 2, "Blackjack": 2.5}
        self.blinds = {"bigblind": 200, "smallblind": 100}
        self.max_players = 6
        
        # Set up logging
        #self.logger = logging.getLogger('realblackjack')
        #self.logger.setLevel(logging.DEBUG)
        #handler = logging.FileHandler(filename='realblackjack.log', encoding='utf-8', mode='w')
        #handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        #self.logger.addHandler(handler)
        

    async def update_wins(self, member):
        current_wins = await self.config.member(member).wins()
        await self.config.member(member).wins.set(current_wins + 1)
        self.logger.debug(f"Updated wins for {member.display_name}")

    async def update_losses(self, member):
        current_losses = await self.config.member(member).losses()
        await self.config.member(member).losses.set(current_losses + 1)
        # self.logger.debug(f"Updated losses for {member.display_name}")

    @commands.group()
    async def realblackjack(self, ctx):
        """Commands Group for Real Blackjack."""
        if ctx.guild is None: 
            await ctx.send("This command can only be used in a server.")
            return
        if ctx.invoked_subcommand is None:
            # Instead of showing error message, invoke help command
            pass
            
    @realblackjack.command()
    async def start(self, ctx):
        """ Start a game of Real Blackjack."""
        # self.logger.info(f"Starting a game in channel {ctx.channel.id}")
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send("A game is already started in this channel.")
            return

        await ctx.send(
            f"Game will start in {self.join_state_timeout} seconds. Type join to sit at the table!"
        )
        # Initialize joined players
        joined_players = []

        def check_join(msg):
            return (
                msg.content.lower() == "bj join" or msg.content.lower() == "join" and msg.channel == ctx.channel
            )

        while True:
            try:
                msg = await self.bot.wait_for(
                    "message", timeout=self.join_state_timeout, check=check_join
                )
                player_id = msg.author.id
                if player_id not in joined_players:
                    joined_players.append(player_id)
                    await ctx.send(f"{msg.author.mention} has joined the game!")
            except asyncio.TimeoutError:
                break

        if not joined_players:
            await ctx.send("No one joined. Game cancelled.")
            return

        # Create a dictionary of player objects
        player_dict = {
            player_id: Player(self.bot.get_user(player_id).name, ctx)
            for player_id in joined_players
        }

        # Initialize GameState with the players who have joined
        self.games[channel_id] = GameState(self.bot, channel_id, self.games, self.config)
        game = self.games[channel_id]
        game.player_objects = player_dict  # Set players directly
        embed = discord.Embed(title="Slurms' Real Blackjack", color=0X9A081B)

        for player in player_dict.values():
            await player.async_init(ctx)

        await ctx.send(f"Game starting with {len(joined_players)} players!")
        await self.play_game(ctx, channel_id, embed)


    @realblackjack.command()
    async def join(self, ctx):
        """Adds the player to the join queue. They will join the table at the start of the next round."""
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            await ctx.send("No game is currently running in this channel.")
            return

        game = self.games[channel_id]
        player_id = ctx.author.id

        # Prevent duplicate joins
        if player_id in game.player_objects or player_id in game.join_queue:
            await ctx.send("You are already in the game or waiting to join.")
            return

        # Add to the join queue
        game.join_queue.append(player_id)
        await ctx.send(f"{ctx.author.mention} will join the table at the start of the next round.")


    @realblackjack.command()
    async def leave(self, ctx):
        """Allow players to leave the table."""
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            await ctx.send("There's no active game right now.")
            return

        game = self.games[channel_id]
        player_id = ctx.author.id

        # Prevent duplicate leave requests
        if player_id not in game.player_objects or player_id in game.leave_queue:
            await ctx.send("You are not in the game or have already requested to leave the table.")
            return

        # Add to the leave queue
        game.leave_queue.append(player_id)
        await ctx.send(f"{ctx.author.mention} is calling it a day and will leave the table next round.")

    @commands.group()
    @commands.is_owner()
    async def realblackjackset(self, ctx):
        """Admin Commands Group for Real Blackjack."""
        if ctx.guild is None: 
            await ctx.send("This command can only be used in a server.")
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid blackjack command passed...")
            
    @realblackjackset.command()
    async def gamestate(self, ctx):
        """Show the current game state."""
        channel_id = ctx.channel.id
        if channel_id in self.games:
            game = self.games[channel_id]
            await ctx.send(f"Game state: {game.state}")
            
    @realblackjackset.command(name="endgame")
    @commands.is_owner()
    async def end(self, ctx):
        """End the game manually."""
        channel_id = ctx.channel.id
        if channel_id in self.games:
            del self.games[channel_id]
            await ctx.send("The game has ended.")
        else:
            await ctx.send("No game is currently running in this channel.")

    @realblackjackset.command(name="timeout")
    async def join_timeout(self, ctx, timeout: int):
        """Set the timeout for players to join the game."""
        if timeout < 10:
            await ctx.send("Timeout must be at least 10 seconds.")
            return
        if timeout > 30:
            await ctx.send("Timeout cannot be more than 30 seconds.")
            return
        self.join_state_timeout = timeout
        await ctx.send(f"Join timeout set to {timeout} seconds.")

    @realblackjackset.command()
    async def decks(self, ctx, number_of_decks: int):
        """Set the number of decks to be used in the game. This increases the number of cards in the shoe."""
        channel_id = ctx.channel.id
        game = self.games[channel_id]
        
        if self.games[channel_id].state != ["Waiting for bets"]:
            await ctx.send("A game is currently in progress. Cannot change the number of decks.")
            return

        self.deck = Deck(num_decks=number_of_decks)
        await ctx.send(f"Deck has been set to {number_of_decks} decks.")


    @realblackjackset.command(name="cardsleft")
    async def cards_remaining(self, ctx):
        """Returns how many cards are left in the shoe."""
        channel_id = ctx.channel.id
        game = self.games.get(channel_id)
        if not game:
            await ctx.send("There's no active game in this channel.")
            return
        if ctx.channel.id in game:
            remaining_cards = game.deck.num_cards_remaining()
            await ctx.send(f'There is an active game in this channel with {remaining_cards} cards left in the shoe.')
        else:
            await ctx.send("There's no active game in this channel.")

    @realblackjackset.command(name="settings")
    async def settings(self, ctx):
        """Display settings information and help for Real Blackjack admin commands."""
        embed = discord.Embed(
            title="Real Blackjack Settings",
            color=0X9A081B,
            description="Current game settings and admin commands"
        )
        embed.set_image(url="https://i.ibb.co/vXNSX8g/realblackjack-logo-transparent.png")

        # Add about field
        embed.add_field(
            name="About",
            value="Real Blackjack - A fully featured multiplayer blackjack game for Discord\nCreated by Slurms Mackenzie/ropeadope62",
            inline=False
        )

        # Add repository field
        embed.add_field(
            name="Repo",
            value="https://github.com/ropeadope62/discordcogs",
            inline=False
        )

        # Current settings
        game = self.games.get(ctx.channel.id)
        settings = [
            ("Join Timeout", f"{self.join_state_timeout} seconds"),
            ('Bet Timeout', f"{game.bet_state_timeout if game else 10} seconds"),
            ("Minimum Bet", f"{game.min_bet if game else 10} chips"),
            ("Maximum Bet", f"{game.max_bet if game else 100} chips"),
            ("Payout Multiplier", f"Win: {self.payouts['Win']}x, Blackjack: {self.payouts['Blackjack']}x"),
            ("Blinds", f"bigblind: {self.blinds['bigblind']} / smallblind: {self.blinds['smallblind']}"),
            ("Number of Decks", f"{game.deck.num_decks if game else 2} decks"),
            ("Max Players", f"{self.max_players if game else 6}"),
        ]

        settings_text = "\n".join(f"**{name}:** {value}" for name, value in settings)
        embed.add_field(
            name="Current Settings",
            value=settings_text,
            inline=False
        )

        # Admin commands
        admin_commands = {
            "-realblackjackset timeout <seconds>": "Set the join timeout duration",
            "-realblackjackset bettimeout <seconds>": "Set the bet timeout duration",
            "-realblackjackset minbet <amount>": "Set the minimum bet amount",
            "-realblackjackset maxbet <amount>": "Set the maximum bet amount",
            "-realblackjackset payout <amount>": "Set the payout multiplier for wins",
            "-realblackjackset blinds <bigblind> <smallblind>": "Set the big bling and small blind amount for each round",
            "-realblackjackset decks <number>": "Set the number of decks in the shoe",
            "-realblackjackset endgame": "Force end the current game",
            "-realblackjackset cardsleft": "Check remaining cards in shoe",
            "-realblackjackset gamestate": "Show current game state"
        }

        cmd_text = "\n".join(f"**{cmd}**: {desc}" for cmd, desc in admin_commands.items())
        embed.add_field(
            name="Admin Commands",
            value=cmd_text,
            inline=False
        )

        await ctx.send(embed=embed)

    async def place_bet(self, ctx, player_id, amount):
        user = self.bot.get_user(player_id)
        if user is None:
            return False

        # Retrieve the balance of the user
        balance = await bank.get_balance(user)

        player = self.player_objects.get(player_id)
        if player is None:
            return False

        success = player.place_bet(amount, balance)
        if not success:
            await ctx.send(
                f"You don't have enough chips to place that bet. Your balance is {balance}."
            )
        return success

    async def play_game(self, ctx, channel_id, embed):
        """Main game loop."""
        game = self.games[channel_id]
        game.end_game = False

        while not game.end_game:
            # Create new embed for this round
            round_embed = discord.Embed(
                title="Real Blackjack",
                color=0X9A081B,
                description="🎲 Starting New Round..."
            )
            round_embed.set_thumbnail(url="https://i.ibb.co/7vJ2Y2V/realblackjack-logo-transparent.png")
            round_message = await ctx.send(embed=round_embed)
            
            # Process join and leave queues
            await game.process_queues(ctx)

            if not game.has_active_players():
                await ctx.send("No players remaining. Ending the game.")
                game.end_game = True
                del self.games[channel_id]
                return

            # Take bets and play a round
            round_embed.description = "💰 Taking Bets..."
            await round_message.edit(embed=round_embed)
            await game.take_bets(ctx, channel_id)

            if game.end_game:
                await ctx.send("Game manually stopped. Ending the game.")
                del self.games[channel_id]
                return

            # Setup the game and deal initial cards with new embed
            round_embed.description = "🎴 Dealing Cards..."
            await round_message.edit(embed=round_embed)
            await game.setup_game(ctx, channel_id, round_embed)

            if game.end_game:
                await ctx.send("Game manually stopped. Ending the game.")
                del self.games[channel_id]
                return

            # Handle player turns with the round's embed
            for player_id, player in game.player_objects.items():
                user = self.bot.get_user(player_id)
                round_embed.description = f"🎮 {user.display_name}'s Turn..."
                await round_message.edit(embed=round_embed)
                await game.player_turns(ctx, channel_id, round_embed)

            if game.end_game:
                await ctx.send("Game manually stopped. Ending the game.")
                del self.games[channel_id]
                return

            # Dealer turn and payouts
            if any(player.score <= 21 for player in game.player_objects.values()):
                round_embed.description = "🎰 Dealer's Turn..."
                await round_message.edit(embed=round_embed)
                await game.dealer_turn(ctx, channel_id, round_embed)

            # Payout results
            round_embed.description = "💵 Calculating Payouts..."
            await round_message.edit(embed=round_embed)
            await game.payout(ctx, channel_id)

            # Clear game states for the next round
            await game.clear_states(ctx, channel_id)

            if game.end_game:
                await ctx.send("Game manually stopped. Ending the game.")
                del self.games[channel_id]
                return

            # Brief delay before next round
            await ctx.send(embed=discord.Embed(
                title="Round Ended",
                description="Next round starts in 10 seconds.\nType `-rbj join` to join or `-rbj leave` to leave.",
                color=0X9A081B
            ))
            await asyncio.sleep(10)

        if channel_id in self.games:
            del self.games[channel_id]
        await ctx.send("Game over. Thanks for playing!")

    # ...existing code...

async def setup(bot):
    await bot.add_cog(RealBlackJack(bot))