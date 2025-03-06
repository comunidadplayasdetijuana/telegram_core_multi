from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from datetime import datetime
from lib.lib_telegram_usr_settings import get_user_info
from lib.lib_db import insert_referral_code
import hashlib


def generate_referral_code(user_id, length=18):
    """Genera un código de referencia único utilizando el user_id y la hora actual."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_input = f"{user_id}{timestamp}".encode('utf-8') 
    hash_object = hashlib.sha256(hash_input)
    code = hash_object.hexdigest()[:length] 
    return code


def gen_ref_handler():
    async def gen_ref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id, _, _, _ = get_user_info(update)
        referral_code = generate_referral_code(user_id)

        insert_referral_code(user_id, referral_code)

        await update.message.reply_text(f"Tu código de referencia es: {referral_code}")

    return CommandHandler("gen_ref", gen_ref)