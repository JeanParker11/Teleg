from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler

# Fonction pour afficher le menu
def menu(update: Update, context):
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
def button_handler(update: Update, context):
    query = update.callback_query
    query.answer()  # Répond au callback pour éviter "loading..."

    chat = query.message.chat
    user = query.from_user

    if query.data == "ban_help":
        query.edit_message_text("🔨 Utilisez /ban @nom_utilisateur pour bannir un membre.")
    elif query.data == "tban_help":
        query.edit_message_text("⏳ Utilisez /tban @nom_utilisateur [durée] pour bannir temporairement un membre.")
    elif query.data == "kick_help":
        query.edit_message_text("🚪 Utilisez /kick @nom_utilisateur pour expulser un membre.")
    elif query.data == "unban_help":
        query.edit_message_text("🔓 Utilisez /unban @nom_utilisateur pour débannir un membre.")
    elif query.data == "masskick_help":
        query.edit_message_text("⚠ Suppression de tous les membres non-admins...")
        mass_kick(context.bot, chat)  # Appel à la fonction mass kick


# Fonction pour expulser tous les membres non-admins
def mass_kick(bot, chat):
    kicked_count = 0
    for member in chat.get_administrators():
        admins = [admin.user.id for admin in chat.get_administrators()]
        
    for member in bot.get_chat_members(chat.id):
        if member.user.id not in admins and not member.user.is_bot:
            try:
                bot.kick_chat_member(chat.id, member.user.id)
                kicked_count += 1
            except Exception as e:
                print(f"Erreur lors de la suppression de {member.user.id}: {e}")
    bot.send_message(chat.id, f"✅ {kicked_count} membres non-admins ont été expulsés.")

# Ajout des Handlers
MENU_HANDLER = CommandHandler("menu", menu)
BUTTON_HANDLER = CallbackQueryHandler(button_handler)

dispatcher.add_handler(MENU_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)
