import discord
from discord.ext import commands
import openai
import json
import aiohttp
import io
import os

default_floppa_personality = ("add you own")

def read_floppa_personality():
    """Read and return the content of 'floppa_personality.txt' as a string."""
    filepath = 'floppa_personality.txt'  # Assuming the file is in the same directory as this script
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file {filepath} was not found in the current directory.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

# Load the Floppa personality from the text file
floppa_personality = read_floppa_personality()
if not floppa_personality:
    print("Floppa personality could not be found, loading default.")
    floppa_personality = default_floppa_personality


def load_config(filename="config.json"):
    """Load configuration file containing API keys."""
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abs_file_path = os.path.join(dir_path, filename)
        with open(abs_file_path, 'r') as file:
            print(f"Configuration loaded from: {abs_file_path}")
            return json.load(file)
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return None

config = load_config()
if not config:
    print("Configuration could not be loaded. Please check the config file.")
    exit(1)

openai.api_key = config.get("OPENAI_API_KEY")
discord_bot_token = config.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Dictionary to store the last 10 messages for each user, including bot's responses
user_message_memory = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    global count  # Declare 'count' as global to modify it within this function
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    user_id = message.author.id
    user_name = message.author.name  # Get user's name

    # Initialize memory for new users
    if user_id not in user_message_memory:
        user_message_memory[user_id] = []

    # Append new message to the specific user's memory
    user_message_memory[user_id].append(f"{user_name}: {message.content}")
    
    # Ensure the memory does not exceed 100 messages for the user
    if len(user_message_memory[user_id]) > 100:
        user_message_memory[user_id].pop(0)

    if bot.user.mentioned_in(message):
        # Use the last 100 messages from this user as context
        context = "\n".join(user_message_memory[user_id][-100:])
        clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        print(len(user_message_memory[user_id]))
        if len(user_message_memory[user_id]) % 5 == 0 or len(user_message_memory[user_id]) == 1:
            prompt = f"Previous conversation context:\n{context}\nThe person your talking to is: {user_name}\nYou are:{floppa_personality}\nRespond to the following user message in first person: \"{clean_message}\""
            print("Personality Refreshed!: ", user_name)
        else:
            prompt = f"Previous conversation context:\n{context}\nRespond to the following user message in first person: \"{clean_message}\""

        
        try:
            # Call OpenAI API with the constructed prompt
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500
            )
            response_text = response.choices[0].message['content'].strip()
            await message.channel.send(response_text)

            # Append the bot's own response to the memory
            user_message_memory[user_id].append(f"Bot: {response_text}")
        except Exception as e:
            error_message = "Sorry, there was an error processing your request."
            print(f"Failed to call OpenAI API: {e}")
            await message.channel.send(error_message)
            # Remember the bot's error message too
            user_message_memory[user_id].append(f"Bot: {error_message}")

    await bot.process_commands(message)

bot.run(discord_bot_token)
