# backend/server.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from main import app  # Mengimpor graf LangGraph Anda dari main.py
from fastapi.middleware.cors import CORSMiddleware


server = FastAPI(title="LangGraph API for Telegram Bot")

# Tambahkan CORS agar frontend Streamlit Anda bisa memanggil API ini
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Bisa diganti dengan URL Streamlit Anda nanti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. MODEL DATA (Skema JSON untuk Request)
class StartRequest(BaseModel):
    saham_target: str

class ContinueRequest(BaseModel):
    thread_id: str
    action: str  # "approve" atau "cancel"
    harga_koreksi: Optional[str] = None
    catatan_berita: Optional[str] = None


# 2. ENDPOINT: MEMULAI RISET SAHAM
@server.post("/api/research/start")
def start_research(data: StartRequest):
    """Memicu LangGraph berjalan paralel sampai terkena interupsi sebelum Manajer Investasi"""
    # Gunakan format thread_id yang konsisten
    thread_id = f"tg_sesi_{data.saham_target.lower()}"
    config_graf = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Jalankan graf pertama kali (akan otomatis berhenti tepat sebelum manajer_investasi)
        app.invoke({"saham_target": data.saham_target.upper()}, config=config_graf)
        
        # Ambil kondisi data terakhir di memori setelah graf dijeda
        snapshot = app.get_state(config_graf)
        
        return {
            "thread_id": thread_id,
            "status": "interrupted",
            "harga_saham": snapshot.values.get("harga_saham", "Tidak ada data harga."),
            "berita_saham": snapshot.values.get("berita_saham", "Tidak ada berita.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memulai graf: {str(e)}")


# 3. ENDPOINT: MENERUSKAN ATAU MEMBATALKAN GRAF
@server.post("/api/research/continue")
def continue_research(data: ContinueRequest):
    """Meneruskan alur graf setelah manusia menekan tombol di Telegram"""
    config_graf = {"configurable": {"thread_id": data.thread_id}}
    
    if data.action == "cancel":
        return {"status": "cancelled", "message": "Proses riset dibatalkan."}
        
    try:
        # Menyuntikkan koreksi harga jika dikirim oleh bot
        if data.harga_koreksi:
            app.update_state(config_graf, {"harga_saham": f"[Koreksi Manusia]: {data.harga_koreksi}"})
            
        # Menyuntikkan catatan berita tambahan jika ada
        if data.catatan_berita:
            snapshot = app.get_state(config_graf)
            berita_lama = snapshot.values.get("berita_saham", "")
            berita_baru = f"{berita_lama}\n\n[Catatan Tambahan Manusia]: {data.catatan_berita}"
            app.update_state(config_graf, {"berita_saham": berita_baru})
            
        # Lanjutkan eksekusi graf yang tertunda (kirim None karena melanjutkan state)
        status_akhir = app.invoke(None, config=config_graf)
        
        return {
            "status": "completed",
            "laporan_akhir": status_akhir.get("laporan_akhir", "Gagal menyusun laporan.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melanjutkan graf: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Menjalankan server lokal pada port 8000
    # Ditambahkan log_level="info" agar uvicorn wajib mencetak laporan aktivitas
    uvicorn.run("server:server", host="127.0.0.1", port=8000, log_level="info", reload=True)

