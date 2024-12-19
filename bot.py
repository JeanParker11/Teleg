import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
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

# Fonction pour kick tous les membres non-admins (simulation)
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    await query.answer("🕒 Bannissement des membres non-admins...")

    # Simuler le bannissement de tous les membres non-admins
    try:
        # Obtenez la liste des membres du groupe (attention, l'API ne permet pas d'obtenir tous les membres d'un coup)
        # Nous allons simuler en bannissant un membre à la fois. Il serait idéal de récupérer tous les membres d'une manière spécifique.
        members = await chat.get_members(limit=100)  # Limite la récupération à 100 membres pour éviter de dépasser les quotas API

        for member in members:
            # Bannir tous les membres non-admins
            if member.user.status not in ["administrator", "creator"]:
                try:
                    await chat.ban_member(member.user.id)
                    logger.info(f"Banni: {member.user.first_name} ({member.user.id})")
                except Exception as e:
                    logger.error(f"Erreur en bannissant {member.user.first_name}: {str(e)}")

        await query.edit_message_text("✅ Tous les membres non-admins ont été bannis.")
    except Exception as e:
        await query.edit_message_text(f"❌ Une erreur est survenue: {str(e)}")

# Fonction pour afficher un message d'aide au bannissement
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    await query.edit_message_text(
        "🔨 Pour bannir un utilisateur, utilise `/ban` en répondant au message de l'utilisateur."
    )

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
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))

    logger.info("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
