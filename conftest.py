"""
Pengaturan bersama untuk semua test DemoQA.

Isinya:
- ukuran jendela browser yang tetap, biar hasil screenshot/video konsisten
- pemblokir iklan (DemoQA penuh iklan yang sering menutupi tombol dan bikin klik gagal)
- helper untuk menyimpan screenshot bukti per test
- menempelkan screenshot akhir ke laporan HTML
"""
import base64
import re
from pathlib import Path

import pytest

FOLDER_BUKTI = Path("hasil/bukti")

# Domain iklan yang kita blokir supaya tidak menutupi elemen yang mau diklik
DOMAIN_IKLAN = (
    "googlesyndication.com",
    "doubleclick.net",
    "googleadservices.com",
    "adservice.google",
    "pagead2",
    "adnxs.com",
    "amazon-adsystem.com",
    "carbonads",
)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}}


@pytest.fixture(autouse=True)
def blokir_iklan(context):
    def tangani(route):
        if any(d in route.request.url for d in DOMAIN_IKLAN):
            route.abort()
        else:
            route.continue_()

    # dipasang di context, jadi tab/window baru ikut terblokir iklannya
    context.route("**/*", tangani)


@pytest.fixture
def bukti(request, page):
    """Panggil bukti('nama-langkah') untuk menyimpan screenshot di hasil/bukti/."""
    FOLDER_BUKTI.mkdir(parents=True, exist_ok=True)
    nama_test = re.sub(r"[^\w-]", "_", request.node.name)

    def simpan(langkah, halaman=None):
        (halaman or page).screenshot(
            path=str(FOLDER_BUKTI / f"{nama_test}__{langkah}.png")
        )

    return simpan


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Tempel screenshot akhir ke laporan HTML (butuh pytest-html versi 4 ke atas)."""
    outcome = yield
    laporan = outcome.get_result()
    if laporan.when != "call":
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        from pytest_html import extras

        png = base64.b64encode(page.screenshot()).decode()
        laporan.extras = getattr(laporan, "extras", []) + [extras.png(png)]
    except Exception:
        pass  # kalau gagal, jangan sampai merusak hasil test
