# frontend_telegram/bot.py
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

import os
from dotenv import load_dotenv
load_dotenv()

# Mengambil kunci API dari file .env secara aman
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
URL_BACKEND = "http://127.0.0.1:8000/api/research"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya AI Financial Agent Bot.\n"
        "Silakan ketik kode saham yang ingin Anda teliti.\nContoh: `TSLA` atau `NVDA`"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    saham = update.message.text.upper().strip()
    await update.message.reply_text(f"🚀 Memulai analisis paralel untuk saham {saham}...")

    # 1. Panggil FastAPI Backend untuk Mulai Graf
    try:
        res = requests.post(f"{URL_BACKEND}/start", json={"saham_target": saham})
        if res.status_code == 200:
            hasil = res.json()
            thread_id = hasil["thread_id"]
            
            # Simpan data ke memori chat user sementara
            context.user_data["thread_id"] = thread_id
            context.user_data["berita_saham"] = hasil["berita_saham"]

            # 2. Tampilkan hasil interupsi ke pengguna Telegram
            pesan_jeda = (
                f"🛑 *[INTERUPSI HITL]*\n\n"
                f"📊 *Data Harga:* {hasil['harga_saham']}\n\n"
                f"📰 *Data Berita:* {hasil['berita_saham'][:200]}...\n\n"
                f"Apakah Anda menyetujui data ini untuk dilanjutkan ke Manajer Investasi?"
            )
            
            # Buat tombol interaktif di Telegram
            keyboard = [
                [InlineKeyboardButton("✅ Setujui & Lanjutkan", callback_data="approve")],
                [InlineKeyboardButton("❌ Batalkan Proses", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(pesan_jeda, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ Gagal terhubung ke backend server.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Terjadi error: {str(e)}")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    thread_id = context.user_data.get("thread_id")
    action = query.data

    if action == "cancel":
        requests.post(f"{URL_BACKEND}/continue", json={"thread_id": thread_id, "action": "cancel"})
        await query.edit_message_text(text="❌ Analisis dibatalkan oleh pengguna.")
        return

    await query.edit_message_text(text="👨‍💼 Manajer Investasi sedang merumuskan laporan akhir di server...")

    # 3. Panggil FastAPI Backend untuk Meneruskan Graf
    try:
        payload = {"thread_id": thread_id, "action": "approve"}
        res = requests.post(f"{URL_BACKEND}/continue", json=payload)
        
        if res.status_code == 200:
            laporan = res.json().get("laporan_akhir", "Gagal merangkum laporan.")
            await query.message.reply_text(f"📜 *LAPORAN INVESTASI AKHIR:*\n\n{laporan}")
        
        else:
            await query.message.reply_text("❌ Gagal mengambil laporan akhir dari server.")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Error saat melanjutkan graf: {str(e)}")

def main():
    app_bot = Application.builder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_bot.add_handler(CallbackQueryHandler(handle_button))
    
    print("🤖 Telegram Bot AI Agent Aktif... Tekan Ctrl+C untuk mematikan.")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
