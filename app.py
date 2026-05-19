import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Miran Bey Konakları", page_icon="🏛️", layout="wide")

# --- GOOGLE DRIVE (SHEETS) BAĞLANTI AYARI ---
# Senin Google E-Tablonun benzersiz kimliği
SHEET_ID = "1RFz1DlYbdAHsPbCMc2UYF53_j2xmo1DyJ1_ks6IgrJw"

@st.cache_data(ttl=2) # Verileri her 2 saniyede bir tazeler, Drive'da yaptığın değişiklik anında yansır
def verileri_cek(sayfa_adi):
    # Google Drive'dan ilgili sekmeyi CSV formatında çeken güvenli link
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sayfa_adi}"
    try:
        df = pd.read_csv(url)
        # Eğer Google Sheets sekmesi tamamen boşsa hata vermemesi için şablon oluşturuyoruz
        if df.empty:
            if sayfa_adi == "butce": return pd.DataFrame(columns=["Tarih", "Açıklama", "Tutar", "Tür"])
            if sayfa_adi == "duyurular": return pd.DataFrame(columns=["Tarih", "Başlık", "İçerik"])
            if sayfa_adi == "aidat": return pd.DataFrame(columns=["Blok", "Daire", "Sakin", "Dönem", "Durum"])
            if sayfa_adi == "arizalar": return pd.DataFrame(columns=["Tarih", "Daire", "Başlık", "Açıklama", "Durum"])
        return df
    except Exception as e:
        st.error(f"Google Drive Bağlantı Hatası ({sayfa_adi}): {e}")
        return pd.DataFrame()

def veriyi_guncelle_mesaji():
    st.info("💡 **Yönetici Notu:** Bu sayfadaki tüm veriler doğrudan senin Google Drive'ındaki 'Miran Bey Konaklari Data' dosyasından okunmaktadır. Yeni veri eklemek, silmek veya düzeltmek için doğrudan Google Drive'daki Excel tablonu kullanabilirsin. Yaptığın değişiklikler buraya anında yansır!")

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
saat = kalan_sure.seconds // 3600
dakika = (kalan_sure.seconds % 3600) // 60

st.info(f"⏳ **Bir Sonraki Aidat Son Ödeme Tarihine Kalan Süre:** {gun} Gün, {saat} Saat, {dakika} Dakika")

# --- 📱 MENÜ SEÇİMİ ---
menu = st.radio(
    "Görüntülemek istediğiniz menüyü seçin:",
    ["📊 Güncel Site Bütçesi", "📢 Duyurular", "💳 Aidat Ödeme Durumu", "🛠️ Arıza Bildir"],
    horizontal=True
)

st.write("---")

