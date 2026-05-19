import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Miran Bey Konakları", page_icon="🏛️", layout="wide")

# --- GOOGLE SHEETS BAĞLANTISI ---
# Bu kütüphane Secrets kısmına yazdığın linki otomatik olarak okur
conn = st.connection("gsheets", type=GSheetsConnection)

# --- VERİLERİ BULUTTAN ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=5) # 5 saniyede bir verileri tazeler, böylece her şey anlık görünür
def verileri_cek(sayfa_adi):
    try:
        return conn.read(worksheet=sayfa_adi)
    except Exception as e:
        st.error(f"Veri çekme hatası ({sayfa_adi}): {e}")
        return pd.DataFrame()

# --- ÜST BAŞLIK VE LOGO ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏛️ Miran Bey Konakları Site Yönetimi</h1>", unsafe_allow_html=True)

# --- GİRİŞ SİSTEMİ ---
with st.sidebar:
    st.markdown("### 🔐 Yönetim Paneli")
    admin_sifre = st.text_input("Yönetici Şifresi", type="password")
    is_admin = (admin_sifre == "miran3458") # GÜNCEL ŞIFRENIZ 🔑
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
# 1. MENÜ: GÜNCEL SİTE BÜTÇESİ
# ==========================================
if menu == "📊 Güncel Site Bütçesi":
    st.subheader("📊 Güncel Site Bütçesi ve Harcamalar")
    
    df_butce = verileri_cek("butce")
    
    # Kasa bakiyesini harcamalara göre dinamik hesaplayabiliriz ya da el ile güncelleyebiliriz.
    # Kolaylık olsun diye toplam kasayı doğrudan Google Sheets'te tutmak yerine harcamalardan düşebiliriz.
    # Ancak manuel kasa ayarını korumak için toplam bütçeyi 50,000 TL başlangıç kabul edip harcamaları düşüyoruz.
    baslangic_kasa = 50000.0
    toplam_harcama = 0.0
    if not df_butce.empty and "Tutar" in df_butce.columns:
        toplam_harcama = df_butce["Tutar"].astype(float).sum()
    
    guncel_kasa_bakiyesi = baslangic_kasa - toplam_harcama
    st.metric(label="💰 Kasa Toplam Bakiyesi (Tahmini)", value=f"{guncel_kasa_bakiyesi:,.2f} TL")
    st.caption("Not: Başlangıç kasası 50.000 TL baz alınarak harcamalar düşülmektedir.")

    if is_admin:
        st.markdown("### ⚙️ Yönetici Bütçe Düzenleme")
        st.markdown("**Yeni Harcama Kaydı Ekle**")
        h_tarih = st.date_input("Harcama Tarihi")
        h_aciklama = st.text_input("Harcama Kalemi / Açıklama (Örn: Asansör Bakımı)")
        h_tutar = st.number_input("Harcama Tutarı (TL)", min_value=0.0)
        
        if st.button("Harcamayı Kaydet ve Google Sheets'e Yaz"):
            if h_aciklama and h_tutar > 0:
                yeni_harcama = pd.DataFrame([{"Tarih": str(h_tarih), "Açıklama": h_aciklama, "Tutar": h_tutar, "Tür": "Gider"}])
                df_butce_yeni = pd.concat([df_butce, yeni_harcama], ignore_index=True)
                
                # Google Sheets'e yükle
                conn.update(worksheet="butce", data=df_butce_yeni)
                st.success("Harcama başarıyla Google E-Tablolar'a kaydedildi!")
                st.cache_data.clear()
                st.rerun()

    st.markdown("#### 📜 Yapılan Harcamalar Listesi")
    if not df_butce.empty and len(df_butce) > 0:
        df_butce = df_butce.sort_values(by="Tarih", ascending=False).reset_index(drop=True)
        
        if is_admin:
            st.caption("Yönetici Girişi Aktif: Hatalı harcamaları sildiğinizde Google Sheets anında güncellenir.")
            for idx, row in df_butce.iterrows():
                col_tarih, col_aciklama, col_tutar, col_buton = st.columns([2, 5, 3, 2])
                with col_tarih: st.write(str(row['Tarih']))
                with col_aciklama: st.write(str(row['Açıklama']))
                with col_tutar: st.write(f"{float(row['Tutar']):,.2f} TL")
                with col_buton:
                    if st.button("❌ İptal Et/Sil", key=f"del_h_{idx}"):
                        df_butce_guncel = df_butce.drop(idx)
                        conn.update(worksheet="butce", data=df_butce_guncel)
                        st.success("Harcama silindi ve buluttan kaldırıldı!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.dataframe(df_butce, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz yapılmış bir harcama kaydı bulunmuyor.")

