# Ev Bitkisi Sulama - Bulanik Mantik Donem Projesi

**Barış Çevik**  
Bilişim Sistemleri ve Teknolojileri | Öğrenci No: **22430070008**  
Ders: Bulanık Mantık

Evdeki saksı bitkisi icin toprak nemi, ortam sicakligi ve isik seviyesine gore **sulama suresi (dakika)** oneren bulanik kontrol sistemi.

## Proje icerigi (teslim)

| Istenen | Repoda |
|---------|--------|
| Rapor (Word) | `Bulanik_Mantik_Donem_Projesi.docx` |
| Kaynak kod | `fuzzy_controller.py`, `app.py` |
| README | bu dosya |
| En az 3 giris, 3 dilsel terim | nem, sicaklik, isik |
| En az 15 kural | 18 Mamdani kurali (`fuzzy_controller.py`) |
| Centroid durulastirma | scikit-fuzzy varsayilan |
| Streamlit arayuz | `app.py` |
| Uyelik grafikleri, aktif kurallar, Hesapla | arayuzde mevcut |

## Kurulum ve calistirma

```
pip install -r requirements.txt
streamlit run app.py
```

## Dosyalar

- `fuzzy_controller.py` - uyelik fonksiyonlari, kurallar, cikarim
- `app.py` - Streamlit arayuzu
- `generate_report.py` / `save_report_figures.py` - rapor ve grafik uretimi
- `rapor_gorselleri/` - rapordaki sekiller
- `requirements.txt` - kutuphaneler

## Konu

Dersin ornek listesindeki klima / sera / trafik vb. konulardan farkli: **ev bitkisi sulama kontrolu**.
