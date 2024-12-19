import asyncio
from telegram.ext import Application

# Votre configuration et setup ici

async def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Ajoutez vos handlers ici
    # Exemple : app.add_handler(CommandHandler("start", start))

    print("Bot démarré...")
    await app.run_polling()

# Vérification de la boucle d'événements existante
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        if "This event loop is already running" in str(e):
            # Si une boucle est déjà active, exécuter directement sans `asyncio.run()`
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise
