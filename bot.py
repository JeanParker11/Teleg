import logging
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
)
from config import TOKEN

# Configuration du logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Liste pour stocker les membres (cela sera mis à jour avec des événements)
group_members = []

# Fonction pour ajouter un membre à la liste
async def add_member_to_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Si ce n'est pas un message de commande ou un message de bot
    if user.id not in [member.user.id for member in group_members]:
        group_members.append(update.message)

# Fonction pour taguer et bannir un utilisateur
async def random_tag_and_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # Récupérer les administrateurs du groupe
    administrators = await chat.get_administrators()

    # Filtrer les membres non-administrateurs
    non_admin_members = [member for member in group_members if member.user.id not in [admin.user.id for admin in administrators]]

    if not non_admin_members:
        await update.message.reply_text("⚠ Il n'y a plus de membres non-administrateurs à bannir.")
        return

    # Choisir un membre au hasard parmi les membres non-administrateurs
    random_member = random.choice(non_admin_members)

    # Bannir l'utilisateur
    await chat.ban_member(random_member.user.id)
    
    # Mentionner le membre dans le message
    await update.message.reply_text(f"🎉 @ {random_member.user.username}, tu es tagué(e) et banni(e) !")

    # Simuler un processus continu : bannir un autre membre après un délai
    if len(non_admin_members) > 1:
        await random_tag_and_ban(update, context)

# Fonction de démarrage
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Utilisez la commande /banall pour taguer et bannir un membre non-admin."
    )

# Commande pour lancer le processus de ban
async def ban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔨 Début du processus de bannissement de tous les membres non-admins...")

    # Lancer la fonction pour bannir un membre
    await random_tag_and_ban(update, context)

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Ajout des handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("banall", ban_all))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, add_member_to_list))

    logger.info("🚀 Bot démarré...")
    app.run_polling()

if __name__ == "__main__":
    main()
