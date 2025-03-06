import os
import hashlib
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler 


ASK_PROBLEM, CONFIRMATION = range(2)


def start_handler() -> CommandHandler:
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("""Bienvenido al Servicio Idx, utiliza el comando /cmds para ver los comandos disponibles.""")

    return CommandHandler("start", start_command)

def cmds_handler() -> CommandHandler:
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
    "Comandos generales disponibles:\n"
    "/start\n"
    "/ayuda\n"
    "/cmds\n\n"


    "Comandos para usuarios disponibles:\n"
    "/registrar\n"
    "/config\n"
    "/gen_ref\n"
    "/creditos\n"
)


    return CommandHandler("cmds", help_command)


def help_handler():
    async def start_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Por favor, describe el problema o la ayuda que necesitas:")
        return ASK_PROBLEM

    async def ask_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['problem'] = update.message.text
        keyboard = [["Sí", "No"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(f"Confirmas esta solicitud?\n\n{update.message.text}", reply_markup=reply_markup)
        return CONFIRMATION

    async def confirm_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text.lower() == "sí":
            print(f"Guardando en SQL: Usuario {update.message.from_user.id}, Problema: {context.user_data['problem']}")
            await update.message.reply_text("Tu solicitud ha sido enviada.")
        else:
            await update.message.reply_text("Solicitud cancelada.")
        return ConversationHandler.END

    return ConversationHandler(
        entry_points=[CommandHandler("ayuda", start_help)],
        states={
            ASK_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_problem)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_request)],
        },
        fallbacks=[],
    )


def photo_handler() -> MessageHandler:
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        photo = update.message.photo[-1]
        file_id = photo.file_id.encode()

        file_hash = hashlib.sha256(file_id).hexdigest()[:16]
        filename = f"{file_hash}.jpg"

        user_dir = f"media/{user_id}"
        os.makedirs(user_dir, exist_ok=True)

        photo_file = await photo.get_file()
        photo_file.download(os.path.join(user_dir, filename))

    return MessageHandler(filters.PHOTO, handle_photo)



