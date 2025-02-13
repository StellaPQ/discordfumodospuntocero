import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import random
import asyncio
import config
import os
from logic import get_duck_image_url, setup_db, update_balance, get_top_users

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  

cooldowns = {}

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Estoy vivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
async def apply_cooldown(ctx, command_name, min_time, max_time):
    user_id = ctx.author.id
    if user_id in cooldowns and command_name in cooldowns[user_id]:
        remaining_time = cooldowns[user_id][command_name] - asyncio.get_event_loop().time()
        if remaining_time > 0:
            await ctx.send(f"{ctx.author.mention}, espera {int(remaining_time)} segundos antes de usar {command_name} de nuevo.")
            return False
    cooldown_time = random.randint(min_time, max_time)
    if user_id not in cooldowns:
        cooldowns[user_id] = {}
    cooldowns[user_id][command_name] = asyncio.get_event_loop().time() + cooldown_time
    return True

@bot.command(name=config.WORK_COMMAND)
async def work(ctx):
    if not await apply_cooldown(ctx, "work", config.WORK_MIN_COOLDOWN_, config.WORK_MAX_COOLDOWN):
        return
    earnings = random.randint(config.MIN_WORK, config.MAX_WORK)
    update_balance(ctx.author.id, earnings)
    await ctx.send(f"{ctx.author.mention}, trabajaste y ganaste {earnings} monedas.")

@bot.command(name=config.CRIME_COMMAND)
async def crime(ctx):
    if not await apply_cooldown(ctx, "crime", config.CRIME_MIN_COOLDOWN_, config.CRIME_MAX_COOLDOWN):
        return
    if random.randint(1, 100) <= config.CRIME_FAIL_CHANCE:
        await ctx.send(f"{ctx.author.mention}, fallaste.")
    else:
        earnings = random.randint(config.MIN_CRIME, config.MAX_CRIME)
        update_balance(ctx.author.id, earnings)
        await ctx.send(f"{ctx.author.mention}, robaste {earnings} monedas.")

@bot.command(name=config.LEADERBOARD_COMMAND)
async def leaderboard(ctx):
    top_users = get_top_users()
    if not top_users:
        await ctx.send("no hay usuarios")
        return
    leaderboard_text = "🏆 Leaderboard 🏆\n"
    for index, (user_id, balance) in enumerate(top_users, start=1):
        user = await bot.fetch_user(user_id)
        leaderboard_text += f"{index}. {user.name} - {balance} monedas\n"
    await ctx.send(leaderboard_text)

@bot.command(name=config.MEME_COMMAND)
async def meme(ctx):
    if random.randint(1, 20) == 1:
        rare_memes = os.listdir('rareimage')
        if rare_memes:
            meme = random.choice(rare_memes)
            folder = "rareimage"
    else:
        memes = os.listdir('images')
        if memes:
            meme = random.choice(memes)
            folder = "images"

    with open(f'{folder}/{meme}', 'rb') as f:
        picture = discord.File(f)
    await ctx.send(file=picture)

@bot.command('patito')
async def duck(ctx):
    image_url = get_duck_image_url()
    await ctx.send(image_url)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    setup_db()

keep_alive()
bot.run(config.TOKEN)

random.choice()