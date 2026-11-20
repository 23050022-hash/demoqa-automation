# Automation Testing DemoQA (Playwright + pytest)

Cakupan: Practice Form, Browser Windows, Alerts, Frames, Nested Frames, Modal Dialogs. Total 17 test.

## Persiapan (cukup sekali)

Butuh Python 3.9 atau lebih baru. Buka terminal di folder ini, lalu:

```
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
playwright install chromium
```

## Menjalankan

Jalankan semua test:

```
pytest
```

Untuk **rekam layar** (biar browser kelihatan jalan dan pelan-pelan):

```
pytest --headed --slowmo 600
```

Jalankan satu test saja:

```
pytest -k aut09
```

## Hasilnya ada di mana?

Semua tersimpan otomatis di folder `hasil/`:

| Yang dicari | Lokasinya |
|---|---|
| Test report (buka di browser) | `hasil/laporan_automation.html` |
| Video eksekusi per test | `hasil/test-results/<nama-test>/video.webm` |
| Screenshot akhir per test | `hasil/test-results/<nama-test>/test-finished-1.png` |
| Screenshot langkah penting | `hasil/bukti/` |

Laporan HTML sudah memuat status Pass/Fail, durasi tiap test, dan screenshot akhirnya, jadi bisa langsung di-screenshot untuk Tabel 3.5 di laporan.

## Kalau ada test yang gagal

1. Cek dulu apakah koneksi ke demoqa.com lancar. Situsnya kadang lambat.
2. Lihat pesan error di laporan. Kalau yang gagal adalah *locator* (elemen tidak ditemukan), kemungkinan tampilan DemoQA berubah. Buka halamannya, klik kanan elemen > Inspect, lalu sesuaikan selector di `test_demoqa.py`.
3. Kalau gagalnya karena assertion (hasil beda dari yang diharapkan), itu bisa jadi temuan beneran. Catat di bagian Temuan laporan.
