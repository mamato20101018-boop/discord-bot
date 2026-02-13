import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

class NekoImage(commands.Cog):
    """猫耳・アニメ系画像を生成するCog"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_url = "https://nekos.best/api/v2"
        self.timeout = aiohttp.ClientTimeout(total=15)
        
    async def cog_load(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        logger.info("NekoImage Cog が読み込まれました")
        
    async def cog_unload(self):
        if self.session:
            await self.session.close()
        logger.info("NekoImage Cog がアンロードされました")

    @app_commands.command(
        name="猫画像生成",
        description="猫耳・アニメ系の画像を生成します"
    )
    @app_commands.describe(
        画像タイプ="生成する画像の種類を選択してください"
    )
    async def neko(
        self, 
        interaction: discord.Interaction,
        画像タイプ: Literal[
            "neko", "kitsune", "waifu", "husbando",
            "smile", "wave", "happy", "sleep"
        ] = "neko"
    ):
        
        await interaction.response.defer()
        
        try:
            if not self.session or self.session.closed:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            endpoint = f"{self.api_url}/{画像タイプ}"
            
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    await interaction.followup.send(
                        "❌ 画像の取得に失敗しました",
                        ephemeral=True
                    )
                    return
                        
                data = await response.json()

            if not data or "results" not in data:
                await interaction.followup.send(
                    "❌ 画像データの取得に失敗しました",
                    ephemeral=True
                )
                return
            
            results = data.get("results", [])
            if not results:
                await interaction.followup.send(
                    "❌ 画像が見つかりませんでした",
                    ephemeral=True
                )
                return
            
            image_data = results[0]
            image_url = image_data.get("url")
            artist_name = image_data.get("artist_name", "不明")
            artist_url = image_data.get("artist_href", "")
            source_url = image_data.get("source_url", "")
            
            type_names = {
                "neko": "猫耳",
                "kitsune": "狐耳",
                "waifu": "ワイフ",
                "husbando": "ハズバンド",
                "smile": "笑顔",
                "wave": "手振り",
                "happy": "ハッピー",
                "sleep": "睡眠"
            }
            
            embed = discord.Embed(
                color=0xFF69B4,
                title=f"🐱 {type_names.get(画像タイプ, 画像タイプ)}画像",
                description=f"タイプ: `{画像タイプ}`"
            )
            embed.set_image(url=image_url)
            
            if artist_name != "不明":
                if artist_url:
                    embed.add_field(
                        name="アーティスト",
                        value=f"[{artist_name}]({artist_url})",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="アーティスト",
                        value=artist_name,
                        inline=True
                    )
            
            if source_url:
                embed.add_field(
                    name="ソース",
                    value=f"[リンク]({source_url})",
                    inline=True
                )
            
            embed.set_footer(
                text=f"リクエスト者: {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(
                "❌ エラーが発生しました",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(NekoImage(bot))
