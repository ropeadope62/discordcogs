from redbot.core import commands, Config, bank
import random
import asyncio
import discord


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
        return f"{self.rank} of {self.suit}"

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
        """
        Determines if the dealer should hit based on the standard Blackjack rules.
        """
        # Calculate score with all Aces as 11 first
        score = sum(card.value for card in self.hand)
        soft_score = score

        # Recalculate score with Aces as 1 if necessary
        aces = sum(1 for card in self.hand if card.rank == "Ace")
        while soft_score > 21 and aces:
            soft_score -= 10
            aces -= 1

        # Check the rules for hitting
        if soft_score < self.stand_on_score:
            return True
        if self.stand_on_soft_17 and soft_score == 17 and aces > 0:
            return True
        return False


class GameState:
    payouts = {"Win": 2, "Blackjack": 2.5}
    buy_in_amount = 100

    def __init__(self, bot, channel_id, games):
        self.bot = bot
        self.channel_id = channel_id
        self.games = games
        self.deck = Deck(num_decks=2)
        self.player_objects = {}  # player_id: Player object
        self.dealer = Dealer()
        self.end_game = False
        self.state = "Stopped"

    async def clear_states(self, ctx, channel_id):
        for player in self.player_objects.values():
            await player.clear_hand()
        await self.dealer.clear_hand()
       
        self.end_game = False
        self.current_bet = 0 
        await ctx.send("The table has been cleared for the next round.")

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

                try:
                    msg = await self.bot.wait_for("message", timeout=20.0, check=check_bet)
                    if msg.content.isdigit(): 
                        bet = int(msg.content)
                        if 0 < bet <= player_balance:
                            player.bet = bet
                            await bank.withdraw_credits(member, bet)  # Deduct the bet amount
                            await ctx.send(
                                f"{member.mention}, your bet of {bet} chips has been placed."
                            )
                        elif bet == 0:
                            await ctx.send(f"{member.mention}, you chose not to place a bet.")
                        else:
                            await ctx.send(
                                f"{member.mention}, your bet must be more than 0 and no more than your balance."
                            )
                    else:
                        await ctx.send(f"{member.mention}, please enter a valid bet amount.")
                except asyncio.TimeoutError:
                    await ctx.send(
                        f"{member.mention}, you took too long to bet. Skipping your turn."
                    )
            else:
                await ctx.send("Player not found in this guild.")

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
        dealer.calculate_score()

        game.state = "In Progress"
        await self.card_table_update_embed(embed, game)
        self.game_message = await ctx.send(embed=embed)

    def set_players(self, player_dict):
        print(f"Setting players for channel ID: {self.channel_id}")
        self.players = player_dict
        self.player_objects = player_dict

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

            # Announce the player's turn
            await ctx.send(f"{user.mention}, it's your turn.")

            # Loop to allow multiple hit and stand
            while True:  

                def check(m):
                    return (
                        m.author.id == player_id
                        and m.channel.id == ctx.channel.id
                        and m.content.lower() in ["hit", "stand"]
                    )

                try:
                    msg = await self.bot.wait_for("message", timeout=15.0, check=check)
                    decision = msg.content.lower()

                    if decision == "hit":
                        player.draw_card(game.deck)
                        player.calculate_score()

                        # Update the embed with the new card and score
                        await self.card_table_update_embed(embed, game)
                        await self.game_message.edit(embed=embed)
                        if player.score > 21:
                            break

                    elif decision == "stand":
                        player.calculate_score()
                        await self.card_table_update_embed(embed, game)
                        break 

                except asyncio.TimeoutError:
                    break  

                # Check for blackjack
                if player.score == 21:
                    await ctx.send(f'Blackjack! {player.name}') 
                    break  # Break out of the loop since player got a blackjack

    async def card_table_update_embed(self, embed, game):
        # Clear previous fields
        embed.clear_fields()

        # Add fields for each player's hand
        cards_left = game.deck.num_cards_remaining()
        
        for player_id, player in game.player_objects.items():
            user = self.bot.get_user(player_id)
            hand_str = ", ".join(str(card) for card in player.hand)
            score_str = f"Score: {player.score}" if player.score <= 21 else "Busted!"
            embed.add_field(
                name=f"{user.display_name}'s Hand",
                value=f"{hand_str} ({score_str})",
                inline=False,
            )
            
        # Add a field for the dealer's hand (showing only one card if the round is in progress)
        if game.state == "Taking Bets":
            
            dealer_hand_str = ", ".join(str(card) for card in game.dealer.hand[:1])
            embed.add_field(
                name="Dealer's Hand",
                value=f"{dealer_hand_str} and a hidden card",
                inline=False,
            )
        else:
            dealer_hand_str = ", ".join(str(card) for card in game.dealer.hand)
            dealer_score_str = f"Score: {game.dealer.score}" if game.dealer.score <= 21 else "Busted!"
            embed.add_field(
                name="Dealer's Hand",
                value=f"{dealer_hand_str} ({dealer_score_str})",
                inline=False)
            
        embed.add_field(name="Cards Remaining in Shoe:", value=str(cards_left), inline=False)
    
    async def dealer_turn(self, ctx, channel_id, embed):  # noqa: E999
        
        self.state = "Dealer turn"
        game = self.games[channel_id]
        dealer = game.dealer

        # Initial embed update for the dealer's starting hand
        await self.card_table_update_embed(embed, game)
        dealer_message = await ctx.send(embed=embed)

        # Dealer rules: must hit until score is 17 or higher
        while dealer.score < 17:
            dealer.draw_card(game.deck)  # Add the card to the dealer's hand
            dealer.calculate_score()  # Recalculate the dealer's score
            await self.card_table_update_embed(embed, game)
            await dealer_message.edit(embed=embed)

            # Check if dealer is busted
            if dealer.score > 21:
                embed.add_field(
                    name="Dealer Busts!",
                    value=f"Dealer has busted with a score of {dealer.score}.",
                    inline=False,
                )
                await self.card_table_update_embed(embed, game)
                await dealer_message.edit(embed=embed)
                break  # End the dealer's turn if they bust

        # Final embed update if the dealer didn't bust
        if dealer.score <= 21:
            await self.card_table_update_embed(embed, game)
            await dealer_message.edit(embed=embed)

    async def payout(self, ctx, channel_id):
        print(f"Payout for channel ID: {channel_id}")
        game = self.games[channel_id]
        dealer = game.dealer

        for player_id, player in game.player_objects.items():
            member = ctx.guild.get_member(player_id)

            # * Player is busted
            if player.score > 21:
                await ctx.send(
                    f"{member.mention}, you're busted. You lose your bet of {player.bet}."
                )
                await bank.withdraw_credits(member, player.bet)

            # * Dealer is busted or player has higher score than dealer
            elif dealer.score > 21 or player.score > dealer.score:
                win_amount = player.bet * self.payouts["Win"]
                await ctx.send(f"{member.mention}, you win! You get {win_amount} chips.")
                await bank.deposit_credits(member, win_amount)

            # * It's a tie
            elif player.score == dealer.score:
                await ctx.send(f"{member.mention}, it's a tie! You get your bet back.")
                # * No change in chips

            # * Dealer wins
            else:
                await ctx.send(
                    f"{member.mention}, dealer wins. You lose your bet of {player.bet}."
                )
                await bank.withdraw_credits(member, player.bet)

            # Clear player's hand and states for the next round
            await player.clear_hand()

    async def build_game_state_embed(self, game):
        # Start creating the embed
        embed = discord.Embed(title="Slurms' Real Blackjack", color=0x0099FF)
        embed.set_author(name="Blackjack Dealer", icon_url="")

        # Update the embed with the current hands and scores
        await self.update_embed_with_hands(embed, game)

        
        embed.add_field(
            name="Cards Left in Shoe", value=str(len(game.deck.cards)), inline=False
        )

    
        return embed



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

    async def get_player_decision(self, ctx, player_id):
        def check(m):
            return m.author.id == player_id and m.content.lower() in ["hit", "stand"]

        try:
            msg = await ctx.bot.wait_for("message", timeout=15.0, check=check)
            return msg.content.lower()
        except asyncio.TimeoutError:
            return "timeout"

    @commands.group()
    async def realblackjack(self, ctx):
        """Play blackjack"""
        if ctx.guild is None: 
            await ctx.send("This command can only be used in a server.")
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid blackjack command passed...")
            
    @realblackjack.command()
    async def decks(self, ctx, number_of_decks: int):
        channel_id = ctx.channel.id
        game = self.games[channel_id]
        
        if self.games[channel_id].state != ["Waiting for bets"]:
            await ctx.send("A game is currently in progress. Cannot change the number of decks.")
            return

        self.deck = Deck(num_decks=number_of_decks)
        await ctx.send(f"Deck has been set to {number_of_decks} decks.")

    @realblackjack.command()
    async def start(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send("A game is already started in this channel.")
            return

        await ctx.send(
            f"Game will start in {self.join_state_timeout} seconds. Type `bj join` to join!"
        )
        # * Initialize joined_players
        joined_players = []

        def check_join(msg):
            return (
                msg.content.lower() == "bj join" or msg.content.lower() == "join" and msg.channel == ctx.channel
            )

        while True:
            try:
                msg = await self.bot.wait_for(
                    "message", timeout=self.join_state_timeout, check=check_join
                )  # Timeout adjusted to 30 seconds
                player_id = msg.author.id
                if player_id not in joined_players:
                    joined_players.append(player_id)
                    await ctx.send(f"{msg.author.mention} has joined the game!")
            except asyncio.TimeoutError:
                break

        if not joined_players:
            await ctx.send("No one joined. Game cancelled.")
            return

        # * Create a dictionary of player objects
        player_dict = {
            player_id: Player(self.bot.get_user(player_id).name, ctx)
            for player_id in joined_players
        }

        #! Debug to make sure players are being added to the dictionary
        print(f"Created player_dict: {player_dict}")

        # * Initialize GameState with the players who have joined
        self.games[channel_id] = GameState(self.bot, channel_id, self.games)
        game = self.games[channel_id]
        game.set_players(player_dict)  # Set the players in the GameState object
        embed = discord.Embed(title="Slurms' Real Blackjack", color=0x0099FF)

        for player in player_dict.values():
            await player.async_init(ctx)

        await ctx.send(f"Game starting with {len(joined_players)} players!")
        await self.play_game(ctx, channel_id, embed)

    @realblackjack.command()
    async def end(self, ctx):
        channel_id = ctx.channel.id
        game = self.games[channel_id]
        game.state = "End Game"
        if channel_id in self.games:
            del self.games[channel_id]
            await ctx.send("Game ended.")
        else:
            await ctx.send("No game in progress to end.")

    @realblackjack.command(name="leave", help="Leave an active game.")
    async def leave_game(self, ctx):
        """Allows a player to leave the game."""
        channel_id = ctx.channel.id
        player_id = ctx.author.id

        # Check if there is a game in this channel
        if channel_id not in self.games:
            await ctx.send("There is no active game in this channel.")
            return

        game = self.games[channel_id]

        # Check if the player is in the game
        if player_id not in game.player_objects:
            await ctx.send("You are not in the game.")
            return

        # Handle the player's departure
        # This could include refunding their bet, removing their hand, etc.
        player = game.player_objects[player_id]
        await self.handle_player_departure(game, player)

        # Remove the player from the game
        del game.player_objects[player_id]

        # Send a message to the channel
        await ctx.send(f"{ctx.author.mention} has left the game.")

    async def handle_player_departure(self, game, player):
        """
        Handles any additional logic when a player leaves the game.
        """
        # Refund the player's bet if necessary
        if game.current_bet and game.state == "betting":
            await bank.deposit_credits(player.user, game.current_bet)

        # Clear the player's hand and any other game-specific actions
        await player.clear_hand()

    @realblackjack.command()
    async def gamestate(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            game = self.games[channel_id]
            await ctx.send(f"Game state: {game.state}")

    @realblackjack.command()
    async def join_timeout(self, ctx, timeout: int):
        if timeout < 10:
            await ctx.send("Timeout must be at least 10 seconds.")
            return
        if timeout > 30:
            await ctx.send("Timeout cannot be more than 30 seconds.")
            return
        self.join_state_timeout = timeout
        await ctx.send(f"Join timeout set to {timeout} seconds.")

    @realblackjack.command()
    async def bet(self, ctx, amount: int):
        print(f"Bet command received for channel ID: {ctx.channel.id}")
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            await ctx.send("No game in progress.")
            return

        game = self.games[channel_id]
        player = game.player_objects.get(ctx.author.id)
        if player:
            success = player.place_bet(amount, await bank.get_balance(ctx.author))
            if success:
                await ctx.send(f"{ctx.author.mention} placed a bet of {amount}.")
            else:
                await ctx.send("Invalid bet.")

    @realblackjack.command(name="cardsleft")
    async def cards_remaining(self, ctx):
        """Tells how many cards are left in the shoe."""
        channel_id = ctx.channel.id
        game = self.games.get(channel_id)
        if ctx.channel.id in game:
            remaining_cards = game.deck.num_cards_remaining()
            await ctx.send(remaining_cards)
        else:
            await ctx.send("There's no active game in this channel.")

    @realblackjack.command()
    async def endgame(self, ctx):
        print(f"Endgame command received for channel ID: {ctx.channel.id}")
        channel_id = ctx.channel.id
        if channel_id in self.games:
            self.end_game = True
            await ctx.send("Game will end after the current round.")

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
        await ctx.send("Welcome to Real Blackjack! Let's play!")
        game = self.games[channel_id]
        game.end_game = False

        while not game.end_game:
            await game.take_bets(ctx, channel_id)  # Take bets from players

            # Check if bets were placed. If not, you may want to skip the round or handle it accordingly.

            await game.setup_game(ctx, channel_id, embed)  # Dealing initial cards

            # Invoke player_turns here
            await game.player_turns(ctx, channel_id, embed)

            # Only proceed to the dealer's turn if there's at least one player who hasn't busted
            if any(player.score <= 21 for player in game.player_objects.values()):
                await game.dealer_turn(ctx, channel_id, embed)  # Dealer's turn

            await game.payout(ctx, channel_id)  # Payouts and ending the round
            await game.clear_states(ctx, channel_id)

            # Ask or check if players want to continue or end the game here

            await ctx.send(
                "The Dealer clears the table, another round will begin in 5 seconds!"
            )

        await ctx.send("Game over. Thanks for playing!")

    @realblackjack.command(name="testdeck", hidden = True, help = "Test the game deck")
    async def test_deck(self, deck):
        deck = Deck()
        deck.shuffle()
        return(deck.cards)
    
async def setup(bot):
    await bot.add_cog(RealBlackJack(bot))