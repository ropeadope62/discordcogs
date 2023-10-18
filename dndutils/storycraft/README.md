# StoryCraft

<a href="url"><img src="https://iili.io/J28Etst.png" align="center" height="200" width="400" ></a>


StoryCraft is a Discord bot built as a cog for the Redbot framework. It leverages the power of GPT-4 to turn your D&D session notes into high-fantasy stories. Record your adventures and let StoryCraft weave them into tales of valor and magic.

## Installation

To install StoryCraft, follow these steps:

1. Ensure you have Redbot already installed and set up. If not, you can find instructions [here](https://docs.discord.red/en/stable/install_windows.html).
2. Load the StoryCraft cog using Redbot's cog install command:
    ```bash
    [p]cog install StoryCraft
    ```
3. Once the cog is installed, load it into your bot:
    ```bash
    [p]load storycraft
    ```

## Usage

Convert DND game session notes into a high fantasy story with GPT-4 using StoryCraft.

### Getting Started

To get started, use the command:

```bash
[p]storycraft help
```

### Primary Commands

Here are some of the main commands you can use:

- `[p]storycraft start`: Start collecting messages.
- `[p]storycraft stop`: Stop collecting messages and join them into one string.
- `[p]storycraft announce`: Announce to the StoryCraft channel.
- `[p]storycraft channel`: Set the channel for the storycraft announcements.
- `[p]storycraft conversation`: Retrieve the current OpenAI conversation history.
- `[p]storycraft edit`: Make changes to an existing story.
- `[p]storycraft generate`: Send the latest session to OpenAI to generate a story.
- `[p]storycraft get`: Retrieve a session based on file in `glob.glob("session_*.txt")`.

- `[p]storycraft history`: Returns a list of all session files.

## Features

- **Real-time Session Notes**: Collect session notes in real-time with the `[p]storycraft start` and `[p]storycraft stop` commands.
- **High-Fantasy Stories**: Transform your D&D sessions into high-fantasy stories using GPT-4.
- **Session Management**: Retrieve past sessions and edit stories for an ever-evolving tale.
- **Customizable Stories**: Edit the generated stories to your liking for a personalized experience.
- **Channel Announcements**: Make announcements related to StoryCraft in a designated Discord channel.

## Examples
**Generating a Story from Player Notes**:
- {user} [p]storycraft start
- {bot} Started collecting messages for the story.
- {user} the group move deeper into the dungeon
- {user} Grandalf, the Wizard, casts Ice Knife but rolls 2 and misses
- {user} Leeroy charges into the fray and everyone dies
- {user} [p]storycraft stop
- {{bot}} Stopped collecting messages. Story saved to story______.txt.
- {user} [p]storycraft generate 
<p> {{bot}} In the heart of a foreboding dungeon, the fellowship of adventurers, led by the enigmatic Paladin, Leeroy, ventured deeper into the abyss. The air was thick with tension and uncertainty as they navigated through the labyrinthine corridors.

Grandalf, their venerable wizard, summoned his arcane powers to cast an Ice Knife spell. His eyes glowed with a frosty light as he conjured a shard of ice in his hand. Alas! His usually steady hand faltered, his spell veering off course. The icy dagger whistled through the air harmlessly before shattering against a stone wall.

Undeterred by Grandalf's miss, Leeroy charged headlong into the fray. A brave but reckless move that spelled disaster for them all. His battle cry echoed through the dungeon halls as he rushed towards their unseen enemies.

In an instant that seemed to stretch into eternity, everything went horribly wrong. One moment they were a band of adventurers; in the next, they were no more than lifeless bodies strewn across the cold dungeon floor. The echoes of Leeroy's charge still hung in the air long after everyone had drawn their last breaths.</p>

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

- Thanks to Redbot for providing the framework for Discord bots.
- GPT-4 by OpenAI for the AI capabilities.
