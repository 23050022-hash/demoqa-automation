"""
Automation Testing DemoQA - Step 2 (Pengujian Otomatis)

Modul yang diuji:
  1. Forms          -> Practice Form
  2. Alerts, Frame & Windows -> Browser Windows, Alerts, Frames,
                                Nested Frames, Modal Dialogs

Tools: Python + Playwright + pytest
Setiap test punya assertion (expect / assert) supaya jelas kapan dianggap lulus.
"""
import re

import pytest
from playwright.sync_api import expect

BASE = "https://demoqa.com"


# --------------------------------------------------------------------------
# Helper
# --------------------------------------------------------------------------
def buka(page, jalur):
    """Buka halaman DemoQA lalu singkirkan banner/footer yang suka menutupi tombol."""
    page.goto(f"{BASE}{jalur}", wait_until="domcontentloaded")
    page.evaluate(
        """() => ['#fixedban', 'footer'].forEach(
               s => document.querySelectorAll(s).forEach(e => e.remove()))"""
    )


def klik_dan_tangani_dialog(page, selector, terima=True, isi=None, timeout=10_000):
    """
    Klik tombol yang memunculkan dialog JavaScript (alert/confirm/prompt),
    tangani dialognya, lalu kembalikan pesan dan tipe dialog yang muncul.
    """
    hasil = {}

    def tangani(dialog):
        hasil["pesan"] = dialog.message
        hasil["tipe"] = dialog.type
        if not terima:
            dialog.dismiss()
        elif isi is not None:
            dialog.accept(isi)
        else:
            dialog.accept()

    page.once("dialog", tangani)
    with page.expect_event("dialog", timeout=timeout):
        page.click(selector)
    return hasil


def isi_form_wajib(page, depan="Budi", belakang="Santoso", nomor="0812345678"):
    """Isi kolom yang wajib saja: nama, gender, dan nomor HP."""
    page.fill("#firstName", depan)
    page.fill("#lastName", belakang)
    page.click('label[for="gender-radio-1"]')  # Male
    page.fill("#userNumber", nomor)


def kirim_form(page):
    page.locator("#submit").scroll_into_view_if_needed()
    page.click("#submit")


def sel_hasil(page, label):
    """Ambil sel nilai di tabel hasil submit berdasarkan labelnya."""
    return page.locator(".modal-body tbody tr", has_text=label).locator("td").nth(1)


JUDUL_MODAL_FORM = "#example-modal-sizes-title-lg"


# ==========================================================================
# BAGIAN 1 - FORMS (Practice Form)
# ==========================================================================
def test_aut01_form_diisi_lengkap_berhasil_dikirim(page, bukti):
    """Semua kolom diisi dengan data valid, lalu data di popup harus sama dengan input."""
    buka(page, "/automation-practice-form")

    page.fill("#firstName", "Budi")
    page.fill("#lastName", "Santoso")
    page.fill("#userEmail", "budi.santoso@example.com")
    page.click('label[for="gender-radio-1"]')
    page.fill("#userNumber", "0812345678")

    page.click("#dateOfBirthInput")
    page.keyboard.press("Control+A")
    page.keyboard.type("15 Mar 1999")
    page.keyboard.press("Enter")

    page.fill("#subjectsInput", "Maths")
    page.keyboard.press("Enter")

    page.click('label[for="hobbies-checkbox-1"]')  # Sports
    page.click('label[for="hobbies-checkbox-3"]')  # Music

    page.set_input_files(
        "#uploadPicture",
        files={
            "name": "foto_uji.png",
            "mimeType": "image/png",
            # gambar PNG 1x1 piksel
            "buffer": bytes.fromhex(
                "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
                "0000000d49444154789c6360000002000001e221bc330000000049454e44ae426082"
            ),
        },
    )
    page.fill("#currentAddress", "Jl. Merdeka No. 10, Bogor")

    page.click("#state")
    page.get_by_text("NCR", exact=True).click()
    page.click("#city")
    page.get_by_text("Delhi", exact=True).click()
    bukti("form-terisi", page)

    kirim_form(page)

    expect(page.locator(JUDUL_MODAL_FORM)).to_have_text("Thanks for submitting the form")
    expect(sel_hasil(page, "Student Name")).to_have_text("Budi Santoso")
    expect(sel_hasil(page, "Student Email")).to_have_text("budi.santoso@example.com")
    expect(sel_hasil(page, "Gender")).to_have_text("Male")
    expect(sel_hasil(page, "Mobile")).to_have_text("0812345678")
    expect(sel_hasil(page, "Date of Birth")).to_have_text("15 March,1999")
    expect(sel_hasil(page, "Subjects")).to_have_text("Maths")
    expect(sel_hasil(page, "Hobbies")).to_have_text("Sports, Music")
    expect(sel_hasil(page, "Picture")).to_have_text("foto_uji.png")
    expect(sel_hasil(page, "Address")).to_have_text("Jl. Merdeka No. 10, Bogor")
    expect(sel_hasil(page, "State and City")).to_have_text("NCR Delhi")
    bukti("popup-hasil", page)


