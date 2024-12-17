from telegram import Update
from telegram.ext import ContextTypes
from config import SUDO_USERS

# Fonction pour kick tout le monde (admin only)
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    bot = context.bot

    # Vérifie si l'utilisateur est admin
    admin_list = [admin.user.id for admin in await bot.get_chat_administrators(chat.id)]
    if query.from_user.id not in admin_list:
        await query.answer("Tu n'es pas admin!")
        return

    await query.answer("Suppression de tous les membres...")

    # Kick tous les membres sauf admins
    async for member in bot.get_chat_members(chat.id):
        if member.user.id not in SUDO_USERS and member.user.id != bot.id and not member.status in ['administrator', 'creator']:
            await bot.ban_chat_member(chat.id, member.user.id)
    
    await query.edit_message_text("Tous les membres non-admins ont été supprimés.")
