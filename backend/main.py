# main.py
from dotenv import load_dotenv
load_dotenv()  # Harus di urutan paling atas sebelum impor node yang butuh API Key

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Impor komponen dari file lain
from state import FinancialState
from nodes import node_analis_angka, node_analis_berita, node_manajer_investasi, cek_validitas_saham

# 1. ORKESTRASI GRAF
workflow = StateGraph(FinancialState)

workflow.add_node("analis_angka", node_analis_angka)
workflow.add_node("analis_berita", node_analis_berita)
workflow.add_node("manajer_investasi", node_manajer_investasi)

workflow.add_edge(START, "analis_angka")
workflow.add_edge(START, "analis_berita")

workflow.add_conditional_edges(
    "analis_angka",
    cek_validitas_saham,
    {
        "lanjut_analisis": "manajer_investasi",
        "stop_eror": END
    }
)

workflow.add_edge("analis_berita", "manajer_investasi")
workflow.add_edge("manajer_investasi", END)

memory = MemorySaver()
app = workflow.compile(
    checkpointer=memory, 
    interrupt_before=["manajer_investasi"]
)

# 2. RUN PROGRAM (HITL CLI)
if __name__ == "__main__":
    print("\n--- SISTEM MULTI-AGENT LANGGRAPH AKTIF (DENGAN HITL + EDIT) ---")
    saham = input("Masukkan kode saham yang ingin diteliti (contoh: TSLA, NVDA): ")
    
    input_awal = {"saham_target": saham}
    opsi_graf = {"configurable": {"thread_id": f"sesi_{saham.lower()}_hitl"}}
    
    print(f"\n🚀 Memulai eksekusi paralel (Analis Angka & Berita)...")
    app.invoke(input_awal, config=opsi_graf)
    
    snapshot = app.get_state(opsi_graf)
    
    if snapshot.next:
        print(f"\n🛑 [INTERUPSI HITL] Graf dijeda sebelum masuk ke Node: {snapshot.next}")
        print("-" * 60)
        
        harga_saat_ini = snapshot.values.get('harga_saham', '')
        berita_saat_ini = snapshot.values.get('berita_saham', '')
        
        print(f"📊 DATA HARGA DARI ANALIS : {harga_saat_ini}")
        cuplikan_berita = berita_saat_ini[:200] + "..." if berita_saat_ini else "Tidak ada berita."
        print(f"📰 DATA BERITA DARI RISET : {cuplikan_berita}")
        print("-" * 60)
        
        print("\nPilih tindakan Anda:")
        print("[1] Setujui dan langsung lanjutkan")
        print("[2] Edit data harga saham")
        print("[3] Edit/tambah catatan berita")
        print("[4] Batalkan eksekusi")
        pilihan = input("Masukkan angka pilihan (1-4): ")
        
        if pilihan == "1":
            print("\n🟢 Langsung melanjutkan grafik untuk Manajer Investasi...\n")
            status_akhir = app.invoke(None, config=opsi_graf)
            print("\n================ LAPORAN AKHIR ================")
            print(status_akhir.get("laporan_akhir"))
            
        elif pilihan == "2":
            harga_baru = input(f"\nHarga saat ini: '{harga_saat_ini}'.\nMasukkan harga koreksi Anda: ")
            app.update_state(opsi_graf, {"harga_saham": f"[Koreksi Manusia]: {harga_baru}"})
            print("✅ Data harga berhasil diperbarui di memori.\n🟢 Melanjutkan grafik...")
            status_akhir = app.invoke(None, config=opsi_graf)
            print("\n================ LAPORAN AKHIR (DATA DIKOREKSI) ================")
            print(status_akhir.get("laporan_akhir"))
            
        elif pilihan == "3":
            catatan_berita = input("\nTambahkan konteks/sentimen berita tambahan dari Anda: ")
            berita_baru = f"{berita_saat_ini}\n\n[Catatan Tambahan Manusia]: {catatan_berita}"
            app.update_state(opsi_graf, {"berita_saham": berita_baru})
            print("✅ Data berita berhasil diperbarui di memori.\n🟢 Melanjutkan grafik...")
            status_akhir = app.invoke(None, config=opsi_graf)
            print("\n================ LAPORAN AKHIR (DATA DIKOREKSI) ================")
            print(status_akhir.get("laporan_akhir"))
            
        else:
            print("\n❌ Eksekusi dibatalkan oleh pengguna.")
