import discord
from discord.ext import commands
import time
import json
from datetime import date

study_sessions = {}
daily_log = {}
current_day = date.today()

def check_new_day():
    global current_day, daily_log
    today = date.today()
    if today != current_day:
        daily_log.clear()
        current_day = today

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

def load_data():
    global daily_log
    try:
        with open(DATA_FILE, "r") as f:
            daily_log = json.load(f)
            daily_log = {int(k): v for k, v in daily_log.items()}
    except FileNotFoundError:
        daily_log = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(daily_log, f)


@bot.event
async def on_ready():
    load_data()
    print("Bot ready")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def start(ctx, *, subject=None):
    check_new_day()

    if subject is None:
        await ctx.send("Please type a subject. Example: !start Python")
        return

    user_id = ctx.author.id

    if user_id in study_sessions:
        await ctx.send("You already started studying. Use !stop first.")
        return

    study_sessions[user_id] = {
        "subject": subject,
        "start_time": time.time()
    }

    await ctx.send(f"Started studying {subject}")

@bot.command()
async def stop(ctx):
    check_new_day()

    user_id = ctx.author.id

    if user_id not in study_sessions:
        await ctx.send("You didn’t start a study session.")
        return

    start_time = study_sessions[user_id]["start_time"]
    subject = study_sessions[user_id]["subject"]

    seconds = int(time.time() - start_time)

    if user_id not in daily_log:
        daily_log[user_id] = {}

    if subject not in daily_log[user_id]:
        daily_log[user_id][subject] = 0

    daily_log[user_id][subject] += seconds
    del study_sessions[user_id]

    if seconds < 60:
        await ctx.send(f"Studied {subject} for {seconds} seconds")
    else:
        minutes = seconds // 60
        await ctx.send(f"Studied {subject} for {minutes} minutes")

@bot.command()
async def summary(ctx):
    check_new_day()  

    user_id = ctx.author.id

    if user_id not in daily_log or not daily_log[user_id]:
        await ctx.send("No study data for today.")
        return

    message = "Today you studied:\n"
    for subject, seconds in daily_log[user_id].items():
        if seconds < 60:
            message += f"{subject} — {seconds} seconds\n"
        else:
            message += f"{subject} — {seconds // 60} minutes\n"

    await ctx.send(message)

@bot.command()
async def top(ctx):
    check_new_day()

    if not daily_log:
        await ctx.send("No study data for today.")
        return

    ranking = []

    for user_id, subjects in daily_log.items():
        total_seconds = sum(subjects.values())
        ranking.append((user_id, total_seconds))

    ranking.sort(key=lambda x: x[1], reverse=True)

    message = "🏆 Today's Top Studiers:\n"

    for i, (user_id, seconds) in enumerate(ranking[:5], start=1):
        user = await bot.fetch_user(user_id)
        if seconds < 60:
            message += f"{i}. {user.name} — {seconds} seconds\n"
        else:
            message += f"{i}. {user.name} — {seconds // 60} minutes\n"

    await ctx.send(message)


bot.run("YOUR_TOKEN_HERE")

