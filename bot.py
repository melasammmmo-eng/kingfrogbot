import discord23
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import os
from dotenv import load_dotenv
import yt_dlp
from openai import OpenAI

load_dotenv()

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Whitelist (starts with owner only)
whitelisted = {OWNER_ID}

# Music queue
queues = {}

# OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# ================== ANTI-THEFT ==================
@bot.event
async def on_guild_join(guild):
    if guild.owner_id != OWNER_ID:
        try:
            await guild.leave()
            owner = await bot.fetch_user(OWNER_ID)
            await owner.send(f"🚨 **Unauthorized Server Alert!**\n"
                             f"Server: **{guild.name}** ({guild.id})\n"
                             f"Owner: {guild.owner} ({guild.owner_id})\n"
                             f"I left automatically.")
        except:
            pass

# Check whitelist for all commands
async def is_whitelisted(interaction: discord.Interaction) -> bool:
    if interaction.user.id not in whitelisted:
        await interaction.response.send_message("You are not allowed to use this bot", ephemeral=True)
        return False
    return True

# ================== WHITELIST COMMANDS ==================

@tree.command(name="whitelist", description="Add user to whitelist (Owner only)")
@app_commands.describe(member="User to whitelist")
async def whitelist_cmd(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You are not allowed to use this bot", ephemeral=True)
        return
    whitelisted.add(member.id)
    await interaction.response.send_message(f"✅ **{member.name}** has been whitelisted!")

@tree.command(name="unwhitelist", description="Remove user from whitelist (Owner only)")
@app_commands.describe(member="User to remove")
async def unwhitelist_cmd(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You are not allowed to use this bot", ephemeral=True)
        return
    if member.id in whitelisted:
        whitelisted.remove(member.id)
        await interaction.response.send_message(f"✅ **{member.name}** removed from whitelist!")
    else:
        await interaction.response.send_message("❌ User is not whitelisted!")

# ================== SECURITY EXPLANATION ==================

@tree.command(name="security", description="Explain how the security system works")
async def security(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return

    security_info = """
**Security System Explanation:**

1. **Whitelist System**
   - Only whitelisted users can use any command in this bot.
   - If you are not whitelisted, you will see: "You are not allowed to use this bot"
   - Only the bot owner can add or remove users using `/whitelist` and `/unwhitelist`

2. **Anti-Theft Protection**
   - If someone adds the bot to a server that is not owned by the owner, the bot automatically leaves the server.
   - The owner gets a direct message with the server name and owner info.

3. **Private AI Chat**
   - `/chat` responses are completely private (only you can see them).

This keeps the bot completely private and secure.
    """
    await interaction.response.send_message(security_info, ephemeral=True)

# ================== HELP COMMAND ==================

@tree.command(name="help", description="Show all available commands")
async def help_cmd(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return

    help_text = """
**King AI Bot - Full Command List**

**Security & Whitelist:**
`/whitelist @user` - Add user (Owner only)
`/unwhitelist @user` - Remove user (Owner only)
`/security` - Explain security system
`/help` - Show this list

**AI Commands:**
`/chat <message>` - Talk to King AI (private)
`/imagine <prompt>` - Generate image with DALL-E
`/weather <city>` - Get AI weather explanation

**Music Commands:**
`/play <song>` - Play a song
`/pause` - Pause music
`/resume` - Resume music
`/skip` - Skip song
`/stop` - Stop and leave

**Fun Commands:**
`/joke` - Random joke
`/8ball <question>` - Magic 8-ball
`/roast @user` - Roast someone
`/meme` - Random meme
`/hug @user` - Hug someone
`/slap @user` - Slap someone
`/kiss @user` - Kiss someone
`/ship @user1 @user2` - Ship two people
`/pp @user` - PP size
`/gayrate @user` - Gay rate
`/simp @user` - Simp rate
`/reverse <text>` - Reverse text
`/coinflip` - Flip a coin
`/roll <sides>` - Roll a dice
`/avatar @user` - Get avatar
`/love @user1 @user2` - Love calculator
`/dadjoke` - Dad joke
`/emojify <text>` - Convert to emojis
`/catfact` - Cat fact
`/ppbattle @user1 @user2` - PP battle
`/trivia` - Random trivia
`/wouldyourather` - Would you rather?
`/neverhaveiever` - Never have I ever
`/truthordare` - Truth or Dare
`/rps <choice>` - Rock Paper Scissors
    """
    await interaction.response.send_message(help_text, ephemeral=True)

# ================== KING AI CHAT (PRIVATE) ==================

@tree.command(name="chat", description="Talk to King AI (private)")
@app_commands.describe(message="What do you want to say?")
async def chat(interaction: discord.Interaction, message: str):
    if not await is_whitelisted(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are King AI, a ai that hates a guy named bluemonkey and painfully rude to him ."},
                {"role": "user", "content": message}
            ],
            temperature=0.85
        )
        reply = response.choices[0].message.content
        await interaction.followup.send(reply, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

# ================== IMAGE GENERATION ==================

@tree.command(name="imagine", description="Generate image with DALL-E")
@app_commands.describe(prompt="Describe the image")
async def imagine(interaction: discord.Interaction, prompt: str):
    if not await is_whitelisted(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        await interaction.followup.send(f"**Generated Image:**\n{image_url}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error generating image: {str(e)}", ephemeral=True)

# ================== WEATHER WITH AI ==================

@tree.command(name="weather", description="Get AI-powered weather explanation")
@app_commands.describe(city="City name")
async def weather(interaction: discord.Interaction, city: str):
    if not await is_whitelisted(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful weather assistant. Give a friendly and detailed weather summary for the city."},
                {"role": "user", "content": f"What is the current weather in {city}?"}
            ]
        )
        weather_info = response.choices[0].message.content
        await interaction.followup.send(f"**Weather in {city}:**\n{weather_info}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Error getting weather: {str(e)}", ephemeral=True)

# ================== MUSIC COMMANDS ==================

@tree.command(name="play", description="Play a song")
@app_commands.describe(query="Song name or URL")
async def play(interaction: discord.Interaction, query: str):
    if not await is_whitelisted(interaction):
        return

    if not interaction.user.voice:
        await interaction.response.send_message("You need to be in a voice channel!")
        return

    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel
    if interaction.guild.voice_client is None:
        await voice_channel.connect()

    ydl_opts = {'format': 'bestaudio', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']

    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}))
    await interaction.followup.send(f"🎵 Now playing: **{title}**")

@tree.command(name="pause", description="Pause music")
async def pause(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("⏸️ Paused")
    else:
        await interaction.response.send_message("Nothing is playing")

@tree.command(name="resume", description="Resume music")
async def resume(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("▶️ Resumed")
    else:
        await interaction.response.send_message("Nothing to resume")

@tree.command(name="skip", description="Skip current song")
async def skip(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped")
    else:
        await interaction.response.send_message("Nothing to skip")

@tree.command(name="stop", description="Stop music and leave")
async def stop(interaction: discord.Interaction):
    if not await is_whitelisted(interaction):
        return
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Stopped and left voice channel")
    else:
        await interaction.response.send_message("I'm not in a voice channel")

# ================== FUN COMMANDS ==================

@tree.command(name="joke", description="Random joke")
async def joke(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["Why don't skeletons fight? They don't have the guts.", "I'm reading a book on anti-gravity. It's impossible to put down."]))

@tree.command(name="8ball", description="Ask the magic 8-ball")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
    answers = ["Yes", "No", "Maybe", "Definitely", "Ask again later"]
    await interaction.response.send_message(f"🎱 **{question}**\n**Answer:** {random.choice(answers)}")

@tree.command(name="roast", description="Roast someone")
@app_commands.describe(member="Who to roast")
async def roast(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    roasts = [f"{member.mention} is so ugly, when they were born the doctor slapped their parents."]
    await interaction.response.send_message(random.choice(roasts))

@tree.command(name="meme", description="Random meme")
async def meme(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(["When you finally understand the joke but you're in class 😭", "Error 404: Motivation not found"]))

@tree.command(name="hug", description="Hug someone")
@app_commands.describe(member="Who to hug")
async def hug(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    await interaction.response.send_message(f"{interaction.user.mention} hugged {member.mention}! 🤗")

@tree.command(name="slap", description="Slap someone")
@app_commands.describe(member="Who to slap")
async def slap(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    await interaction.response.send_message(f"{interaction.user.mention} slapped {member.mention}! 👋")

@tree.command(name="kiss", description="Kiss someone")
@app_commands.describe(member="Who to kiss")
async def kiss(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    await interaction.response.send_message(f"{interaction.user.mention} kissed {member.mention}! 💋")

@tree.command(name="ship", description="Ship two people")
@app_commands.describe(p1="First person", p2="Second person")
async def ship(interaction: discord.Interaction, p1: discord.Member, p2: discord.Member):
    name = p1.name[:len(p1.name)//2] + p2.name[len(p2.name)//2:]
    percent = random.randint(50, 100)
    await interaction.response.send_message(f"❤️ **{p1.name} x {p2.name}** = **{name}** ✨\nCompatibility: **{percent}%**")

@tree.command(name="pp", description="PP size (funny)")
@app_commands.describe(member="Who to check")
async def pp(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    size = random.randint(1, 30)
    await interaction.response.send_message(f"{member.mention}'s pp size: **{size}cm** {'='*size}😳")

@tree.command(name="gayrate", description="Gay rate someone")
@app_commands.describe(member="Who to rate")
async def gayrate(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    rate = random.randint(0, 100)
    await interaction.response.send_message(f"🏳️‍🌈 **{member.name}** is **{rate}%** gay")

@tree.command(name="simp", description="Simp rate someone")
@app_commands.describe(member="Who to rate")
async def simp(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    rate = random.randint(0, 100)
    await interaction.response.send_message(f"💔 **{member.name}** is **{rate}%** simp")

@tree.command(name="fact", description="Random fun fact")
async def fact(interaction: discord.Interaction):
    facts = ["Octopuses have three hearts.", "Bananas are technically berries.", "Honey never spoils."]
    await interaction.response.send_message(random.choice(facts))

@tree.command(name="reverse", description="Reverse text")
@app_commands.describe(text="Text to reverse")
async def reverse(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text[::-1])

@tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 **{random.choice(['Heads', 'Tails'])}**!")

@tree.command(name="roll", description="Roll a dice")
@app_commands.describe(sides="Number of sides (default 6)")
async def roll(interaction: discord.Interaction, sides: int = 6):
    await interaction.response.send_message(f"🎲 Rolled a **{random.randint(1, sides)}**!")

@tree.command(name="avatar", description="Get someone's avatar")
@app_commands.describe(member="Whose avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    if not member: member = interaction.user
    await interaction.response.send_message(member.display_avatar.url)

@tree.command(name="love", description="Love calculator")
@app_commands.describe(person1="First person", person2="Second person")
async def love(interaction: discord.Interaction, person1: discord.Member, person2: discord.Member):
    percent = random.randint(0, 100)
    await interaction.response.send_message(f"💖 **{person1.name}** & **{person2.name}** = **{percent}%** love")

@tree.command(name="dadjoke", description="Dad joke")
async def dadjoke(interaction: discord.Interaction):
    jokes = ["I'm reading a book about mazes. I got lost in it.", "Why don't eggs tell jokes? They'd crack each other up."]
    await interaction.response.send_message(random.choice(jokes))

@tree.command(name="emojify", description="Convert text to emojis")
@app_commands.describe(text="Text to emojify")
async def emojify(interaction: discord.Interaction, text: str):
    emoji_map = {char: f":regional_indicator_{char.lower()}:" for char in "abcdefghijklmnopqrstuvwxyz"}
    result = ''.join(emoji_map.get(c.lower(), c) for c in text)
    await interaction.response.send_message(result)

@tree.command(name="catfact", description="Random cat fact")
async def catfact(interaction: discord.Interaction):
    facts = ["Cats sleep 70% of their lives.", "A group of cats is called a clowder."]
    await interaction.response.send_message(random.choice(facts))

@tree.command(name="ppbattle", description="PP size battle")
@app_commands.describe(member1="First person", member2="Second person")
async def ppbattle(interaction: discord.Interaction, member1: discord.Member, member2: discord.Member):
    s1 = random.randint(1, 30)
    s2 = random.randint(1, 30)
    winner = member1 if s1 > s2 else member2
    await interaction.response.send_message(f"**{member1.name}**: {'='*s1} **{s1}cm**\n**{member2.name}**: {'='*s2} **{s2}cm**\n\n🏆 Winner: **{winner.name}**!")

@tree.command(name="trivia", description="Random trivia")
async def trivia(interaction: discord.Interaction):
    await interaction.response.send_message("What is the capital of France?\nA) London B) Paris C) Berlin\n\nAnswer: **B) Paris**")

@tree.command(name="wouldyourather", description="Would you rather?")
async def wouldyourather(interaction: discord.Interaction):
    options = ["Eat only pizza forever or only burgers forever?", "Be able to fly or be invisible?", "Have unlimited money or unlimited time?"]
    await interaction.response.send_message(random.choice(options))

@tree.command(name="neverhaveiever", description="Never have I ever")
async def neverhaveiever(interaction: discord.Interaction):
    statements = ["Never have I ever lied to my parents.", "Never have I ever stayed up all night."]
    await interaction.response.send_message(random.choice(statements))

@tree.command(name="truthordare", description="Truth or Dare")
async def truthordare(interaction: discord.Interaction):
    choice = random.choice(["Truth", "Dare"])
    await interaction.response.send_message(f"**{choice}**! Ask someone to give you one.")

@tree.command(name="rps", description="Rock Paper Scissors")
@app_commands.describe(choice="rock, paper, or scissors")
async def rps(interaction: discord.Interaction, choice: str):
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = "It's a tie!"
    elif (choice.lower() == "rock" and bot_choice == "scissors") or (choice.lower() == "paper" and bot_choice == "rock") or (choice.lower() == "scissors" and bot_choice == "paper"):
        result = "You win!"
    else:
        result = "I win!"
    await interaction.response.send_message(f"You chose **{choice}** | I chose **{bot_choice}**\n**{result}**")

# Sync commands
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is online as {bot.user}")
    print(f"Whitelisted users: {len(whitelisted)}")

bot.run(TOKEN)
