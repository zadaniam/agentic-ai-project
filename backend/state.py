# state.py
from typing import Optional, TypedDict

class FinancialState(TypedDict):
    saham_target: str
    harga_saham: Optional[str]
    berita_saham: Optional[str]
    laporan_akhir: Optional[str]
