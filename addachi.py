import discord
from discord.ext import commands
import openai
import json
import os


default_floppa_personality = ("add your own" )


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

# Dictionary to store the last 100 messages for each user, including bot's responses
user_message_memory = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Global memory to store messages
global_message_memory = []

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    # Append new message to the global memory
    global_message_memory.append(f"{message.author.name}: {message.content}")
    
    # Ensure the memory does not exceed 100 messages overall
    if len(global_message_memory) > 100:
        global_message_memory.pop(0)

    if bot.user.mentioned_in(message):
        # Use the last 100 messages as context, irrespective of the user
        context = "\n".join(global_message_memory[-100:])
        clean_message = message.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        # Check length to adjust prompts or personality exposure
        if len(global_message_memory) % 5 == 0 or len(global_message_memory) == 1:
            prompt = f"Previous conversation context:\n{context}\nYou are: {floppa_personality}\nRespond to {message.author.name} in first person STAY IN CHARACTER as you exist in real life: \"{clean_message}\""
            print("Personality Refrshed, talking to: ", {message.author.name})
        elif len(global_message_memory) > 40:
            prompt = f"Previous conversation context:\n{context}\nwill never admit to being an AI\nRespond to {message.author.name} in first person annoyed: \"{clean_message}\""
            print("Now annoyed, talking to: ",{message.author.name} )
        else:
            prompt = f"Previous conversation context:{context}\nwill never admit to being an AI\nRespond to {message.author.name} in first person: \"{clean_message}\""
        
        print("Conversation count is: ",len(global_message_memory))

        try:
            # Call OpenAI API with the constructed prompt
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500
            )
            response_text = response.choices[0].message['content'].strip()
            await message.channel.send(response_text)

            # Append the bot's own response to the global memory
            global_message_memory.append(f"Bot: {response_text}")
        except Exception as e:
            error_message = "Sorry, there was an error processing your request."
            print(f"Failed to call OpenAI API: {e}")
            await message.channel.send(error_message)
            global_message_memory.append(f"Bot: {error_message}")

    await bot.process_commands(message)

bot.run(discord_bot_token)