# ==========================================
# 2. MENÜ: DUYURULAR
# ==========================================
elif menu == "📢 Duyurular":
    st.subheader("📢 Yönetimden Duyurular")
    df_duyuru = verileri_cek("duyurular")
    
    if is_admin:
        st.markdown("### ⚙️ Yeni Duyuru Paylaş")
        d_baslik = st.text_input("Duyuru Başlığı")
        d_icerik = st.text_area("Duyuru Metni")
        if st.button("Duyuruyu Yayınla"):
            if d_baslik and d_icerik:
                yeni_d = pd.DataFrame([{"Tarih": simdi.strftime("%d.%m.%Y"), "Başlık": d_baslik, "İçerik": d_icerik}])
                df_duyuru_yeni = pd.concat([df_duyuru, yeni_d], ignore_index=True)
                
                conn.update(worksheet="duyurular", data=df_duyuru_yeni)
                st.success("Duyuru Google Sheets'e yazıldı ve yayınlandı!")
                st.cache_data.clear()
                st.rerun()

    if not df_duyuru.empty and len(df_duyuru) > 0:
        for idx, row in df_duyuru.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"### 📌 {row['Başlık']}")
                st.caption(f"📅 Yayınlanma Tarihi: {row['Tarih']}")
                st.write(row['İçerik'])
                if is_admin:
                    if st.button(f"❌ Bu Duyuruyu Sil", key=f"del_d_{idx}"):
                        df_duyuru_guncel = df_duyuru.drop(idx)
                        conn.update(worksheet="duyurular", data=df_duyuru_guncel)
                        st.success("Duyuru silindi!")
                        st.cache_data.clear()
                        st.rerun()
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
        if arama:
            df_goster = df_aidat[df_aidat.astype(str).apply(lambda x: x.str.contains(arama, case=False)).any(axis=1)]
        else:
            df_goster = df_aidat
        st.dataframe(df_goster, use_container_width=True, hide_index=True)
    else:
        st.info("Aidat tablosu şu an boş.")
    
    if is_admin:
        st.markdown("### ⚙️ Yönetici Veri Girişi / Düzenleme")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Yeni Satır (Borç/Aidat) Ekle**")
            a_blok = st.selectbox("Blok", ["A", "B", "C"])
            a_daire = st.text_input("Daire No")
            a_sakin = st.text_input("Sakin Adı Soyadı")
            a_donem = st.text_input("Dönem (Örn: Haziran 2026)")
            a_durum = st.selectbox("Durum", ["Ödendi", "Gecikti"])
            
            if st.button("Tabloya Ekle"):
                if a_daire and a_sakin and a_donem:
                    yeni_a = pd.DataFrame([{"Blok": a_blok, "Daire": a_daire, "Sakin": a_sakin, "Dönem": a_donem, "Durum": a_durum}])
                    df_aidat_yeni = pd.concat([df_aidat, yeni_a], ignore_index=True)
                    conn.update(worksheet="aidat", data=df_aidat_yeni)
                    st.success("Veri Google Sheets'e başarıyla işlendi!")
                    st.cache_data.clear()
                    st.rerun()
                    
        with col2:
            st.markdown("**Mevcut Satırı Sil**")
            if not df_aidat.empty and len(df_aidat) > 0:
                silinecek_idx = st.selectbox("Silmek istediğiniz kaydı seçin:", 
                                             options=range(len(df_aidat)), 
                                             format_func=lambda x: f"{df_aidat.iloc[x]['Blok']} Blok D:{df_aidat.iloc[x]['Daire']} - {df_aidat.iloc[x]['Sakin']} ({df_aidat.iloc[x]['Dönem']})")
                if st.button("Seçili Kaydı Sil"):
                    df_aidat_guncel = df_aidat.drop(silinecek_idx)
                    conn.update(worksheet="aidat", data=df_aidat_guncel)
                    st.success("Kayıt buluttan silindi!")
                    st.cache_data.clear()
                    st.rerun()

# ==========================================
# 4. MENÜ: ARIZA BİLDİR
# ==========================================
elif menu == "🛠️ Arıza Bildir":
    st.subheader("🛠️ Arıza ve Talep Bildirim Formu")
    df_ariza = verileri_cek("arizalar")
    
    st.markdown("### 📋 Yeni Arıza Bildirim Formu")
    ari_daire = st.text_input("Blok ve Daireniz (Örn: A Blok Daire 5)")
    ari_baslik = st.text_input("Arıza Başlığı (Örn: Asansör Bozuk)")
    ari_aciklama = st.text_area("Arıza Detayı ve Açıklaması")
    
    if st.button("Bildirimi Yönetime Gönder"):
        if ari_daire and ari_baslik and ari_aciklama:
            yeni_ariza = pd.DataFrame([{"Tarih": simdi.strftime("%d.%m.%Y %H:%M"), "Daire": ari_daire, "Başlık": ari_baslik, "Açıklama": ari_aciklama, "Durum": "Beklemede"}])
            df_ariza_yeni = pd.concat([df_ariza, yeni_ariza], ignore_index=True)
            
            conn.update(worksheet="arizalar", data=df_ariza_yeni)
            st.success("Bildiriminiz anında yönetimin veri tabanına ulaştı. Teşekkür ederiz!")
            st.cache_data.clear()
            st.rerun()
            
    if is_admin:
        st.write("---")
        st.markdown("### 📬 Gelen Arıza / Talep Kutusu (Sadece Yönetici)")
        
        if not df_ariza.empty and len(df_ariza) > 0:
            for idx, row in df_ariza.iterrows():
                with st.expander(f"🔴 {row['Tarih']} - {row['Daire']} : {row['Başlık']}"):
                    st.markdown(f"**Açıklama:** {row['Açıklama']}")
                    st.markdown(f"**Mevcut Durum:** {row['Durum']}")
                    
                    if st.button("✅ Çözüldü Olarak İşaretle/Sil", key=f"solve_{idx}"):
                        df_ariza_guncel = df_ariza.drop(idx)
                        conn.update(worksheet="arizalar", data=df_ariza_guncel)
                        st.success("Talep çözüldü olarak işaretlendi ve kaldırıldı!")
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.info("Gelen herhangi bir arıza bildirilmedi.")
