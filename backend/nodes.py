# nodes.py
import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from state import FinancialState
from tools import ambil_harga_saham, cari_berita_keuangan

# Inisialisasi LLM di sini
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

def node_analis_angka(state: FinancialState):
    print("🤖 [Analis Angka] Sedang bekerja...")
    ticker = state.get("saham_target")
    hasil_harga = ambil_harga_saham(ticker)
    return {"harga_saham": hasil_harga}

def node_analis_berita(state: FinancialState):
    print("🤖 [Analis Berita] Sedang bekerja...")
    ticker = state.get("saham_target")
    berita_mentah = cari_berita_keuangan(f"berita terkini saham {ticker}")

    prompt_sistem = "Kamu adalah analis sentimen media. Tugasmu membuang teks sampah dan merangkum berita menjadi 3 poin sentimen terpenting saja."
    respons = llm.invoke([
        SystemMessage(content=prompt_sistem),
        HumanMessage(content=f"Saring berita mentah berikut:\n{berita_mentah}")
    ])
    return {"berita_saham": respons.content}

def node_manajer_investasi(state: FinancialState):
    print("👨‍💼 [Manajer Investasi] Sedang menyusun laporan akhir...")
    prompt = (
        f"Kamu adalah Manajer Investasi Senior.\n"
        f"Analisis kondisi saham {state['saham_target']}.\n\n"
        f"Data Harga dari Analis: {state['harga_saham']}\n"
        f"Data Berita dari Riset: {state['berita_saham']}\n\n"
        f"Berikan kesimpulan (Positif/Negatif/Netral) dan tindakan dalam format Markdown "
        f"yang memuat Ringkasan Angka, Sentimen Berita, dan Rekomendasi Anda."
    )
    respons = llm.invoke([HumanMessage(content=prompt)])
    return {"laporan_akhir": respons.content}

def cek_validitas_saham(state: FinancialState) -> Literal["lanjut_analisis", "stop_eror"]:
    text_harga = state.get("harga_saham", "")
    if "tidak ditemukan" in text_harga or "Eror" in text_harga:
        print("\n🛑 [Sistem Guardrail] Emiten tidak valid! Memotong jalur langsung ke END...")
        return "stop_eror"
    
    print("\n✅ [Sistem Guardrail] Saham valid. Meneruskan ke Manajer Investasi...")
    return "lanjut_analisis"
