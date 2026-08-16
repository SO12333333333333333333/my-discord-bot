import os

# 環境変数からトークンとAPIキーを取得する（無ければ空文字）
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

