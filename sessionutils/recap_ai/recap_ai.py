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
        with open(".\\conversation_history.json", "w") as file:
            json.dump(self.conversation_history, file)

    def read_conversation_history(self):
        with open(".\\conversation_history.json", "r") as file:
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

    def recap_to_story_gpt4(self, message):
        try:
            self.conversation_history.append({"role": "user", "content": message})
            response = self.get_openai_response([
                {
                    "role": "assistant",
<<<<<<< HEAD
                    "content": "The party members are Seeker (automaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter), and Epho (satyr Bard).",
                },
                {
                    "role": "user",
                    "content": f"Keep the story short, and do not add detail which was not in the session recap",
                },
            ])
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_conversation_history()
            return response
=======
                    "content": f"With the supplied text which is a brief synopsis, write the text into long form written in the Dungeons and Dragons Universe in the style of high fantasy. The party members are Seeker (aormaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter) and Epho (satyr Bard). Here is a part of the story:\n {message}:",
                }
            ],
            temperature=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )

        return response["choices"][0]["message"]["content"]

    def recap_to_story(self, message):
        message_scrub = self.remove_special_characters(message)
        prompt = f"""With the supplied string of text, craft the outline of this text into the style of a high fantasy novel written in the Dungeons and Dragons Universe. The party members are Seeker (aormaton fighter), Asinis (human cleric), Astrea (druid), Serath (hollowed one fighter) and Epho (satyr Bard). Here is my message:\n{message_scrub}"""
        try:
            # Check if the message qualifies as meaningful feedback
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.9,
                top_p=1,
                frequency_penalty=0.2,
                presence_penalty=0.2,
            )
            return response.choices[0].text.strip()
>>>>>>> parent of 9124801 (Update recap_ai.py)

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def add_to_recap(self, instruction):
        try:
            self.conversation_history.append({"role": "system", "content": instruction})
            new_response = self.get_openai_response([
                {
                    "role": "system",
                    "content": "The user would like to add more details to the story.",
                },
                {
                    "role": "user",
                    "content": f"Here is the previous story: {self.conversation_history}",
                },
            ])
            self.conversation_history.append({"role": "assistant", "content": new_response})
            self.save_conversation_history()
            return new_response

        except Exception as e:
            return str(e)
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_conversation_history()
            return response["choices"][0]["message"]["content"]

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."

    def add_to_recap(self, instruction):
        try:
            self.conversation_history.append({"role": "system", "content": instruction})
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
            self.save_conversation_history()
            return new_response["choices"][0]["message"]["content"]
        except Exception as e:
            return str(e)
