import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import sys

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_test_message():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el entorno o .env")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': '✅ Prueba de mensaje desde lolnotifier',
        'parse_mode': 'Markdown'
    }
    timeout = aiohttp.ClientTimeout(total=10)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=data) as resp:
                    print(f"Mensaje enviado. Status: {resp.status}")
                    print(await resp.text())
                    return
        except aiohttp.ClientConnectorError as e:
            print(f"[ERROR] DNS/Conexión fallida (intento {attempt}): {e}")
        except Exception as e:
            print(f"[ERROR] Excepción inesperada (intento {attempt}): {e}")

        wait = 2 ** attempt
        print(f"Reintentando en {wait} segundos...")
        await asyncio.sleep(wait)
    print("Fallo al enviar mensaje tras varios intentos. Verifica tu red y DNS.")

if __name__ == "__main__":
    # Windows event loop fix
    if sys.platform.startswith('win'):
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send_test_message())
