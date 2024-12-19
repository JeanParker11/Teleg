import logging
import json
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
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

# Fonction pour enregistrer les membres actifs
async def track_active_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_member(user.id, user.username or user.first_name)
    logger.info(f"Membre actif détecté : {user.username or user.first_name} ({user.id})")

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

# Fonction pour kick tous les utilisateurs non-admin
async def kick_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    await query.answer("🕒 Suppression des membres non-admins...")

    # Listage des membres du chat (non disponible via l'API publique, cette partie est simulée)
    try:
        members = await chat.get_members(limit=200)  # Limité à 200 membres pour l'exemple
        for member in members:
            if member.status not in ["administrator", "creator"]:
                try:
                    await chat.kick_member(member.user.id)
                    logger.info(f"Utilisateur kické: {member.user.username}")
                except Exception as e:
                    logger.error(f"Impossible de kicker {member.user.username}: {str(e)}")
        await query.edit_message_text("✅ Tous les utilisateurs non-admins ont été kickés.")
    except Exception as e:
        await query.edit_message_text(f"❌ Une erreur est survenue: {str(e)}")

# Fonction pour bannir un utilisateur
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    await query.answer("🔨 Bannissement de l'utilisateur en cours...")

    # Vérifier si le message contient un utilisateur
    if not update.message.reply_to_message:
        await query.edit_message_text("⚠ Utilise cette commande en répondant à un message d'un utilisateur.")
        return

    user_to_ban = update.message.reply_to_message.from_user
    try:
        await chat.ban_member(user_to_ban.id)
        await query.edit_message_text(f"✅ {user_to_ban.first_name} a été banni!")
    except Exception as e:
        logger.error(f"Erreur lors du bannissement : {str(e)}")
        await query.edit_message_text(f"❌ Impossible de bannir {user_to_ban.first_name}.")

# Fonction pour afficher la liste des membres enregistrés
async def list_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat

    # Vérifie si l'utilisateur est admin
    user_status = await chat.get_member(query.from_user.id)
    if user_status.status not in ["administrator", "creator"]:
        await query.answer("❌ Tu n'es pas admin!")
        return

    # Charger la liste des membres enregistrés depuis le fichier JSON
    members = load_members()
    if not members:
        await query.answer("❌ Aucun membre trouvé.")
        return

    member_list = "\n".join([f"{username} (ID: {user_id})" for user_id, username in members.items()])
    
    await query.answer()
    await query.edit_message_text(
        f"👥 Liste des membres actifs:\n\n{member_list}",
    )

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))
    app.add_handler(CallbackQueryHandler(list_members, pattern="list_members"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members))

    print("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
