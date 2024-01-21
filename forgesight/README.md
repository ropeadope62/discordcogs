<a href="url"><img src="https://iili.io/JnF9oG9.webp" align="center" height="300" width="350" ></a>


Forgesight is a TableFlip Foundry Bot, designed to promote engagement and reward participation in the discord community. The bot rewards server member participation with goals of making the server more fun and interactive. 

## Installation

To run Forgesight, follow these steps:

1. Create a .env file with your Discord Bot Token. 
2. Create a virtual environment with python -m venv .\path_to_venv
3. Activate the venv
4. git clone the repo into the venv and install the required modules 
5. Currently the bot has no setup function and should be run directly. python main.py

## Usage

### Getting Started

To get started, use the command:

```bash
[p]forgesight help
```

### Forgesight Command List
[p]show config
Get the current Forgesight configuration.
Usade: /show

[p]sync
Synchronize the Forgesight Slash commands between Discord API and the bot. 
Usage: /sync

[p]balance
Check your gold balance. Only visible to the command executor. 
Usage: /balance

[p]backup
Manually backup the Forgesight database. Enter the path and file name (no extension necessary) 
Usage: /backup forgesight_bak

[p]bank
Shows Forgesight Gold statistics. 
Usage: /bank

[p]log
Get or clear the Forgesight log file
Usage: /show_config

[p]set_min_message_length
Set the message size requirements for earning gold
Usage: /set_min_message_length 5 

[p]subscriber_bonus
Set the subscriber bonus applied to Gold rewards.

[p]media_bonus
Set the media bonus applied to Gold rewards.

[p]toggle_rewards
Toggle Gold rewards on or off.
Usage: /toggle_rewards <on/off>

[p]reward_timeout
Set the timeout for Gold rewards in seconds between messages.

[p]channel_restriction
Toggle channel restriction on or off.
Usage: /toggle_channel_restriction <on/off>

[p]toggle_reward_timeout
Toggle the message reward timeout on or off.
Usage: /toggle_reward_timeout <on/off>

[p]commands
Show a list of all Forgesight commands
Usage: /commands

[p]gold_leaderboard
Show the Server Gold leaderboard.
Usage: /gold_leaderboard

[p]gold_balance
Check a user's gold balance.
Usage: /gold_balance <@user>

[p]grant_gold
Grant gold to a user
Usage: /grant_gold <@user> <amount of gold>

[p]deduct_gold
Deduct gold from a user
Usage: /deduct_gold <@user> <amount of gold>

[p]default_gold_award
Set the gold reward per message.
Usage: /gold_reward <number of gold>

[p]configuration
Displays the current Forgesight configuration.
Usage: /configuration


show_config
Show the current Forgesight configuration.
Usage: /show_config
sync
Sync the bot tree commands.
Usage: /sync
balance
Check your gold balance.
Usage: /balance
backup
Manually Backup the Forgesight database.
Usage: /backup <filename>
forgesight
Forgesight - Community engagement bot for Tableflip Foundry.
bank
Show the current gold balance and stats of the Forgesight Bank.
log
Get or clear the Forgesight log file
Usage: /log <get/clear>
set_min_message_length
Set the minimum message length requirement for earning gold
subscriber_bonus
Set the subscriber bonus applied to Gold rewards.
media_bonus
Set the media bonus applied to Gold rewards.
get_mediabonus
Get the current media bonus applied to Gold rewards.
toggle_rewards
Toggle Gold rewards on or off.
Usage: /toggle_rewards <on/off>
reward_timeout
Set the timeout for Gold rewards in seconds between messages.
channel_restriction
Toggle channel restriction on or off.
Usage: /toggle_channel_restriction <on/off>
toggle_min_message_requirement
Toggle the message reward timeout on or off.
Usage: /toggle_reward_timeout <on/off>
set_streak_bonus
Set the streak bonus applied to Gold rewards.
get_user_data
Get the Forgesight user data for a specific user.
Usage: /get_user_data <user_id>
commands
Show a list of all Forgesight commands
Usage: /commands
gold_leaderboard
Show the Server Gold leaderboard.
Usage: /gold_leaderboard
goldbalance
Show your gold balance.
grant_gold
Grant gold to a user
Usage: /grant_gold <@user> <amount of gold>
deduct_gold
Deduct gold to a user
Usage: /deduct_gold <@user> <amount of gold>
say
Make the bot say something
Usage: /say <thing to say>
default_gold_award
Set the gold reward per message.
Usage: /gold_reward <number of gold>
## Features

- **Gold Rewards**: Collect session notes in real-time with the `[p]storycraft start` and `[p]storycraft stop` commands.
- **Subscriber Perks**: Transform your D&D sessions into high-fantasy stories using GPT-4.
- **Guild Bank**: Retrieve past sessions and edit stories for an ever-evolving tale.
- **Leaderboard**: Edit the generated stories to your liking for a personalized experience.
- **Gold Trading**: Trade Gold amongst guild members.

## Contributing

We welcome contributions to improve StoryCraft! To get started:

1. Fork the repository on GitHub.
2. Clone your fork locally on your machine.
3. Create a new branch for your feature or fix.
4. Make your changes and commit them with a clear message.
5. Push your changes to your fork on GitHub.
6. Create a pull request and wait for review.

For more information, see the [Contribution Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Discord.py
