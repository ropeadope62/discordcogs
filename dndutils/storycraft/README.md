# StoryCraft

[Alt text](https://iili.io/J28Etst.png)

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
