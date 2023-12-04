import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
import muhammad_ali_chatgpt_bot

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key and Discord bot token from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_KEY")


# Define the intents
intents = discord.Intents.default()
intents.message_content = True

# Define the Discord bot command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store conversation history for each user
conversation_histories = {}

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

    # Get the user's ID
    user_id = str(message.author.id)

    # Initialize the conversation history for the user if not exists
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Classify user input using the OpenAI API with conversation history
    classified_category = muhammad_ali_chatgpt_bot.classify_user_input(message.content)
    # Generate a response based on the classified category using the OpenAI API
    bot_response = muhammad_ali_chatgpt_bot.generate_response(classified_category, message.content, conversation_histories[user_id])
    # Send the generated response to the Discord channel
    await message.channel.send(bot_response)

    # Update the user's conversation history
    conversation_histories[user_id].append(message.content)

    await bot.process_commands(message)

# Start the bot with the Discord bot token
bot.run(DISCORD_BOT_TOKEN)
