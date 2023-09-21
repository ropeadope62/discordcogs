import openai
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()


class OpenAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    @staticmethod
    def remove_special_characters(input_string):
        pattern = r"[^a-zA-Z0-9\s]"
        return re.sub(pattern, "", input_string)

    def recap_to_story(self, message):
        message_scrub = self.remove_special_characters(message)
        prompt = f"""With the supplied string of text, craft the outline of this text into the style of a high fantasy novel written in the Dungeons and Dragons Universe. The party members are Seeker (aormaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter) and Epho (satyr Bard). Here is my message:\n{message_scrub}"""
        try:
            # Check if the message qualifies as meaningful feedback
            response = openai.ChatCompletion.create(
                engine="gpt-4",
                messages=prompt,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.9,
                top_p=1,
                frequency_penalty=0.2,
                presence_penalty=0.2,
            )

            response_content = response.choices[0]["message"]["content"]
            return response_content
        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."
