from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackQueryHandler, 
    CallbackContext
)
import os

# Configuration du TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Assurez-vous d'avoir défini la variable d'environnement TELEGRAM_BOT_TOKEN

# Fonction pour afficher le menu
def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔨 Bannir", callback_data="ban_help"),
         InlineKeyboardButton("⏳ Bannir Temporaire", callback_data="tban_help")],
        [InlineKeyboardButton("🚪 Expulser", callback_data="kick_help"),
         InlineKeyboardButton("🔓 Débannir", callback_data="unban_help")],
        [InlineKeyboardButton("⚠ Mass Kick", callback_data="masskick_help")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choisissez une action :", reply_markup=reply_markup)


# Callback pour chaque action
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat = query.message.chat
    if query.data == "ban_help":
        query.edit_message_text("🔨 Utilisez /ban @nom_utilisateur pour bannir un membre.")
    elif query.data == "tban_help":
        query.edit_message_text("⏳ Utilisez /tban @nom_utilisateur [durée] pour bannir temporairement un membre.")
    elif query.data == "kick_help":
        query.edit_message_text("🚪 Utilisez /kick @nom_utilisateur pour expulser un membre.")
    elif query.data == "unban_help":
        query.edit_message_text("🔓 Utilisez /unban @nom_utilisateur pour débannir un membre.")
    elif query.data == "masskick_help":
        query.edit_message_text("⚠ Suppression de tous les membres non-admins en cours...")
        mass_kick(context, chat)


# Fonction pour expulser tous les membres non-admins
def mass_kick(context: CallbackContext, chat):
    bot = context.bot
    admins = [admin.user.id for admin in chat.get_administrators()]
    kicked_count = 0

    for member in bot.get_chat_administrators(chat.id):
        if member.user.id not in admins and not member.user.is_bot:
            try:
                bot.kick_chat_member(chat.id, member.user.id)
                kicked_count += 1
            except Exception as e:
                print(f"Erreur : {e}")

    bot.send_message(chat.id, f"✅ {kicked_count} membres non-admins ont été expulsés.")

# Fonction principale pour démarrer le bot
def main():
    # Initialisation du bot
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Ajout des Handlers
    dispatcher.add_handler(CommandHandler("menu", menu))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Démarrer le bot
    print("Bot démarré...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
