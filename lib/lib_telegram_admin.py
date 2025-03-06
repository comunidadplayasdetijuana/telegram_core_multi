from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from lib.lib_db import add_credit, check_credits, remove_last_credit, log_user_action, log_action
from datetime import datetime, timedelta

# Define the admin ID(s)
ADMIN_IDS = [123456789,7548760980]  

# Verifica si el usuario es admin
def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_user_info(update: Update):
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else None
    first_name = user.first_name if user.first_name else None
    last_name = user.last_name if user.last_name else None
    return user_id, username, first_name, last_name

def credit_handler() -> CommandHandler:
    async def credit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if not is_admin(user_id):
            await update.message.reply_text("No tienes permisos para realizar esta acción.")
            return

        print(f"Argumentos recibidos: {context.args}")
        if len(context.args) < 1:
            await update.message.reply_text("Uso: /credit {add|check|remove} {userid} [amount] [note]")
            return

        command = context.args[0].lower()

        try:
            if command == "add":
                if len(context.args) < 3:
                    await update.message.reply_text("Uso: /credit add {userid} {amount} {note}")
                    return

                target_user_id, amount, *note = context.args[1:]
                amount = int(amount)
                note = " ".join(note) if note else None

                print(f"User ID: {target_user_id}")
                print(f"Monto: {amount}")
                print(f"Nota: {note}")

                add_credit(target_user_id, amount, note)
                log_action(user_id, f"Credits: +{amount}", note)
                await update.message.reply_text(f"{amount} credits added to {target_user_id}. {'Note: ' + note if note else ''}")

            elif command == "check":
                if len(context.args) < 2:
                    await update.message.reply_text("Uso: /credit check {userid}")
                    return

                target_user_id = context.args[1]
                total_credits = check_credits(target_user_id)
                total_credits_formatted = f"{total_credits:,}"
                await update.message.reply_text(f"El usuario {target_user_id} tiene {total_credits_formatted} créditos.")


            elif command == "remove":
                if len(context.args) < 2:
                    await update.message.reply_text("Uso: /credit remove {userid}")
                    return

                target_user_id = context.args[1]
                date, amount = remove_last_credit(target_user_id)

                if date and amount:
                    log_action(user_id, f"Removed {amount} credits from {target_user_id} on {date}")
                    await update.message.reply_text(f"Se eliminaron {amount} créditos de {target_user_id} el {date}.")
                else:
                    await update.message.reply_text(f"No hay registros de crédito para el usuario {target_user_id}.")


            else:
                await update.message.reply_text("Comando no reconocido. Uso: /credit {add|check|remove} {userid} [amount] [note]")

        except ValueError as e:
            print(f"Error de conversión: {e}")
            await update.message.reply_text("Error: Asegúrate de que el monto sea un número válido.")

        except Exception as e:
            print(f"Error inesperado: {e}")
            await update.message.reply_text(f"Ocurrió un error: {str(e)}")

    return CommandHandler("credit", credit)


def ban_handler() -> CommandHandler:
    async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if not is_admin(user_id):
            await update.message.reply_text("No tienes permisos para realizar esta acción.")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Uso: /ban {userid} {tiempo} {motivo}")
            return
        
        target_user_id = context.args[0]
        duration = context.args[1]
        reason = " ".join(context.args[2:]) if len(context.args) > 2 else "Violación de reglas"
        
        start_date = datetime.now()
        try:
            if duration.isdigit():
                end_date = start_date + timedelta(hours=int(duration))
            else:
                unit = duration[-1].lower()
                num = duration[:-1]
                
                if not num.isdigit():
                    raise ValueError("Formato de tiempo inválido")

                num = int(num)
                
                if unit == "w":
                    end_date = start_date + timedelta(weeks=num)
                elif unit == "m":
                    end_date = start_date + timedelta(days=num * 30)
                elif unit == "y":
                    end_date = start_date + timedelta(days=num * 365)
                elif unit == "d":
                    end_date = None  # Ban permanente
                else:
                    raise ValueError("Formato de tiempo inválido")
            
            end_date_str = end_date.strftime("%Y-%m-%d %I:%M %p") if end_date else "Permanente"
            start_date_str = start_date.strftime("%Y-%m-%d %I:%M %p")

            log_user_action(target_user_id, "ban", reason, start_date_str, end_date_str)
            log_action(user_id, f"Banned user {target_user_id} until {end_date_str} for: {reason}")
            
            await update.message.reply_text(f"Usuario {target_user_id} ha sido baneado hasta {end_date_str}. Motivo: {reason}")

        except ValueError:
            await update.message.reply_text("Formato de tiempo inválido. Usa horas o sufijos: w=semana, m=mes, y=año, d=permanente.")
    
    return CommandHandler("ban", ban)



def message_handler() -> CommandHandler:
    async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id
        if not is_admin(user_id):
            await update.message.reply_text("No tienes permisos para realizar esta acción.")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Uso: /message {userid} {text}")
            return
        
        user_id, *message = context.args
        message = " ".join(message)
        
        await context.bot.send_message(chat_id=user_id, text=message)
        log_action(update, f"Sent message to {user_id}: {message}")
        await update.message.reply_text(f"Mensaje enviado a {user_id}.")
    
    return CommandHandler("message", send_message, filters=None)
