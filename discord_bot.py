import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
import re
import spacy
from spacy.matcher import Matcher

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key and Discord bot token from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_KEY")

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # This line might not be necessary, but I added it to be explicit

# Define the Discord bot command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to classify the user's utterance using the OpenAI API
def classify_user_input(utterance):
    classification_prompt = f"Is the following utterance related to Muhammad Ali? (Follow this format as a response if it's not related to Muhammad Ali at all: 'No' if it's directly a question about Muhammad Ali: 'Yes' and if it's a question that MAY be related to Muhammad Ali, such as a question about his opponents: 'Maybe'. I only ever want those three responses as responses.)'{utterance}'?"
    classification_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=classification_prompt,
        temperature=0.7,
        max_tokens=50
    )

    classified_category = extract_category(classification_response['choices'][0]['text'])
    return classified_category

# Function to generate a response based on the classified category using the OpenAI API
def generate_response(classified_category, user_utterance):
    if classified_category == "Muhammad Ali":
        response_prompt = f"Generate a response to the user's inquiry about Muhammad Ali. User's utterance: '{user_utterance}'."
    elif classified_category == "Maybe related":
        response_prompt = f"The user's utterance is most likely about someone related to Muhammad Ali. Give back an appropriate response on information that relates to their relationship with Muhammad Ali. User's utterance: '{user_utterance}'"
    else:
        response_prompt = f"Generate an appropriate response to the user's {classified_category} utterance, making sure to let them know that this is a bot about Muhammad Ali. User's utterance: '{user_utterance}'."
    
    response_generation_response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=response_prompt,
        temperature=0.8,
        max_tokens=150
    )

    return response_generation_response['choices'][0]['text']

# Function to extract the category from the OpenAI API response
def extract_category(api_response):
    if "No" in api_response or "No." in api_response:
        return "Not related"
    elif "Yes" in api_response or "Yes." in api_response:
        return "Muhammad Ali"
    elif "Maybe" in api_response or "Maybe." in api_response:
        return "Maybe related"
    else:
        return "unknown"

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Event triggered on every message in a server
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent an infinite loop
    if message.author == bot.user or not message.content.startswith('!'):
        return

    # Classify user input using the OpenAI API
    classified_category = classify_user_input(message.content)
    # Generate a response based on the classified category using the OpenAI API
    bot_response = generate_response(classified_category, message.content)
    # Send the generated response to the Discord channel
    await message.channel.send(bot_response)

    await bot.process_commands(message)

# Start the bot with the Discord bot token
bot.run(DISCORD_BOT_TOKEN)
