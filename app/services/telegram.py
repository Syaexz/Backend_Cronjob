
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_message(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[TELEGRAM] Token atau Chat ID belum diatur")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                json={
                    "chat_id": CHAT_ID,
                    "text": message,
                },
            )

            response.raise_for_status()
            result = response.json()
            return result.get("ok", False)

    except Exception as error:
        print(f"[TELEGRAM] Gagal mengirim pesan: {repr(error)}")

        if isinstance(error, httpx.HTTPStatusError):
            print(f"[TELEGRAM] Detail: {error.response.text}")

        return False
