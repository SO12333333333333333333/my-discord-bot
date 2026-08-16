import os
import discord
from discord import app_commands
import google.generativeai as genai

# 環境変数からトークンとAPIキーを取得
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Geminiの初期設定（3.5-flash-liteを使用）
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.5-flash-lite")

# Discord Client・CommandTree設定
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    # スラッシュコマンドをDiscordと同期
    await tree.sync()
    print(f"Logged in as {client.user}")

# /q コマンドの処理
@tree.command(name="q", description="Geminiに質問します")
async def q(interaction: discord.Interaction, question: str):
    # ① 3秒タイムアウトを防ぐため、最初に「考え中...」状態にして制限時間を15分へ延長する
    await interaction.response.defer()

    try:
        # Geminiで回答を生成
        response = model.generate_content(question)
        
        # ② defer() を使用したため、send_message ではなく followup.send で返信する
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"エラーが発生しました: {e}")

# ボットを起動
client.run(DISCORD_TOKEN)
