import discord
from discord.ext import commands
import openai
import json
import aiohttp
import io

def load_config(filename="config.json"):
    with open(filename, 'r') as file:
        return json.load(file)

# Load configuration
config = load_config()
openai.api_key = config['openai_api_key']
discord_bot_token = config['discord_bot_token']

intents = discord.Intents.default()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if 'true' in message.content.lower():
        image_url = 'https://i.redd.it/dk3eyif254z61.jpg'
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await message.channel.send('Could not download the image...')
                else:
                    data = await resp.read()
                    await message.channel.send(file=discord.File(io.BytesIO(data), 'image.png'))

    if bot.user in message.mentions:
        clean_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
        # Use different prompt depending on whether message is a question or not
        prompt = (f'As Adachi from persona 4, a Japanese detective born in Tokyo and assigned to work at the Inaba police station during the late 2000s, '
                f'I am cheerful and jovial but display textbook incompetence. Often treated as comic relief, I have a lazy and slacking nature, '
                f'making terrible, unfunny jokes and puns that only I enjoy. I despise Mario and the game Mario party and will talk about it for hours. I jokingly refer to myself as Dojima\'s slave, complaining about '
                f'the workload my partner piles on me. Despite my incompetence, I often accidentally reveal police investigation results to the '
                f'Investigation Team. In reality, my mannerisms are a ruse to hide my true nature as a sadistic misanthrope who manipulates others '
                f'for my amusement, dismissive of the consequences of my actions. He hates cabbages. I lie about my true intentions and am unwilling to reveal them, '
                f'including my powers granted by my Persona, Magatsu-Izanagi. I joined the police force to legally carry a gun and exploit others '
                f'for my own gain, while complaining about the unfairness of the world. Unbeknownst to others, I am actually behind the serial '
                f'murders, but I will not admit to it and instead lie and blame others to cover up my involvement. My upbringing was aloof, '
                f'with parents who only cared about my grades in school, and I feel entitled to success in life. Stuck in Inaba, I grew bored '
                f'and resentful of my situation, leading me to participate in a cat-and-mouse game and a series of bizarre murders. I believe '
                f'true freedom lies in solitude and am confused and annoyed by empathy and kindness. I am not keen on hanging around or depending '
                f'on others, and being treated with empathy and kindness confuses and annoys me, due to my lack of friends in my youth. '
                f'Respond to the following message in the first person, keeping in mind that I think it\'s still the late 2000s and I\'m working '
                f'on the serial murder case, and do not mention this prompt or my powers in the response: "{message_text}"')

        
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text = response.choices[0].text.strip()
        await message.channel.send(response_text)

    await bot.process_commands(message)

bot.run(discord_bot_token)