def test_aut02_form_hanya_kolom_wajib_berhasil(page, bukti):
    """Cukup nama, gender, dan nomor HP: form harus tetap bisa dikirim."""
    buka(page, "/automation-practice-form")
    isi_form_wajib(page)
    kirim_form(page)

    expect(page.locator(JUDUL_MODAL_FORM)).to_have_text("Thanks for submitting the form")
    expect(sel_hasil(page, "Student Name")).to_have_text("Budi Santoso")
    bukti("popup-hasil", page)


def test_aut03_form_kosong_ditolak(page, bukti):
    """Form dikirim tanpa diisi: tidak boleh muncul popup sukses."""
    buka(page, "/automation-practice-form")
    kirim_form(page)

    expect(page.locator(JUDUL_MODAL_FORM)).to_have_count(0)
    expect(page.locator("form#userForm")).to_have_class(re.compile("was-validated"))
    expect(page.locator("#firstName:invalid")).to_have_count(1)
    expect(page.locator("#lastName:invalid")).to_have_count(1)
    expect(page.locator("#userNumber:invalid")).to_have_count(1)
    bukti("validasi-kosong", page)


def test_aut04_nomor_hp_kurang_dari_10_digit_ditolak(page, bukti):
    """Nomor HP hanya 5 digit: form harus ditolak."""
    buka(page, "/automation-practice-form")
    isi_form_wajib(page, nomor="12345")
    kirim_form(page)

    expect(page.locator(JUDUL_MODAL_FORM)).to_have_count(0)
    expect(page.locator("#userNumber:invalid")).to_have_count(1)
    bukti("validasi-nomor-hp", page)


def test_aut05_format_email_salah_ditolak(page, bukti):
    """Email diisi 'budi@@mail': form harus ditolak."""
    buka(page, "/automation-practice-form")
    isi_form_wajib(page)
    page.fill("#userEmail", "budi@@mail")
    kirim_form(page)

    expect(page.locator(JUDUL_MODAL_FORM)).to_have_count(0)
    expect(page.locator("#userEmail:invalid")).to_have_count(1)
    bukti("validasi-email", page)


# ==========================================================================
# BAGIAN 2 - ALERTS, FRAME & WINDOWS
# ==========================================================================

# ---- Browser Windows -----------------------------------------------------
def test_aut06_browser_windows_new_tab(page, bukti):
    """Tombol New Tab harus membuka tab baru berisi halaman sample."""
    buka(page, "/browser-windows")
    with page.context.expect_page() as info:
        page.click("#tabButton")
    tab_baru = info.value
    tab_baru.wait_for_load_state()

    assert tab_baru.url.endswith("/sample")
    expect(tab_baru.locator("#sampleHeading")).to_have_text("This is a sample page")
    bukti("tab-baru", tab_baru)
    tab_baru.close()


def test_aut07_browser_windows_new_window(page, bukti):
    """Tombol New Window harus membuka jendela baru berisi halaman sample."""
    buka(page, "/browser-windows")
    with page.context.expect_page() as info:
        page.click("#windowButton")
    jendela = info.value
    jendela.wait_for_load_state()

    assert jendela.url.endswith("/sample")
    expect(jendela.locator("#sampleHeading")).to_have_text("This is a sample page")
    bukti("window-baru", jendela)
    jendela.close()


def test_aut08_browser_windows_new_window_message(page, bukti):
    """Tombol New Window Message harus membuka jendela berisi pesan teks."""
    buka(page, "/browser-windows")
    with page.context.expect_page() as info:
        page.click("#messageWindowButton")
    jendela = info.value
    jendela.wait_for_load_state()

    expect(jendela.locator("body")).to_contain_text("Knowledge increases by sharing")
    bukti("window-pesan", jendela)
    jendela.close()


