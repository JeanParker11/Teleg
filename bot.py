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

# Fonction pour promouvoir un utilisateur comme administrateur
async def promote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠ Utilise cette commande en répondant à un message.")
        return

    user_to_promote = update.message.reply_to_message.from_user
    try:
        await chat.promote_member(
            user_id=user_to_promote.id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
        )
        await update.message.reply_text(f"✅ {user_to_promote.first_name} est maintenant administrateur!")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Impossible de promouvoir cet utilisateur.")

# Fonction pour rétrograder un administrateur
async def demote_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠ Utilise cette commande en répondant à un message.")
        return

    user_to_demote = update.message.reply_to_message.from_user
    try:
        await chat.promote_member(
            user_id=user_to_demote.id,
            is_anonymous=False,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
        )
        await update.message.reply_text(f"✅ {user_to_demote.first_name} a été rétrogradé.")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Impossible de rétrograder cet utilisateur.")

# Fonction pour activer/désactiver des permissions de groupe
async def set_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # Autorisations par défaut : Toutes désactivées
    disable_all = ChatPermissions()
    enable_all = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=True,
        can_invite_users=True,
        can_pin_messages=True,
    )

    if "disable" in context.args:
        try:
            await chat.set_permissions(disable_all)
            await update.message.reply_text("🚫 Toutes les permissions ont été désactivées pour ce groupe.")
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Impossible de désactiver les permissions.")
    elif "enable" in context.args:
        try:
            await chat.set_permissions(enable_all)
            await update.message.reply_text("✅ Toutes les permissions ont été activées pour ce groupe.")
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Impossible d'activer les permissions.")
    else:
        await update.message.reply_text("⚠ Utilisez `/permissions enable` ou `/permissions disable`.")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("promote", promote_admin))
    app.add_handler(CommandHandler("demote", demote_admin))
    app.add_handler(CommandHandler("permissions", set_permissions))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members))
    app.add_handler(CallbackQueryHandler(kick_all, pattern="kick_all"))
    app.add_handler(CallbackQueryHandler(ban_user, pattern="ban_user"))
    app.add_handler(CallbackQueryHandler(list_members, pattern="list_members"))

    print("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
