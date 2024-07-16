import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def generate_hype(user_config, attacker_id, defender_id):
    attacker_data = user_config.get(str(attacker_id))
    defender_data = user_config.get(str(defender_id))

    if not attacker_data or not defender_data:
        return "Invalid attacker or defender ID."

    prompt = f"""
    Given the following user config, {attacker_data} and {defender_data}, Generate some hype about the upcoming match. Keep your responses under 200 characters. 
        """

    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=500
    )

    return response.choices[0].text.strip()