# ==========================================
# 1. MENÜ: GÜNCEL SİTE BÜTÇESİ (DRIVE ENTEGRELİ + GELİR-GİDER MOTORU)
# ==========================================
if menu == "📊 Güncel Site Bütçesi":
    st.subheader("📊 Güncel Site Bütçesi ve Harcamalar")
    
    df_butce = verileri_cek("butce")
    
    # İstediğin gibi başlangıç kasası tam olarak 0 (sıfır) abi 🎯
    guncel_kasa_bakiyesi = 0.0
    
    if not df_butce.empty and "Tutar" in df_butce.columns and "Tür" in df_butce.columns:
        # Boş satırları filtrele
        df_butce = df_butce.dropna(subset=["Tutar", "Tür"])
        
        # Google Drive'dan gelen satırları tek tek okuyup bütçeyi hesaplayan motor
        for idx, row in df_butce.iterrows():
            try:
                tutar = float(str(row["Tutar"]).replace(",", ".").strip())
                tur = str(row["Tür"]).strip().lower()
                
                # Tür kısmına girilen veriye göre artı veya eksi yansıtma
                if tur == "gelir":
                    guncel_kasa_bakiyesi += tutar
                elif tur == "gider":
                    guncel_kasa_bakiyesi -= tutar
            except:
                continue

    st.metric(label="💰 Kasa Toplam Bakiyesi", value=f"{guncel_kasa_bakiyesi:,.2f} TL")
    
    if is_admin:
        st.markdown("### ⚙️ Yönetici Bütçe Düzenleme")
        veriyi_guncelle_mesaji()

    st.markdown("#### 📜 Bütçe Hareketleri Listesi (Google Drive'dan Gelen)")
    if not df_butce.empty and len(df_butce) > 0:
        if "Tarih" in df_butce.columns:
            df_butce = df_butce.sort_values(by="Tarih", ascending=False).reset_index(drop=True)
        st.dataframe(df_butce, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz yapılmış bir bütçe hareketi (Gelir/Gider) kaydı bulunmuyor.")

# ==========================================
# 2. MENÜ: DUYURULAR
# ==========================================
elif menu == "📢 Duyurular":
    st.subheader("📢 Yönetimden Duyurular")
    df_duyuru = verileri_cek("duyurular")
    
    if is_admin:
        st.markdown("### ⚙️ Yeni Duyuru Paylaş")
        veriyi_guncelle_mesaji()

    if not df_duyuru.empty and len(df_duyuru) > 0:
        if "Başlık" in df_duyuru.columns:
            df_duyuru = df_duyuru.dropna(subset=["Başlık"])
            for idx, row in df_duyuru.iloc[::-1].iterrows():
                with st.container():
                    st.markdown(f"### 📌 {row['Başlık']}")
                    if "Tarih" in row: st.caption(f"📅 Yayınlanma Tarihi: {row['Tarih']}")
                    if "İçerik" in row: st.write(row['İçerik'])
                    st.markdown("---")
    else:
        st.info("Yayınlanmış aktif bir duyuru bulunmuyor.")

# ==========================================
# 3. MENÜ: AİDAT ÖDEME DURUMU
# ==========================================
elif menu == "💳 Aidat Ödeme Durumu":
    st.subheader("💳 Aidat ve Borç Takip Tablosu")
    
    df_aidat = verileri_cek("aidat")
    
    arama = st.text_input("🔍 Tabloda Ara (Blok, Daire No veya İsim girin):")
    if not df_aidat.empty and len(df_aidat) > 0:
        if "Sakin" in df_aidat.columns:
            df_aidat = df_aidat.dropna(subset=["Sakin"])
        if arama:
            df_goster = df_aidat[df_aidat.astype(str).apply(lambda x: x.str.contains(arama, case=False)).any(axis=1)]
        else:
            df_goster = df_aidat
        st.dataframe(df_goster, use_container_width=True, hide_index=True)
    else:
        st.info("Aidat tablosu şu an boş.")
    
    if is_admin:
        st.markdown("### ⚙️ Yönetici Veri Girişi / Düzenleme")
        veriyi_guncelle_mesaji()

# ==========================================
# 4. MENÜ: ARIZA BİLDİR
# ==========================================
elif menu == "🛠️ Arıza Bildir":
    st.subheader("🛠️ Arıza ve Talep Bildirim Formu")
    df_ariza = verileri_cek("arizalar")
    
    if is_admin:
        st.markdown("### 📬 Gelen Arıza / Talep Kutusu (Sadece Yönetici)")
        if not df_ariza.empty and len(df_ariza) > 0:
            if "Başlık" in df_ariza.columns:
                df_ariza = df_ariza.dropna(subset=["Başlık"])
                for idx, row in df_ariza.iterrows():
                    with st.expander(f"🔴 {row['Tarih']} - {row['Daire']} : {row['Başlık']}"):
                        st.markdown(f"**Açıklama:** {row['Açıklama']}")
                        st.markdown(f"**Mevcut Durum:** {row['Durum']}")
        else:
            st.info("Gelen herhangi bir arıza bildirilmedi.")
    else:
        st.markdown("### 📋 Yeni Arıza Bildirim Formu")
        st.info("💡 Arıza ve taleplerinizi site yönetimine iletmek için lütfen yöneticinizle doğrudan iletişime geçiniz.")
