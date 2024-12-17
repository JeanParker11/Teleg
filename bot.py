import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN, SUDO_USERS

# Configuration du logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Commande /start avec un menu principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [
        [InlineKeyboardButton("🚫 Kick All", callback_data="kick_all")],
        [InlineKeyboardButton("🔨 Ban User", callback_data="ban_user")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"Salut {user.first_name}!\nBienvenue dans le bot d'administration.\nChoisis une option :",
        reply_markup=reply_markup
    )

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

# Main
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des gestionnaires (handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))

    logger.info("Bot démarré...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
