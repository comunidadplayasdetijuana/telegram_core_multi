from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from telegram.constants import ParseMode
from lib.lib_db import register_user,get_user_config, update_user_config, check_credits


def get_user_info(update: Update):
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else None
    first_name = user.first_name if user.first_name else None
    last_name = user.last_name if user.last_name else None
    return user_id, username, first_name, last_name


def register_handler():
    async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id, username, first_name, last_name = get_user_info(update)

        user_settings = get_user_config(user_id)
        if user_settings:
            await update.message.reply_text("Ya estás registrado. Usa /config para modificar tus datos.")
            return

        # Guardamos los datos del usuario en la base de datos
        nickname = first_name or username or None
        if not nickname:
            await update.message.reply_text("No encontré un nombre. ¿Cómo te gustaría que te llamemos?")
            context.user_data["awaiting_nickname"] = True
            return
        
        # Aquí llamamos a la función para registrar el usuario en la base de datos
        register_user(user_id, username, nickname, first_name, last_name)

        await update.message.reply_text(f"Registro completado, {nickname}. Usa /config para ver o modificar tus datos.")

    async def ask_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if "awaiting_nickname" in context.user_data:
            user_id, _, _, _ = get_user_info(update)
            register_user(user_id, _, update.message.text, _, _)  # Registramos el nickname en la base de datos
            del context.user_data["awaiting_nickname"]
            await update.message.reply_text("Listo! Registro completado. Usa \"/config\" para ver y \"/config set param valor\" modificar los valores.")

    # Devolver los handlers individualmente
    register_cmd_handler = CommandHandler("registrar", register_command)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, ask_nickname)
    
    return register_cmd_handler


def config_handler():
    async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id, _, _, _ = get_user_info(update)

        # Verificamos si el usuario está registrado en la base de datos
        user_settings = get_user_config(user_id)
        if not user_settings:
            await update.message.reply_text("No tienes configuraciones guardadas. Utiliza /registrar primero.")
            return

        args = context.args

        # Si no hay parámetros, mostramos las configuraciones actuales con los nombres modificados
        if not args:
            settings_text = ""
            for key, value in user_settings.items():
                if key == "user_id":
                    settings_text += f"*UserID*: {value}\n"
                elif key == "notifications_enabled":
                    settings_text += f"*Notificaciones*: {'Activadas' if value == 1 else 'Desactivadas'}\n"
                elif key == "phone":
                    settings_text += f"*Telefono*: {value}\n"
                elif key == "contact_userid":
                    settings_text += f"*UserID Alterno*: {value}\n"
                elif key == "first_name":
                    settings_text += f"*Nombre*: {value}\n"
                elif key == "last_name":
                    settings_text += f"*Apellido*: {value}\n"

            await update.message.reply_text(f"*Configuraciones*\n\n{settings_text}\n\nUtiliza \"/config set param valor\" para modificar los valores")
            return

        # Modificar configuración con `/config set <parametro> <valor>`
        if len(args) >= 2 and args[0].lower() == "set":
            param_map = {
                "nombre": "first_name",
                "apellido": "last_name",
                "telefono": "phone",
                "notificaciones": "notifications_enabled",
                "userid_alterno": "contact_userid"
            }

            key = args[1].lower()
            value = " ".join(args[2:])

            # Si el parámetro es reconocido, actualizamos el valor
            if key in param_map:
                db_key = param_map[key]
                
                # Si es un valor booleano (como notifications_enabled), convertimos
                if db_key == "notifications_enabled":
                    value = 1 if value.lower() in ['activadas', 'true', 'yes'] else 0

                update_user_config(user_id, db_key, value)  # Actualizar configuración en la base de datos
                await update.message.reply_text(f"Configuración actualizada: {key} = {value}")
            else:
                await update.message.reply_text("Parámetro no válido. Usa /config para ver los disponibles.")

    return CommandHandler("config", config_command)


def credits_handler():
    async def creditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id, _, _, _ = get_user_info(update)

        # Verificamos si el usuario tiene créditos registrados
        user_settings = get_user_config(user_id)
        if not user_settings:
            await update.message.reply_text("No tienes configuraciones guardadas. Utiliza /registrar primero.")
            return

        # Obtenemos los créditos del usuario
        total_credits = check_credits(user_id)  # Asegúrate de que esta función devuelva el total de créditos

        if total_credits is None:
            await update.message.reply_text("No se han encontrado créditos para este usuario.")
        else:
            await update.message.reply_text(f"Cuentas con un total de *{total_credits:,} créditos*.")  # Usamos coma para formato

    return CommandHandler("creditos", creditos_command)
