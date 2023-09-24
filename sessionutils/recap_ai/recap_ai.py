import openai
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()


class OpenAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []

    def save_conversation_history(self):
        with open("conversation_history.json", "w") as file:
            json.dump(self.conversation_history, file)

    def read_conversation_history(self):
        with open("conversation_history.json", "r") as file:
            return json.load(file)
    
    

    @staticmethod
    def remove_special_characters(input_string):
        pattern = r"[^a-zA-Z0-9\s]"
        return re.sub(pattern, "", input_string)

    def recap_to_story_gpt4(self, message):
        try:
            self.conversation_history.append({"role": "user", "content": message})
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant trained to convert short DND recaps into high fantasy narratives.",
                    },
                    {
                        "role": "user",
                        "content": f"Convert the following DND session recap into a high fantasy narrative:\n {message}",
                    },
                    {
                        "role": "assistant",
                        "content": "The party members are Seeker (automaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter), and Epho (satyr Bard).",
                    },
                    {
                        "role": "user",
                        "content": f"Keep the story short, and do not add detail which was not in the session recap",
                    },
                ],
                temperature=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.5,
            )
            self.conversation_history.append({"role": "assistant", "content": response})
            return response["choices"][0]["message"]["content"]

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def add_to_recap(self, instruction):
        try:
            self.conversation_history.append({"role": "system", "content": instruction})
            self.save_conversation_history()
            new_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "The user would like to add more details to the story.",
                    },
                    {
                        "role": "user",
                        "content": f"Here is the previous story: {self.conversation_history}",
                    },
                ],
                temperature=0.3,
                frequency_penalty=0.5,
                presence_penalty=0.5,
            )
            self.conversation_history.append(
                {"role": "assistant", "content": new_response}
            )
            return new_response
        except Exception as e:
            return str(e)
