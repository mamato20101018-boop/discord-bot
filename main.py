import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    await bot.tree.sync()

async def main():
    async with bot:
        await bot.load_extension("neko_1")
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())
