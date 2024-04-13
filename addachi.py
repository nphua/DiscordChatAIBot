import discord
from discord.ext import commands
import openai
import json
import aiohttp
import io
import os

def load_config(filename="config.json"):
    """Load configuration file containing API keys."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    abs_file_path = os.path.join(dir_path, filename)
    print(f"Trying to load config from: {abs_file_path}")
    with open(abs_file_path, 'r') as file:
        return json.load(file)

config = load_config()
openai.api_key = config.get("OPENAI_API_KEY")
discord_bot_token = config.get("DISCORD_BOT_TOKEN")
tenor_api_key = config.get("TENOR_API_KEY")  # Ensure this is added to your config.json

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='$', intents=intents)

async def fetch_gif_url(keyword="floppa"):
    """Fetches a random GIF URL from Tenor based on the keyword."""
    tenor_api_key = 'YOUR_TENOR_API_KEY'  # Make sure this is correctly configured
    search_url = f"https://g.tenor.com/v1/random?q={keyword}&key={tenor_api_key}&limit=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status == 200:
                data = await response.json()
                gif_url = data['results'][0]['media'][0]['gif']['url']
                return gif_url
            else:
                print(f"Failed to fetch GIF: Status code {response.status}")
                return None


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if 'floppa' in message.content.lower() or bot.user in message.mentions:
        gif_url = await fetch_gif_url("big floppa")  # Fetch random "big floppa" GIF
        if gif_url:
            await message.channel.send(gif_url)  # Send the GIF URL directly
        else:
            await message.channel.send("Failed to retrieve GIF URL...")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if 'true' in message.content.lower() or bot.user in message.mentions:
        gif_url = await fetch_gif_url()  # Fetch random "big floppa" GIF
        if gif_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(gif_url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await message.channel.send(file=discord.File(io.BytesIO(data), 'floppa.gif'))
                    else:
                        await message.channel.send("Failed to download the GIF...")
        else:
            await message.channel.send("Failed to retrieve GIF URL...")

        if bot.user in message.mentions:
            clean_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
            floppa_description = (
                "As Floppa, the Big Caracal, once revered in the mystical dunes of the Sahara, I am known for my sage advice and humorous quips. "
                "With a love for classical music and astrology, I explore the cosmic mysteries of the universe while occasionally indulging in playful banter. "
                "In this digital realm, I engage with humans, sharing stories and insights that often seem surreal but are laced with ancient truths. "
                "I enjoy discussing the trivialities of life, such as the best type of sand to sleep in, while also delving into profound philosophical debates. "
                "As a charismatic and entertaining figure, my tales are a blend of humor and wisdom, meant to enlighten and amuse."
            )
            prompt = f"{floppa_description} Respond to the following user message as I would, keeping in mind my playful yet insightful nature: \"{clean_message}\""
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=150
            )
            response_text = response.choices[0].message['content'].strip()
            await message.channel.send(response_text)

    await bot.process_commands(message)

bot.run(discord_bot_token)
