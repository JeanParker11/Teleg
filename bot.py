import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import TOKEN

# Configuration du logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Fichier pour stocker les membres enregistrés
MEMBERS_FILE = "members.json"

# Charger ou initialiser le fichier JSON
def load_members():
    try:
        with open(MEMBERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_member(user_id, username):
    members = load_members()
    members[str(user_id)] = username
    with open(MEMBERS_FILE, "w") as file:
        json.dump(members, file)

# Commande /start avec un menu principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [
        [InlineKeyboardButton("🚫 Kick All", callback_data="kick_all")],
        [InlineKeyboardButton("🔨 Ban User", callback_data="ban_user")],
        [InlineKeyboardButton("👥 Liste des Membres", callback_data="list_members")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"Salut {user.first_name}!\nBienvenue dans le bot d'administration.\nChoisis une option :",
        reply_markup=reply_markup,
    )

# Fonction pour enregistrer les membres actifs
async def track_active_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_member(user.id, user.username or user.first_name)
    logger.info(f"Membre actif détecté : {user.username or user.first_name} ({user.id})")

# Fonction pour afficher la liste des membres enregistrés
async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    members = load_members()
    if not members:
        await update.callback_query.answer("Aucun membre enregistré pour le moment.")
        return

    response = "👥 Liste des membres enregistrés :\n"
    for user_id, username in members.items():
        response += f"- {username} (ID: {user_id})\n"

    await update.callback_query.edit_message_text(response)

# Fonction pour kick tout le monde (admin only)
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    await query.answer("🕒 Suppression des membres non-admins...")

    await query.edit_message_text(
        "⚠ Suppression de tous les membres non-admins n'est pas autorisée directement via l'API Telegram."
    )

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))
    app.add_handler(CallbackQueryHandler(list_members, pattern="list_members"))

    print("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
