import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TOKEN, SUDO_USERS

# Configuration du logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
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
        reply_markup=reply_markup,
    )

# Fonction pour kicker tous les membres non-admins
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    bot = context.bot

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    await query.answer("🕒 Suppression de tous les membres non-admins...")

    # Récupère la liste des membres du groupe
    try:
        members = await chat.get_members()  # Remplacer par une méthode valide pour obtenir les membres
        kicked_users = 0
        for member in members:
            # Ignore les administrateurs, le bot et les utilisateurs dans la liste SUDO_USERS
            if member.user.id not in SUDO_USERS and member.user.id != bot.id and member.status not in ['administrator', 'creator']:
                try:
                    await chat.ban_member(member.user.id)
                    kicked_users += 1
                except Exception as e:
                    logger.error(f"Erreur lors du kick de {member.user.id}: {e}")

        await query.edit_message_text(f"✅ {kicked_users} membres non-admins ont été expulsés!")
    except Exception as e:
        await query.edit_message_text(f"Erreur lors du kick de tous les membres: {e}")

# Commande pour bannir un utilisateur via réponse
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # Vérifie si l'utilisateur appelant est admin
    user_status = await chat.get_member(update.effective_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Tu n'es pas admin!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠ Utilise cette commande en répondant à un message.")
        return

    user_to_ban = update.message.reply_to_message.from_user
    await chat.ban_member(user_to_ban.id)
    await update.message.reply_text(f"✅ {user_to_ban.first_name} a été banni!")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))

    print("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
