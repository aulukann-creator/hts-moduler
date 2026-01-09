import json
import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication, QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from bs4 import BeautifulSoup

from ui.dialog import ModernDialog


def show_info(title: str, html: str, parent: QWidget = None):
    """
    Global HTML bilgi penceresi.
    show_expert_help() içindeki show_info(...) çağrısını karşılar.
    """
    try:
        if parent is None:
            parent = QApplication.activeWindow()

        dlg = QDialog(parent)
        dlg.setWindowTitle(title)
        dlg.setMinimumSize(820, 620)
        dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)

        v = QVBoxLayout(dlg)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(10)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html)
        v.addWidget(browser, 1)

        btn_close = QPushButton("Kapat")
        btn_close.setMinimumHeight(34)
        btn_close.clicked.connect(dlg.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(btn_close)
        v.addLayout(btn_row)

        dlg.exec()
    except Exception as e:
        # En kötü ihtimal fallback
        try:
            ModernDialog.show_info(parent, title, str(e))
        except Exception:
            pass


def _style_set_bg(tag, color: str):
    """
    tag['style'] içinde background/background-color varsa temizler, yeni background-color ekler.
    """
    s = str(tag.get("style", "") or "")
    parts = [p.strip() for p in s.split(";") if p.strip()]
    cleaned = []
    for p in parts:
        low = p.lower()
        if low.startswith("background:") or low.startswith("background-color:"):
            continue
        cleaned.append(p)
    cleaned.append(f"background-color:{color}")
    tag["style"] = ";".join(cleaned)


def _extract_table_headers_rows(table_html: str):
    """
    HtmlIcerik içinden ilk <table> için header ve body rows çıkarır.
    headers: list[str]
    rows: list[list[str]]
    """
    soup = BeautifulSoup(table_html or "", "html.parser")
    table = soup.find("table")
    if not table:
        return [], []

    # headers
    headers = []
    thead = table.find("thead")
    if thead:
        ths = thead.find_all("th")
        headers = [th.get_text(" ", strip=True) for th in ths]

    if not headers:
        first_tr = table.find("tr")
        if first_tr:
            headers = [x.get_text(" ", strip=True) for x in first_tr.find_all(["th", "td"])]

    # rows
    rows = []
    trs = table.find_all("tr")
    start_i = 1 if (trs and headers) else 0
    for tr in trs[start_i:]:
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        rows.append([c.get_text(" ", strip=True) for c in cells])

    return headers, rows


def _apply_hidden_cols_to_table_html(table_html: str, hidden_headers: list[str] | None) -> str:
    """
    hidden_headers: header text'e göre gizlenecek sütun adları.
    lxml zorunluluğu YOK: html.parser ile çalışır.
    """
    if not table_html:
        return table_html or ""
    hidden_headers = [str(x).strip() for x in (hidden_headers or []) if str(x).strip()]
    if not hidden_headers:
        return table_html

    try:
        from bs4 import BeautifulSoup
    except Exception:
        # bs4 yoksa dokunma
        return table_html

    try:
        soup = BeautifulSoup(table_html, "html.parser")  # ✅ lxml yok
        table = soup.find("table")
        if not table:
            return table_html

        # header metinleri -> kolon index
        header_row = None
        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
        if not header_row:
            header_row = table.find("tr")
        if not header_row:
            return str(soup)

        ths = header_row.find_all(["th", "td"], recursive=False) or header_row.find_all(["th", "td"])
        headers = [(" ".join(th.get_text(" ", strip=True).split())) for th in ths]

        hide_idx = set()
        for i, h in enumerate(headers):
            if h in hidden_headers:
                hide_idx.add(i)

        if not hide_idx:
            return str(soup)

        # tüm satırlarda ilgili hücreleri kaldır
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th", "td"], recursive=False)
            if not cells:
                cells = tr.find_all(["th", "td"])
            # sağdan sola sil (index kaymasın)
            for i in sorted(hide_idx, reverse=True):
                if i < len(cells):
                    cells[i].decompose()

        return str(soup)

    except Exception:
        return table_html


def _apply_fmt_to_table_html(table_html: str, fmt_json: str | None) -> str:
    """
    fmt_json: {
      "cols": {"0":"#ffeeaa", ...},
      "rows": {"1":"#ccffcc", ...},         # editor satır indexi (header HARİÇ)
      "cells":{"2,3":"#aabbcc", ...}        # editor satır indexi (header HARİÇ)
    }

    DÜZELTME:
    - Header satırı (<th>) varsa, rows/cells uygulamasında satır indeksini 1 kaydırır.
      (Editor satırları header saymaz; HTML <tr> listesi header'ı da sayar.)
    - Satır renklendirmesini <tr> yerine satırdaki tüm hücrelere uygular.
    """
    if not table_html:
        return table_html or ""
    if not fmt_json:
        return table_html

    try:
        fmt = json.loads(fmt_json) if isinstance(fmt_json, str) else (fmt_json or {})
        cols = (fmt or {}).get("cols") or {}
        rows = (fmt or {}).get("rows") or {}
        cells = (fmt or {}).get("cells") or {}

        soup = BeautifulSoup(table_html, "html.parser")
        table = soup.find("table")
        if not table:
            return table_html

        trs = table.find_all("tr")
        if not trs:
            return str(soup)

        # ✅ Header var mı? (ilk tr içinde th varsa)
        has_header = False
        first_cells = trs[0].find_all(["th", "td"], recursive=False)
        if not first_cells:
            first_cells = trs[0].find_all(["th", "td"])
        if any(c.name == "th" for c in first_cells):
            has_header = True

        def _set_bg_style(tag, color: str):
            if not tag or not color:
                return
            style = (tag.get("style") or "").strip()
            if "background-color" not in style.lower():
                if style and not style.strip().endswith(";"):
                    style += ";"
                style += f" background-color: {color};"
            else:
                style = re.sub(
                    r"background-color\s*:\s*[^;]+;?",
                    f"background-color: {color};",
                    style,
                    flags=re.I
                )
            tag["style"] = style.strip()

        # 1) Kolon renklendirme (header dahil) — burada index değişmez
        for col_idx_str, color in cols.items():
            try:
                ci = int(col_idx_str)
            except Exception:
                continue

            for tr in trs:
                tds = tr.find_all(["th", "td"])
                if 0 <= ci < len(tds):
                    _set_bg_style(tds[ci], color)

        # ✅ Editor->HTML satır map: header varsa +1
        def _to_html_row(editor_row: int) -> int:
            return editor_row + 1 if has_header else editor_row

        # 2) Satır renklendirme (editor satır indexi -> html tr indexi)
        for row_idx_str, color in rows.items():
            try:
                editor_ri = int(row_idx_str)
            except Exception:
                continue

            html_ri = _to_html_row(editor_ri)
            if 0 <= html_ri < len(trs):
                tds = trs[html_ri].find_all(["th", "td"])
                for td in tds:
                    _set_bg_style(td, color)

        # 3) Hücre renklendirme (editor row,col -> html row,col)
        for key, color in cells.items():
            try:
                r_s, c_s = str(key).split(",", 1)
                editor_ri = int(r_s.strip())
                ci = int(c_s.strip())
            except Exception:
                continue

            html_ri = _to_html_row(editor_ri)
            if 0 <= html_ri < len(trs):
                tds = trs[html_ri].find_all(["th", "td"])
                if 0 <= ci < len(tds):
                    _set_bg_style(tds[ci], color)

        return str(soup)

    except Exception:
        return table_html
