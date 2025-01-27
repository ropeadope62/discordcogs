# Caption Crunch - Discord Game

<img src="https://i.ibb.co/y4WCcbB/caption-crunch.png" alt="Markdown Logo" width="400" height="600">

**Caption Crunch** is a fun and interactive Discord game where users submit captions for an image, and then vote on the best one! The game is designed to be easy to set up and play, with rewards for the most creative captions. 

## Features

- **Image Captioning**: Users submit captions for an image, which can be either uploaded by an admin or fetched automatically from the Pexels API.
- **Voting System**: After submissions are collected, users vote on their favorite caption.
- **Rewards**: Winners can earn in-game currency (if enabled by the server admin).
- **Leaderboard**: Track the top players based on their wins and winnings.
- **Customizable Settings**: Admins can configure various settings such as submission timeout, vote timeout, caption length limits, and more.

## Installation

1. **Prerequisites**:
   - Ensure you have Python 3.8 or higher installed.
   - Install the required dependencies using `pip`:
     ```bash
     pip install -r requirements.txt
     ```
   - You will need a Pexels API key, which can be obtained from [Pexels](https://www.pexels.com/api/).

2. **Setup**:
   - Clone the repository or download the `captioncrunch.py` file.
   - Place the file in your Red-DiscordBot `cogs` directory.
   - Add your Pexels API key to a `.env` file in the same directory as the cog:
     ```plaintext
     PEXELS_API_KEY=your_pexels_api_key_here
     ```

3. **Load the Cog**:
   - Start your Red-DiscordBot.
   - Load the `CaptionCrunch` cog using the following command in Discord:
     ```plaintext
     [p]load captioncrunch
     ```

## Commands

### Admin Commands

- `captioncrunch setquery <query>`: Set the search query for the Pexels API.
- `captioncrunch setchannel`: Set the channel for Caption Crunch submissions.
- `captioncrunch setminlength <int>`: Set the minimum caption length.
- `captioncrunch setmaxlength <int>`: Set the maximum caption length.
- `captioncrunch setsubmissiontimeout <int>`: Set the submission timeout in seconds.
- `captioncrunch setvotetimeout <int>`: Set the vote timeout in seconds.
- `captioncrunch togglerewards`: Toggle rewards for winning captions.
- `captioncrunch rewardrange <min> <max>`: Set the reward range for winning captions.
- `captioncrunch setfontsize <size>`: Set the font size for captions.
- `captioncrunch settings`: Display the current guild configuration settings.

### User Commands

- `captioncrunch start`: Start a new Caption Crunch game.
- `captioncrunch stats [@user]`: View Caption Crunch stats for yourself or another user.
- `captioncrunch leaderboard`: Display the Caption Crunch leaderboard.
- `captioncrunch help`: Show the help message for Caption Crunch.

## How to Play

1. **Start the Game**: A can start the game using the `captioncrunch start` command.
   - **Optional**: Start the game with a custom image by attaching it with the start command. 
2. **Submit Captions**: Users submit captions by typing their caption in double quotes (e.g., `"This is my caption"`) in the designated channel.
3. **Vote**: After the submission period ends, users vote on their favorite caption by typing the corresponding number.
4. **Win**: The caption with the most votes wins, and the user who submitted it earns rewards (if enabled).

## Configuration

The game can be customized using the various admin commands. For example, you can set the minimum and maximum caption lengths, adjust the submission and vote timeouts, and enable or disable rewards.

## Support

If you encounter any issues or have suggestions for improvements, please open an issue on the [GitHub repository](https://github.com/ropeadope62/discordcogs).

## Credits

- **Developer**: Slurms Mackenzie (ropeadope62)
- **Repository**: [GitHub](https://github.com/ropeadope62/discordcogs)

Enjoy playing **Caption Crunch** on your Discord server! 🎉