from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import SUDO_USERS

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
