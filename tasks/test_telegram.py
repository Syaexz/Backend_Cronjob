
import asyncio
from app.services.telegram import send_telegram_message


async def main():
    success = await send_telegram_message(
        "Tes notifikasi CronJob Scheduler berhasil!"
    )

    if success:
        print("Pesan Telegram berhasil dikirim.")
    else:
        print("Pesan Telegram gagal dikirim.")


if __name__ == "__main__":
    asyncio.run(main())
