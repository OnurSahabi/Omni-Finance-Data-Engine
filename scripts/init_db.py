import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_connection import get_connection

# --- AYARLAR ---
# SQL dosyalarının bulunduğu klasör
SQL_KLASORU = "database"


SQL_DOSYALARI = ["schema.sql", "return_function.sql"]


def sql_scriptlerini_calistir():
    baglanti = None
    imlec = None
    try:

        print("🔌 Veritabanına bağlanılıyor...")
        baglanti = get_connection()
        imlec = baglanti.cursor()
        print("✅ Veritabanı bağlantısı başarılı!\n")

        #  Dosyaları Sırayla Oku ve Çalıştır
        for dosya_adi in SQL_DOSYALARI:
            # Proje ana dizininden Database klasörüne giden yolu oluşturur
            dosya_yolu = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', SQL_KLASORU, dosya_adi))

            if os.path.exists(dosya_yolu):
                print(f"📂 '{dosya_adi}' okunuyor ve çalıştırılıyor...")

                with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
                    sql_sorgusu = dosya.read()

                    # SQL kodunu çalıştır
                    imlec.execute(sql_sorgusu)

                    # Değişiklikleri kaydet
                    baglanti.commit()
                    print(f"✅ '{dosya_adi}' başarıyla uygulandı!\n")
            else:
                raise FileNotFoundError(f"⚠️ HATA: '{dosya_yolu}' bulunamadı!")

        print("🎉 Tüm SQL scriptleri başarıyla veritabanına işlendi!")

    except Exception as hata:
        print(f"❌ Bir hata oluştu: {hata}")
        if baglanti:
            baglanti.rollback()
            print("⚠️ Hatalı işlem geri alındı (Rollback).")

    finally:
        # 3. Bağlantıları Kapat
        if imlec:
            imlec.close()
        if baglanti:
            baglanti.close()
            print("🔒 Veritabanı bağlantısı kapatıldı.")


if __name__ == "__main__":
    sql_scriptlerini_calistir()