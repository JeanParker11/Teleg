from telegram import Update
from telegram.ext import ContextTypes
from config import SUDO_USERS

# Fonction ban (admin only)
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    bot = context.bot

    if query.from_user.id not in SUDO_USERS:
        await query.answer("Tu n'as pas les permissions.")
        return
    
    await query.edit_message_text("Réponds au message de l'utilisateur que tu veux bannir avec /ban.")

# Commande ban (via handle ou réponse)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.get_member(update.effective_user.id).status not in ['administrator', 'creator']:
        await update.message.reply_text("Tu n'es pas admin!")
        return

    user_to_ban = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user_to_ban.id)
    await update.message.reply_text(f"{user_to_ban.first_name} a été banni!")
