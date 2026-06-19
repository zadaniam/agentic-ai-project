import streamlit as st
import requests

st.title("📊 AI Financial Agent")

saham = st.text_input("Masukkan kode saham:", "TSLA")

if st.button("🚀 Mulai Analisis"):
    res = requests.post("http://127.0.0.1:8000/api/research/start", 
                       json={"saham_target": saham})
    data = res.json()
    
    # Simpan ke session state
    st.session_state.thread_id = data["thread_id"]
    st.session_state.harga = data["harga_saham"]
    st.session_state.berita = data["berita_saham"]
    st.session_state.fase = "hitl"  # tandai sedang di fase HITL

# Tampilkan HITL hanya jika sedang di fase itu
if st.session_state.get("fase") == "hitl":
    st.warning("🛑 Interupsi HITL — Tinjau data berikut:")
    st.write(f"**Harga:** {st.session_state.harga}")
    st.write(f"**Berita:** {st.session_state.berita[:200]}...")
    
    harga_koreksi = st.text_input("Koreksi harga (kosongkan jika setuju):")
    catatan_berita = st.text_input("Tambah catatan berita (opsional):")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Setujui & Lanjutkan"):
            res = requests.post("http://127.0.0.1:8000/api/research/continue", json={
                "thread_id": st.session_state.thread_id,
                "action": "approve",
                "harga_koreksi": harga_koreksi or None,
                "catatan_berita": catatan_berita or None
            })
            st.session_state.laporan = res.json().get("laporan_akhir")
            st.session_state.fase = "selesai"
    
    with col2:
        if st.button("❌ Batalkan"):
            st.session_state.fase = None
            st.error("Analisis dibatalkan.")

if st.session_state.get("fase") == "selesai":
    st.success("📜 Laporan Investasi Akhir:")
    st.write(st.session_state.laporan)