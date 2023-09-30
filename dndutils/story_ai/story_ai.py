import openai
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()


class StoryCraft_AI:
    def __init__(self):
        """Initialize the StoryCraft AI class"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []

    def set_last_story(self, last_story):
        """Set the last story to be used in the next conversation setup"""
        self.last_story = last_story

    def save_conversation_history(self):
        """Save the conversation history to the conversation_history.json file"""
        with open(os.path.join(".", "conversation_history.json"), "w") as file:
            json.dump(self.conversation_history, file)

    def read_conversation_history(self):
        """Read the conversation history from the conversation_history.json file"""
        with open(os.path.join(".", "conversation_history.json"), "r") as file:
            return json.load(file)

    @staticmethod
    def remove_special_characters(input_string):
        """Remove special characters from a string. Useful when passing a string to the OpenAI API"""
        pattern = r"[^a-zA-Z0-9\s]"
        return re.sub(pattern, "", input_string)

    def get_openai_response(self, messages):
        """Get a response from the OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.5,
            )
            return response["choices"][0]["message"]["content"]
        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def session_to_story_gpt4(self, messages, adjustment_params=None):
        """Convert DND session notes into a high fantasy narrative using GPT-4
        this is the main function that is called from the discord bot when the user calls the storycraft generate command
        """
        temperature = (
            adjustment_params.get("temperature", 0.3) if adjustment_params else 0.3
        )
        frequency_penalty = (
            adjustment_params.get("frequency_penalty", 0.5)
            if adjustment_params
            else 0.5
        )
        presence_penalty = (
            adjustment_params.get("presence_penalty", 0.5) if adjustment_params else 0.5
        )

        try:
            self.conversation_history.append({"role": "user", "content": messages})
            response = self.get_openai_response(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant trained to convert short DND session notes into high fantasy narratives.",
                    },
                    {
                        "role": "user",
                        "content": f"Convert the following DND session notes into a high fantasy narrative:\n {messages}",
                    },
                    {
                        "role": "assistant",
                        "content": "The party members are Seeker (automaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter), and Yfo (satyr Bard).",
                    },
                    {
                        "role": "user",
                        "content": "Keep the story short, and do not add detail which was not in the session notes",
                    },
                ]
            )
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_conversation_history()
            return response

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def edit_story(self, last_story, edit_prompt):
        """Create a new conversation setup with the editing prompt and the last story"""
        try:
            new_prompt = [
                {
                    "role": "user",
                    "content": f"Edit the following story to {edit_prompt}: {last_story}",
                }
            ]
            return self.get_openai_response(new_prompt)
        except Exception as e:
            return str(e)

    def summarize_story_title(self, last_story, summary_prompt):
        """Summarize the story into a title to be added to the start of the paginated embed"""
        try:
            summary_prompt = [
                {
                    "role": "user",
                    "content": f"Summarize the following story into one line: {last_story}",
                }
            ]
            return self.get_openai_response(summary_prompt)
        except Exception as e:
            return str(e)
