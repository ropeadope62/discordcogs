import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_hype(user_config, attacker_id, defender_id, attacker_name, defender_name):
    # Define relevant keys
    relevant_keys = ['training_level', 'nutrition_level', 'wins', 'losses']

    # Extract relevant data for attacker and defender
    attacker_data = {key: user_config[str(attacker_id)].get(key) for key in relevant_keys}
    print(attacker_data) # debug print
    defender_data = {key: user_config[str(defender_id)].get(key) for key in relevant_keys}
    print(defender_data) # debug print
    

    if not attacker_data or not defender_data:
        return "Invalid attacker or defender ID."

    # Create a concise prompt
    prompt = (
        f"Generate some funny hype about the upcoming match between {attacker_name} and {defender_name}. "
        f"{attacker_name}'s stats: {attacker_data}. "
        f"{defender_name}'s stats: {defender_data}. "
        "Keep your response under 200 characters. Include some of their stats in the response."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a commentator for a fight in the Bullshido Kumatae."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content