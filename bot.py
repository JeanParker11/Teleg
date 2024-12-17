from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os

# Configuration du TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Définissez votre TOKEN comme variable d'environnement

# Fonction pour afficher le menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔨 Bannir", callback_data="ban_help"),
         InlineKeyboardButton("⏳ Bannir Temporaire", callback_data="tban_help")],
        [InlineKeyboardButton("🚪 Expulser", callback_data="kick_help"),
         InlineKeyboardButton("🔓 Débannir", callback_data="unban_help")],
        [InlineKeyboardButton("⚠ Mass Kick", callback_data="masskick_help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choisissez une action :", reply_markup=reply_markup)

# Callback pour gérer les actions
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ban_help":
        await query.edit_message_text("🔨 Utilisez /ban @nom_utilisateur pour bannir un membre.")
    elif query.data == "tban_help":
        await query.edit_message_text("⏳ Utilisez /tban @nom_utilisateur [durée] pour bannir temporairement un membre.")
    elif query.data == "kick_help":
        await query.edit_message_text("🚪 Utilisez /kick @nom_utilisateur pour expulser un membre.")
    elif query.data == "unban_help":
        await query.edit_message_text("🔓 Utilisez /unban @nom_utilisateur pour débannir un membre.")
    elif query.data == "masskick_help":
        await query.edit_message_text("⚠ Suppression de tous les membres non-admins en cours...")
        # Ajoutez ici la logique pour expulser les membres si nécessaire

# Fonction principale pour démarrer le bot
def main():
    # Création de l'application
    application = ApplicationBuilder().token(TOKEN).build()

    # Ajout des handlers
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Lancer le bot
    print("Bot démarré...")
    application.run_polling()

if __name__ == "__main__":
    main()