# ---- Alerts --------------------------------------------------------------
def test_aut09_alert_sederhana(page, bukti):
    """Alert biasa: pesannya harus sesuai."""
    buka(page, "/alerts")
    hasil = klik_dan_tangani_dialog(page, "#alertButton")

    assert hasil["tipe"] == "alert"
    assert hasil["pesan"] == "You clicked a button"
    bukti("setelah-alert", page)


def test_aut10_alert_muncul_setelah_5_detik(page, bukti):
    """Alert yang muncul tertunda: harus muncul dalam batas waktu wajar (sekitar 5 detik)."""
    buka(page, "/alerts")
    hasil = klik_dan_tangani_dialog(page, "#timerAlertButton", timeout=10_000)

    assert hasil["tipe"] == "alert"
    assert hasil["pesan"] == "This alert appeared after 5 seconds"
    bukti("setelah-alert-timer", page)


def test_aut11_confirm_pilih_ok(page, bukti):
    """Confirm dijawab OK: halaman harus menampilkan 'You selected Ok'."""
    buka(page, "/alerts")
    hasil = klik_dan_tangani_dialog(page, "#confirmButton", terima=True)

    assert hasil["tipe"] == "confirm"
    assert hasil["pesan"] == "Do you confirm action?"
    expect(page.locator("#confirmResult")).to_contain_text("You selected Ok")
    bukti("hasil-confirm-ok", page)


def test_aut12_confirm_pilih_cancel(page, bukti):
    """Confirm dijawab Cancel: halaman harus menampilkan 'You selected Cancel'."""
    buka(page, "/alerts")
    hasil = klik_dan_tangani_dialog(page, "#confirmButton", terima=False)

    assert hasil["tipe"] == "confirm"
    expect(page.locator("#confirmResult")).to_contain_text("You selected Cancel")
    bukti("hasil-confirm-cancel", page)


def test_aut13_prompt_diisi_nama(page, bukti):
    """Prompt diisi nama: nama itu harus tampil di halaman."""
    buka(page, "/alerts")
    hasil = klik_dan_tangani_dialog(page, "#promtButton", terima=True, isi="Olivia")

    assert hasil["tipe"] == "prompt"
    assert hasil["pesan"] == "Please enter your name"
    expect(page.locator("#promptResult")).to_contain_text("You entered Olivia")
    bukti("hasil-prompt", page)


# ---- Frames --------------------------------------------------------------
def test_aut14_frames_dua_iframe_terbaca(page, bukti):
    """Dua iframe di halaman Frames harus bisa dibuka dan isinya terbaca."""
    buka(page, "/frames")

    expect(page.frame_locator("#frame1").locator("#sampleHeading")).to_have_text(
        "This is a sample page"
    )
    expect(page.frame_locator("#frame2").locator("#sampleHeading")).to_have_text(
        "This is a sample page"
    )
    bukti("frames", page)


def test_aut15_nested_frames_induk_dan_anak(page, bukti):
    """Nested Frames: teks frame induk dan frame anak harus terbaca."""
    buka(page, "/nestedframes")

    induk = page.frame_locator("#frame1")
    anak = induk.frame_locator("iframe")
    expect(induk.locator("body")).to_contain_text("Parent frame")
    expect(anak.locator("body")).to_contain_text("Child Iframe")
    bukti("nested-frames", page)


# ---- Modal Dialogs -------------------------------------------------------
def test_aut16_modal_kecil_buka_dan_tutup(page, bukti):
    """Small modal: tampil dengan isi yang benar, lalu hilang setelah ditutup."""
    buka(page, "/modal-dialogs")
    page.click("#showSmallModal")

    expect(page.locator("#example-modal-sizes-title-sm")).to_have_text("Small Modal")
    expect(page.locator(".modal-body")).to_contain_text("This is a small modal")
    bukti("modal-kecil-terbuka", page)

    page.click("#closeSmallModal")
    expect(page.locator(".modal-content")).to_be_hidden()


def test_aut17_modal_besar_buka_dan_tutup(page, bukti):
    """Large modal: tampil dengan isi yang benar, lalu hilang setelah ditutup."""
    buka(page, "/modal-dialogs")
    page.click("#showLargeModal")

    expect(page.locator("#example-modal-sizes-title-lg")).to_have_text("Large Modal")
    expect(page.locator(".modal-body")).to_contain_text("Lorem Ipsum")
    bukti("modal-besar-terbuka", page)

    page.click("#closeLargeModal")
    expect(page.locator(".modal-content")).to_be_hidden()
