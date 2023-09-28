import openai
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()


class Recap_AI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []

    def save_conversation_history(self):
        with open(os.path.join(".", "conversation_history.json"), "w") as file:
            json.dump(self.conversation_history, file)

    def read_conversation_history(self):
        with open(os.path.join(".", "conversation_history.json"), "r") as file:
            return json.load(file)

    @staticmethod
    def remove_special_characters(input_string):
        pattern = r"[^a-zA-Z0-9\s]"
        return re.sub(pattern, "", input_string)

    def get_openai_response(self, messages):
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

    def recap_to_story_gpt4(self, messages, adjustment_params=None):
        
        # Use adjustment_params to modify the API call
        temperature = adjustment_params.get('temperature', 0.3) if adjustment_params else 0.3
        frequency_penalty = adjustment_params.get('frequency_penalty', 0.5) if adjustment_params else 0.5
        presence_penalty = adjustment_params.get('presence_penalty', 0.5) if adjustment_params else 0.5

        try:        
            self.conversation_history.append({"role": "user", "content": messages})
            response = self.get_openai_response(
                [
                    {
                        "role": "system",
                        "content": "You are an assistant trained to convert short DND recaps into high fantasy narratives.",
                    },
                    {
                        "role": "user",
                        "content": f"Convert the following DND session recap into a high fantasy narrative:\n {messages}",
                    },
                    {
                        "role": "assistant",
                        "content": "The party members are Seeker (automaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter), and Yfo (satyr Bard).",
                    },
                    {
                        "role": "user",
                        "content": f"Keep the story short, and do not add detail which was not in the session recap",
                    },
                ]
            )
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_conversation_history()
            return response

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def edit_story(self, *command):
        try:
            last_story = (
                self.conversation_history[-1]["content"]
                if self.conversation_history
                else "No story has been generated yet."
            )

            # Build a new prompt based on the command
            new_prompt = f"Based on the previous story: '{last_story}', {command}"

            # Generate a new story based on the new prompt
            new_story = self.recap_to_story_gpt4(new_prompt)

            return new_story

        except Exception as e:
            return str(e)
