# tools.py
import yfinance as yf
from duckduckgo_search import DDGS

def ambil_harga_saham(ticker: str) -> str:
    try:
        saham = yf.Ticker(ticker.strip().upper())
        data = saham.history(period="1d")
        if not data.empty:
            return f"Harga terakhir untuk {ticker} adalah {round(data['Close'].iloc[-1], 2)} USD."
        return f"Simbol {ticker} tidak ditemukan."
    except Exception as e:
        return f"Eror data saham: {str(e)}"

def cari_berita_keuangan(kata_kunci: str) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(kata_kunci, max_results=3):
                results.append(f"Judul: {r.get('title')}\nKonteks: {r.get('body')}\n")
        return "\n---\n".join(results)
    except Exception as e:
        return f"Gagal mencari berita: {str(e)}"
