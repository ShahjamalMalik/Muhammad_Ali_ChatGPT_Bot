import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
import re
import spacy
from spacy.matcher import Matcher
import muhammad_ali_chatgpt_bot as muhammad_ali_bot_utils

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key and Discord bot token from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_KEY")

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define the intents
intents = discord.Intents.default()
intents.message_content = True

# Define the Discord bot command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

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
    classified_category = muhammad_ali_bot_utils.classify_user_input(message.content)
    # Generate a response based on the classified category using the OpenAI API
    bot_response = muhammad_ali_bot_utils.generate_response(classified_category, message.content)
    # Send the generated response to the Discord channel
    await message.channel.send(bot_response)

    await bot.process_commands(message)

# Start the bot with the Discord bot token
bot.run(DISCORD_BOT_TOKEN)
