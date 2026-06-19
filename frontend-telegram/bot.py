# frontend-telegram/bot.py
import logging
import os
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# === PERBAIKAN: Menggunakan URL Backend Render yang Sudah Live ===
URL_BACKEND = "https://agentic-ai-project-backend.onrender.com/api/research"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Saya AI Financial Agent Bot.\n"
        "Silakan ketik kode saham yang ingin Anda teliti.\nContoh: `TSLA` atau `NVDA`"
    )
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    saham = update.message.text.upper().strip()
    
    # Validasi: Kode saham umumnya hanya berupa huruf dan panjangnya 3-5 karakter
    if not saham.isalpha() or len(saham) < 4 or len(saham) > 4:
        await update.message.reply_text("⚠️ Kode saham tidak valid. Silakan masukkan kode saham yang benar (Contoh: BBCA, NVDA, TSLA).")
        return
        
    await update.message.reply_text(f"🚀 Memulai analisis paralel untuk saham {saham}...")

    try:
        res = requests.post(f"{URL_BACKEND}/start", json={"saham_target": saham})
        if res.status_code == 200:
            hasil = res.json()
            thread_id = hasil["thread_id"]

            pesan_jeda = (
                f"🛑 *[INTERUPSI HITL]*\n\n"
                f"📊 *Data Harga:* {hasil['harga_saham']}\n\n"
                f"📰 *Data Berita:* {hasil['berita_saham'][:200]}...\n\n"
                f"Apakah Anda menyetujui data ini untuk dilanjutkan ke Manajer Investasi?"
            )
            
            # === PERBAIKAN: Menyimpan aksi dan thread_id ke dalam callback_data agar tidak tertukar antar user ===
            keyboard = [
                [InlineKeyboardButton("✅ Setujui & Lanjutkan", callback_data=f"approve:{thread_id}")],
                [InlineKeyboardButton("❌ Batalkan Proses", callback_data=f"cancel:{thread_id}")]
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
    
    # === PERBAIKAN: Membongkar data aksi dan thread_id dari callback_data ===
    data_tombol = query.data.split(":")
    action = data_tombol[0]
    thread_id = data_tombol[1]

    if action == "cancel":
        try:
            requests.post(f"{URL_BACKEND}/continue", json={"thread_id": thread_id, "action": "cancel"})
        except Exception:
            pass
        await query.edit_message_text(text="❌ Analisis dibatalkan oleh pengguna.")
        return

    await query.edit_message_text(text="👨‍💼 Manajer Investasi sedang merumuskan laporan akhir di server...")

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
