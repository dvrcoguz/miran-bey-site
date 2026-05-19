import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Miran Bey Konakları", page_icon="🏛️", layout="wide")

# --- GOOGLE SHEETS KESİN ÇÖZÜM BAĞLANTISI ---
SHEET_ID = "1RFz1DlYbdAHsPbCMc2UYF53_j2xmo1DyJ1_ks6IgrJw"

@st.cache_data(ttl=2)
def verileri_cek(sayfa_adi):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sayfa_adi}"
    try:
        df = pd.read_csv(url)
        if df.empty:
            if sayfa_adi == "butce": return pd.DataFrame(columns=["Tarih", "Açıklama", "Tutar", "Tür"])
            if sayfa_adi == "duyurular": return pd.DataFrame(columns=["Tarih", "Başlık", "İçerik"])
            if sayfa_adi == "aidat": return pd.DataFrame(columns=["Blok", "Daire", "Sakin", "Dönem", "Durum"])
            if sayfa_adi == "arizalar": return pd.DataFrame(columns=["Tarih", "Daire", "Başlık", "Açıklama", "Durum"])
        return df
    except Exception as e:
        st.error(f"Bağlantı Hatası ({sayfa_adi}): {e}")
        return pd.DataFrame()

def veriyi_guncelle():
    st.info("💡 Tablo düzenlemelerini (Yeni veri ekleme, silme, düzeltme) doğrudan Google Drive'daki 'Miran Bey Konaklari Data' dosyasından yapabilirsiniz. Buraya anında yansıyacaktır!")

# --- ÜST BAŞLIK VE LOGO ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏛️ Miran Bey Konakları Site Yönetimi</h1>", unsafe_allow_html=True)

# --- GİRİŞ SİSTEMİ ---
with st.sidebar:
    st.markdown("### 🔐 Yönetim Paneli")
    admin_sifre = st.text_input("Yönetici Şifresi", type="password")
    is_admin = (admin_sifre == "miran3458")
    if is_admin:
        st.success("Yönetici olarak giriş yapıldı!")
    elif admin_sifre != "":
        st.error("Hatalı Şifre!")

# --- ⏳ GERİ SAYIM SAYACI ---
simdi = datetime.now()
bu_ay_10 = datetime(simdi.year, simdi.month, 10, 23, 59, 59)

if simdi > bu_ay_10:
    if simdi.month == 12:
        sonraki_ay_10 = datetime(simdi.year + 1, 1, 10, 23, 59, 59)
    else:
        sonraki_ay_10 = datetime(simdi.year, simdi.month + 1, 10, 23, 59, 59)
    hedef_tarih = sonraki_ay_10
else:
    hedef_tarih = bu_ay_10

kalan_sure = hedef_tarih - simdi
gun = kalan_sure.days
saat = kalan_sure.seconds // 3
