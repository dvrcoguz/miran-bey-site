import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Miran Bey Konakları", page_icon="🏛️", layout="wide")

# --- VERİ DOSYALARI KONTROLÜ (Verilerin kaybolmaması için) ---
if not os.path.exists("butce.csv"):
    pd.DataFrame(columns=["Tarih", "Açıklama", "Tutar", "Tür"]).to_csv("butce.csv", index=False)
if not os.path.exists("duyurular.csv"):
    pd.DataFrame(columns=["Tarih", "Başlık", "İçerik"]).to_csv("duyurular.csv", index=False)
if not os.path.exists("aidat.csv"):
    ornek_aidat = pd.DataFrame([
        {"Blok": "A", "Daire": "1", "Sakin": "Ahmet Yılmaz", "Dönem": "Mayıs 2026", "Durum": "Ödendi"},
        {"Blok": "B", "Daire": "5", "Sakin": "Mehmet Demir", "Dönem": "Mayıs 2026", "Durum": "Gecikti"},
        {"Blok": "C", "Daire": "12", "Sakin": "Ayşe Kaya", "Dönem": "Mayıs 2026", "Durum": "Ödendi"}
    ])
    ornek_aidat.to_csv("aidat.csv", index=False)
if not os.path.exists("arizalar.csv"):
    pd.DataFrame(columns=["Tarih", "Daire", "Başlık", "Açıklama", "Durum"]).to_csv("arizalar.csv", index=False)
if not os.path.exists("kasa.txt"):
    with open("kasa.txt", "w") as f: f.write("50000")

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
# 1. MENÜ: GÜNCEL SİTE BÜTÇESİ (GÜNCELLENDİ 🛠️)
# ==========================================
if menu == "📊 Güncel Site Bütçesi":
    st.subheader("📊 Güncel Site Bütçesi ve Harcamalar")
    
    with open("kasa.txt", "r") as f: kasa_bakiyesi = float(f.read())
    st.metric(label="💰 Kasa Toplam Bakiyesi", value=f"{kasa_bakiyesi:,.2f} TL")
    
    if is_admin:
        st.markdown("### ⚙️ Yönetici Bütçe Düzenleme")
        col1, col2 = st.columns(2)
        with col1:
            yeni_kasa = st.number_input("Ana Kasa Bakiyesini Doğrudan Güncelle (TL)", value=kasa_bakiyesi)
            if st.button("Kasayı Güncelle"):
                with open("kasa.txt", "w") as f: f.write(str(yeni_kasa))
                st.success("Kasa bakiyesi güncellendi!")
                st.rerun()
                
        with col2:
            st.markdown("**Yeni Harcama Kaydı Ekle**")
            h_tarih = st.date_input("Harcama Tarihi")
            h_aciklama = st.text_input("Harcama Kalemi / Açıklama (Örn: Asansör Bakımı)")
            h_tutar = st.number_input("Harcama Tutarı (TL)", min_value=0.0)
            if st.button("Harcamayı Kaydet ve Kasadan Düş"):
                if h_aciklama and h_tutar > 0:
                    df_butce = pd.read_csv("butce.csv")
                    yeni_harcama = pd.DataFrame([{"Tarih": str(h_tarih), "Açıklama": h_aciklama, "Tutar": h_tutar, "Tür": "Gider"}])
                    df_butce = pd.concat([df_butce, yeni_harcama], ignore_index=True)
                    df_butce.to_csv("butce.csv", index=False)
                    
                    with open("kasa.txt", "w") as f: f.write(str(kasa_bakiyesi - h_tutar))
                    st.success("Harcama kaydedildi ve bakiyeden düşüldü!")
                    st.rerun()

    st.markdown("#### 📜 Yapılan Harcamalar Listesi")
    df_butce = pd.read_csv("butce.csv")
    
    if len(df_butce) > 0:
        # Harcamaları tarihe göre sıralayıp gösteriyoruz
        df_butce = df_butce.sort_values(by="Tarih", ascending=False).reset_index(drop=True)
        
        # Eğer admin ise silme butonlu özel liste gösteriyoruz
        if is_admin:
            st.caption("Yönetici Girişi Aktif: Hatalı harcamaları aşağıdaki listeden iptal edebilirsiniz. Silinen tutar kasaya geri yüklenecektir.")
            for idx, row in df_butce.iterrows():
                col_tarih, col_aciklama, col_tutar, col_buton = st.columns([2, 5, 3, 2])
                with col_tarih: st.write(row['Tarih'])
                with col_aciklama: st.write(row['Açıklama'])
                with col_tutar: st.write(f"{row['Tutar']:,.2f} TL")
                with col_buton:
                    if st.button("❌ İptal Et/Sil", key=f"del_h_{idx}"):
                        # Kasaya parayı geri ekle
                        guncel_kasa = kasa_bakiyesi + float(row['Tutar'])
                        with open("kasa.txt", "w") as f: f.write(str(guncel_kasa))
                        
                        # Tablodan bu satırı sil
                        df_butce = df_butce.drop(idx)
                        df_butce.to_csv("butce.csv", index=False)
                        
                        st.success("Harcama iptal edildi, tutar kasaya geri yüklendi!")
                        st.rerun()
        else:
            # Normal kullanıcılar düz tablo görür
            st.dataframe(df_butce, use_container_width=True)
    else:
        st.info("Henüz yapılmış bir harcama kaydı bulunmuyor.")

