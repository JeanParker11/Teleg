import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from modules import start, ban_user, kick_all, ban  # Importation centralisée via __init__.py
from config import TOKEN

# Configuration du logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des gestionnaires de commandes et de callback
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))

    logger.info("Bot démarré...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
