import os
import discord
from discord.ext import commands
from google import genai
from gtts import gTTS
import config
import threading
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return 'Bot is alive!'


def run():
  app.run(host='0.0.0.0', port=8080)


# ダミーサーバーを別スレッドで起動
threading.Thread(target=run).start()
# Gemini APIの初期化
client = genai.Client(api_key=config.GEMINI_API_KEY)

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

def get_system_instruction():
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "あなたはツンデレな幼馴染です。"

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"同期されたコマンド数: {len(synced)}")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")

# VC退出コマンド (/leave)
@bot.tree.command(name="leave", description="ボイスチャンネルから切断する")
async def leave_command(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("別にどこにも参加してないんだけど？")
        return

    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("じゃあね！べ、別になごり惜しくなんてないんだから！")

# 質問＆読み上げコマンド (/q)
@bot.tree.command(name="q", description="ツンデレ幼馴染に質問する（クラウドTTS読み上げ）")
async def q_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    # 自動VC参加
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            await channel.connect()
        elif interaction.guild.voice_client.channel != channel:
            await interaction.guild.voice_client.move_to(channel)

    try:
        system_prompt = get_system_instruction()
        full_prompt = f"{system_prompt}\n\nユーザーの質問: {question}"

        # Gemini 2.5 Flashでテキスト生成
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=full_prompt,
        )
        reply_text = response.text

        await interaction.followup.send(f"**質問:** {question}\n\n{reply_text}")

        # VCに接続中ならクラウドTTSで音声を生成して再生
        vc = interaction.guild.voice_client
        if vc is not None and vc.is_connected():
            tts = gTTS(text=reply_text, lang="ja")
            audio_file = "response.mp3"
            tts.save(audio_file)

            if vc.is_playing():
                vc.stop()

            # FFmpegオプションで再生速度を少し上げて聞きやすく調整
            ffmpeg_options = {
                'options': '-filter:a "atempo=1.15"'
            }
            vc.play(discord.FFmpegPCMAudio(audio_file, **ffmpeg_options))

    except Exception as e:
        print(f"エラー発生: {e}")
        await interaction.followup.send(f"エラーが発生しちゃったじゃない！…（エラー内容: {e}）")

bot.run(config.DISCORD_TOKEN)
