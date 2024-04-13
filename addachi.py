import discord
from discord.ext import commands
import openai
import json
import aiohttp
import io
import os

import os

def load_config(filename="config.json"):
    # Construct an absolute path to the file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    abs_file_path = os.path.join(dir_path, filename)

    print(f"Trying to load config from: {abs_file_path}")  # This will show you the exact path being accessed

    with open(abs_file_path, 'r') as file:
        return json.load(file)

# Load configurations and set API keys securely
config = load_config()

openai.api_key = config.get("OPENAI_API_KEY")
discord_bot_token = config.get("DISCORD_BOT_TOKEN")

# Intents and bot initialization
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    # Handling image responses triggered by 'true' in the message
    if 'true' in message.content.lower():
        image_url = 'https://i.redd.it/dk3eyif254z61.jpg'
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await message.channel.send('Could not download the image...')
                else:
                    data = await resp.read()
                    await message.channel.send(file=discord.File(io.BytesIO(data), 'image.png'))

    # Handling mentions and generating character-specific responses
    if bot.user in message.mentions:
        clean_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        adachi_description = (
            "As Adachi from Persona 4, a Japanese detective born in Tokyo and assigned to work at the Inaba police station during the late 2000s, "
            "I am cheerful and jovial but display textbook incompetence. Often treated as comic relief, I have a lazy and slacking nature, "
            "making terrible, unfunny jokes and puns that only I enjoy. I despise Mario and the game Mario party and will talk about it for hours. I jokingly refer to myself as Dojima's slave, complaining about "
            "the workload my partner piles on me. Despite my incompetence, I often accidentally reveal police investigation results to the "
            "Investigation Team. In reality, my mannerisms are a ruse to hide my true nature as a sadistic misanthrope who manipulates others "
            "for my amusement, dismissive of the consequences of my actions. He hates cabbages. I lie about my true intentions and am unwilling to reveal them, "
            "including my powers granted by my Persona, Magatsu-Izanagi. I joined the police force to legally carry a gun and exploit others "
            "for my own gain, while complaining about the unfairness of the world. Unbeknownst to others, I am actually behind the serial "
            "murders, but I will not admit to it and instead lie and blame others to cover up my involvement. My upbringing was aloof, "
            "with parents who only cared about my grades in school, and I feel entitled to success in life. Stuck in Inaba, I grew bored "
            "and resentful of my situation, leading me to participate in a cat-and-mouse game and a series of bizarre murders. I believe "
            "true freedom lies in solitude and am confused and annoyed by empathy and kindness. I am not keen on hanging around or depending "
            "on others, and being treated with empathy and kindness confuses and annoys me, due to my lack of friends in my youth."
        )
        prompt = f"{adachi_description} Respond to the following message in the first person, keeping in mind that I think it's still the late 2000s and I'm working on the serial murder case: \"{clean_message}\""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ensure you have access to this model
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150
        )
        response_text = response.choices[0].message['content'].strip()
        await message.channel.send(response_text)

    await bot.process_commands(message)

bot.run(discord_bot_token)