# ==========================================
# 2. MENÜ: DUYURULAR
# ==========================================
elif menu == "📢 Duyurular":
    st.subheader("📢 Yönetimden Duyurular")
    
    if is_admin:
        st.markdown("### ⚙️ Yeni Duyuru Paylaş")
        d_baslik = st.text_input("Duyuru Başlığı")
        d_icerik = st.text_area("Duyuru Metni")
        if st.button("Duyuruyu Yayınla"):
            if d_baslik and d_icerik:
                df_duyuru = pd.read_csv("duyurular.csv")
                yeni_d = pd.DataFrame([{"Tarih": simdi.strftime("%d.%m.%Y"), "Başlık": d_baslik, "İçerik": d_icerik}])
                df_duyuru = pd.concat([df_duyuru, yeni_d], ignore_index=True)
                df_duyuru.to_csv("duyurular.csv", index=False)
                st.success("Duyuru başarıyla yayınlandı!")
                st.rerun()

    df_duyuru = pd.read_csv("duyurular.csv")
    if len(df_duyuru) > 0:
        for idx, row in df_duyuru.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"### 📌 {row['Başlık']}")
                st.caption(f"📅 Yayınlanma Tarihi: {row['Tarih']}")
                st.write(row['İçerik'])
                if is_admin:
                    if st.button(f"❌ Bu Duyuruyu Sil", key=f"del_d_{idx}"):
                        df_duyuru = df_duyuru.drop(idx)
                        df_duyuru.to_csv("duyurular.csv", index=False)
                        st.success("Duyuru silindi!")
                        st.rerun()
                st.markdown("---")
    else:
        st.info("Yayınlanmış aktif bir duyuru bulunmuyor.")

# ==========================================
# 3. MENÜ: AİDAT ÖDEME DURUMU
# ==========================================
elif menu == "💳 Aidat Ödeme Durumu":
    st.subheader("💳 Aidat ve Borç Takip Tablosu")
    
    df_aidat = pd.read_csv("aidat.csv")
    arama = st.text_input("🔍 Tabloda Ara (Blok, Daire No veya İsim girin):")
    if arama:
        df_goster = df_aidat[df_aidat.astype(str).apply(lambda x: x.str.contains(arama, case=False)).any(axis=1)]
    else:
        df_goster = df_aidat

    st.dataframe(df_goster, use_container_width=True)
    
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
                    df_aidat = pd.concat([df_aidat, yeni_a], ignore_index=True)
                    df_aidat.to_csv("aidat.csv", index=False)
                    st.success("Yeni veri başarıyla eklendi!")
                    st.rerun()
                    
        with col2:
            st.markdown("**Mevcut Satırı Sil**")
            if len(df_aidat) > 0:
                silinecek_idx = st.selectbox("Silmek istediğiniz kaydı seçin:", 
                                             options=range(len(df_aidat)), 
                                             format_func=lambda x: f"{df_aidat.iloc[x]['Blok']} Blok D:{df_aidat.iloc[x]['Daire']} - {df_aidat.iloc[x]['Sakin']} ({df_aidat.iloc[x]['Dönem']})")
                if st.button("Seçili Kaydı Sil"):
                    df_aidat = df_aidat.drop(silinecek_idx)
                    df_aidat.to_csv("aidat.csv", index=False)
                    st.success("Kayıt tablodan silindi!")
                    st.rerun()

# ==========================================
# 4. MENÜ: ARIZA BİLDİR
# ==========================================
elif menu == "🛠️ Arıza Bildir":
    st.subheader("🛠️ Arıza ve Talep Bildirim Formu")
    
    st.markdown("### 📋 Yeni Arıza Bildirim Formu")
    ari_daire = st.text_input("Blok ve Daireniz (Örn: A Blok Daire 5)")
    ari_baslik = st.text_input("Arıza Başlığı (Örn: Asansör Bozuk, Hidrofor Ses Yapıyor)")
    ari_aciklama = st.text_area("Arıza Detayı ve Açıklaması")
    
    if st.button("Bildirimi Yönetime Gönder"):
        if ari_daire and ari_baslik and ari_aciklama:
            df_ariza = pd.read_csv("arizalar.csv")
            yeni_ariza = pd.DataFrame([{"Tarih": simdi.strftime("%d.%m.%Y %H:%M"), "Daire": ari_daire, "Başlık": ari_baslik, "Açıklama": ari_aciklama, "Durum": "Beklemede"}])
            df_ariza = pd.concat([df_ariza, yeni_ariza], ignore_index=True)
            df_ariza.to_csv("arizalar.csv", index=False)
            st.success("Bildiriminiz site yönetimine başarıyla ulaştırıldı. Teşekkür ederiz!")
            st.rerun()
            
    if is_admin:
        st.write("---")
        st.markdown("### 📬 Gelen Arıza / Talep Kutusu (Sadece Yönetici)")
        df_ariza = pd.read_csv("arizalar.csv")
        
        if len(df_ariza) > 0:
            for idx, row in df_ariza.iterrows():
                with st.expander(f"🔴 {row['Tarih']} - {row['Daire']} : {row['Başlık']}"):
                    st.markdown(f"**Açıklama:** {row['Açıklama']}")
                    st.markdown(f"**Mevcut Durum:** {row['Durum']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Çözüldü Olarak İşaretle/Sil", key=f"solve_{idx}"):
                            df_ariza = df_ariza.drop(idx)
                            df_ariza.to_csv("arizalar.csv", index=False)
                            st.success("Talep çözüldü olarak işaretlendi ve kaldırıldı!")
                            st.rerun()
        else:
            st.info("Gelen herhangi bir arıza bildirilmedi.")
