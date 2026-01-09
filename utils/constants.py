import os
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    APP_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

HEADER_ALIASES = {
    "hts_abone": {
        "SIRA NO": "SIRA_NO", "SIRANO": "SIRA_NO",
        "NUMARA": "NUMARA", "GSM NO": "NUMARA", "MSISDN": "NUMARA",
        "DURUM": "DURUM", "ABONE DURUMU": "DURUM",
        "AD": "AD", "ABONE ADI": "AD", "ISIM": "AD", "MUSTERI ADI": "AD",
        "SOYAD": "SOYAD", "ABONE SOYADI": "SOYAD", "MUSTERI SOYADI": "SOYAD",
        "ADRES": "ADRES", "ABONE ADRESI": "ADRES", "FATURA ADRESI": "ADRES",
        "DOGUM TARİHİ": "DOGUM_TARIHI", "DOGUM TARIHI": "DOGUM_TARIHI",
        "DOGUM YERİ": "DOGUM_YERI", "DOGUM YERI": "DOGUM_YERI",
        "İLÇE": "ILCE", "ILCE": "ILCE",
        "İL": "IL", "SEHIR": "IL",
        "TC KİMLİK NO": "TC_KIMLIK_NO", "TCK NO": "TC_KIMLIK_NO", "TC KIMLIK NO": "TC_KIMLIK_NO", "TCKNO": "TC_KIMLIK_NO",
        "ANNE ADI": "ANNE_ADI", "ANNE": "ANNE_ADI",
        "BABA ADI": "BABA_ADI", "BABA": "BABA_ADI",
        "ABONE SORGU ARALIĞI": "ABONE_SORGU_ARALIGI", "SORGU ARALIGI": "ABONE_SORGU_ARALIGI",
        "ABONE BASLANGIÇ": "ABONE_BASLANGIC", "BASLANGIC TARIHI": "ABONE_BASLANGIC",
        "ABONE BİTİŞ": "ABONE_BITIS", "BITIS TARIHI": "ABONE_BITIS",
        "OPERATÖR": "OPERATOR", "OPERATOR": "OPERATOR"
    },
    "hts_gsm": {
        "SIRA NO": "SIRA_NO", "SIRA": "SIRA_NO",
        "NUMARA": "NUMARA", "ARAYAN NO": "NUMARA", "GSM NO": "NUMARA",
        "TİP": "TIP", "ARAMA TİPİ": "TIP", "YON": "TIP", "CALL TYPE": "TIP", "ISLEM TIPI": "TIP",
        "DİĞER NUMARA": "DIGER_NUMARA", "KARSI NUMARA": "DIGER_NUMARA", "ARANAN NO": "DIGER_NUMARA", "DIGER NO": "DIGER_NUMARA", "KARSI TARAF": "DIGER_NUMARA",
        "TARİH": "TARIH", "ARAMA TARİHİ": "TARIH", "ISLEM TARIHI": "TARIH", "BASLANGIC TARIHI": "TARIH", "TARIH SAAT": "TARIH",
        "SÜRE": "SURE", "ARAMA SÜRESİ": "SURE", "SURE (SN)": "SURE", "DURATION": "SURE",

        "İsim Soyisim ( Numara)": "DIGER_ISIM",
        "İsim Soyisim (  Numara)": "DIGER_ISIM",
        "İsim Soyisim ( Diğer Numara)": "DIGER_ISIM",
        "REHBER ADI": "DIGER_ISIM",
        "DIGER ISIM": "DIGER_ISIM",
        "KARSI AD SOYAD": "DIGER_ISIM",

        "TC Kimlik No ( Numara)": "DIGER_TC",
        "TC Kimlik No (  Numara)": "DIGER_TC",
        "TC Kimlik No (Diğer Numara)": "DIGER_TC",
        "DIGER TC": "DIGER_TC",
        "KARSI TC": "DIGER_TC",

        "IMEI": "IMEI", "KULLANILAN IMEI": "IMEI",
        "BAZ (Numara)": "BAZ", "BAZ": "BAZ", "BAZ ISTASYONU": "BAZ", "CELL ID": "BAZ", "LOKASYON": "BAZ", "HCRE ADI": "BAZ"
    },
    "hts_sms": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "DİĞER NUMARA": "DIGER_NUMARA",
        "TARİH": "TARIH", "SÜRE": "SURE",
        "İsim Soyisim ( Numara)": "DIGER_ISIM",
        "İsim Soyisim ( Diğer Numara)": "DIGER_ISIM", "KARSI ABONE": "DIGER_ISIM",
        "TC Kimlik No ( Numara)": "DIGER_TC",
        "TC Kimlik No (Diğer Numara)": "DIGER_TC",
        "MESAJ BOYUTU (Byte)": "MESAJ_BOYUTU", "MESAJ İÇERİK TİPİ": "MESAJ_ICERIK_TIPI"
    },
    "hts_sabit": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "DİĞER NUMARA": "DIGER_NUMARA",
        "TARİH": "TARIH", "SÜRE": "SURE", "İsim Soyisim ( Diğer Numara)": "DIGER_ISIM", "TC Kimlik No (Diğer Numara)": "DIGER_TC"
    },
    "hts_gprs": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "TARİH": "TARIH", "SÜRE": "SURE",
        "IMEI": "IMEI", "KAYNAK IP": "KAYNAK_IP", "GÖNDERME BOYUTU (Byte)": "GONDERME", "İNDİRME BOYUTU (Byte)": "INDIRME", "BAZ (Numara)": "BAZ", "BAZ": "BAZ"
    },
    "hts_wap": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "TARİH": "TARIH", "SÜRE": "SURE",
        "IMEI": "IMEI", "KAYNAK IP": "KAYNAK_IP", "HEDEF IP": "HEDEF_IP", "ERİŞİLEN SAYFA": "ERISILEN_SAYFA",
        "GÖNDERME BOYUTU (Byte)": "GONDERME", "İNDİRME BOYUTU (Byte)": "INDIRME", "BAZ (Numara)": "BAZ", "BAZ": "BAZ"
    },
    "hts_sth": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "DİĞER NUMARA": "DIGER_NUMARA", "TARİH": "TARIH", "SÜRE": "SURE", "OPERATÖR": "OPERATOR", "İsim Soyisim ( Diğer Numara)": "DIGER_ISIM", "TC Kimlik No (Diğer Numara)": "DIGER_TC", "DATA TİP": "DATA_TIP", "DURUM": "DURUM", "PİN NO": "PIN_NO", "BAŞL. GATEWAY": "BASL_GATEWAY", "SONL. GATEWAY": "SONL_GATEWAY", "BAŞL. SANTRAL": "BASL_SANTRAL", "SONL. SANTRAL": "SONL_SANTRAL"
    },
    "hts_uluslararasi": {
        "SIRA NO": "SIRA_NO", "NUMARA": "NUMARA", "TİP": "TIP", "DİĞER NUMARA": "DIGER_NUMARA", "TARİH": "TARIH", "SÜRE": "SURE", "İsim Soyisim ( Diğer Numara)": "DIGER_ISIM", "TC Kimlik No (Diğer Numara)": "DIGER_TC"
    }
}
TABLE_COLUMNS = {
    "hts_abone": [
        "SIRA_NO", "NUMARA", "DURUM", "AD", "SOYAD", "ADRES",
        "DOGUM_TARIHI", "DOGUM_YERI", "ILCE", "IL", "TC_KIMLIK_NO",
        "ANNE_ADI", "BABA_ADI", "ABONE_SORGU_ARALIGI", "ABONE_BASLANGIC",
        "ABONE_BITIS", "OPERATOR"
    ],
    "hts_gsm": [
        "SIRA_NO", "NUMARA", "TIP", "DIGER_NUMARA", "TARIH",
        "SURE", "DIGER_ISIM", "DIGER_TC", "IMEI", "BAZ"
    ],
    "hts_sabit": [
        "SIRA_NO", "NUMARA", "TIP", "DIGER_NUMARA", "TARIH",
        "SURE", "DIGER_ISIM", "DIGER_TC"
    ],
    "hts_uluslararasi": [
        "SIRA_NO", "NUMARA", "TIP", "DIGER_NUMARA", "TARIH",
        "SURE", "DIGER_ISIM", "DIGER_TC"
    ],
    "hts_sms": [
        "SIRA_NO", "NUMARA", "TIP", "DIGER_NUMARA", "TARIH",
        "SURE", "DIGER_ISIM", "DIGER_TC", "MESAJ_BOYUTU", "MESAJ_ICERIK_TIPI"
    ],
    "hts_gprs": [
        "SIRA_NO", "NUMARA", "TIP", "TARIH", "SURE",
        "IMEI", "KAYNAK_IP", "GONDERME", "INDIRME", "BAZ"
    ],
    "hts_wap": [
        "SIRA_NO", "NUMARA", "TIP", "TARIH", "SURE",
        "IMEI", "KAYNAK_IP", "HEDEF_IP", "ERISILEN_SAYFA",
        "GONDERME", "INDIRME", "BAZ"
    ],
    "hts_sth": [
        "SIRA_NO", "NUMARA", "TIP", "DIGER_NUMARA", "TARIH",
        "SURE", "OPERATOR", "DIGER_ISIM", "DIGER_TC", "DATA_TIP",
        "DURUM", "PIN_NO", "BASL_GATEWAY", "SONL_GATEWAY",
        "BASL_SANTRAL", "SONL_SANTRAL"
    ]
}
QSS_LIGHT = """
/* === GENEL PENCERE AYARLARI === */
QMainWindow, QDialog { 
    background-color: #f4f6f8; 
}
QWidget { 
    color: #2c3e50; 
    font-family: 'Segoe UI', sans-serif; 
    font-size: 13px; 
}

/* === GÖRÜNMEZ ÇERÇEVELERİ TEMİZLE === */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }

/* === GİRİŞ KUTULARI (INPUTS) === */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px;
    color: #2c3e50;
    selection-background-color: #3498db;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 2px solid #3498db;
    background-color: #ffffff;
}

/* === TABLOLAR === */
QTableView, QTableWidget {
    background-color: #ffffff;
    gridline-color: #ecf0f1;
    border: 1px solid #dcdcdc;
    selection-background-color: #e8f6f3; 
    selection-color: #16a085;
    alternate-background-color: #fafafa;
    outline: none;
}
QHeaderView::section {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 8px;
    border: none;
    border-right: 1px solid #bdc3c7;
    border-bottom: 2px solid #bdc3c7;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

/* === GRUPLAMA KUTULARI (GROUPBOX) === */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 6px;
    margin-top: 24px;
    font-weight: bold;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #2980b9;
    background-color: transparent;
}

/* === FRAME (KUTULAR) === */
QFrame { border: none; }
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    background-color: #dcdcdc;
    min-height: 1px; max-height: 1px; border: none;
}

/* === BUTONLAR === */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover { background-color: #2980b9; margin-top: 1px; }
QPushButton:pressed { background-color: #1abc9c; }
QPushButton:disabled { background-color: #bdc3c7; color: #ecf0f1; }

/* === SEKME (TABS) - BELİRGİN VE MODERN === */
QTabWidget::pane {
    border: 1px solid #dcdcdc;
    background-color: #ffffff;
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
    border-top-right-radius: 6px;
    /* Sol üst köşe düz kalsın ki seçili sekmeyle birleşsin */
    margin-top: -1px; 
}

QTabBar::tab {
    background: #e5e7eb; /* Pasif Gri */
    color: #57606f;
    padding: 10px 25px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    min-width: 80px;
}

/* Fare üzerine gelince */
QTabBar::tab:hover {
    background: #d1d5db;
    color: #2c3e50;
}

/* SEÇİLİ SEKME (KRİTİK GÜNCELLEME) */
QTabBar::tab:selected {
    background: #3498db; /* Canlı Mavi */
    color: white;        /* Beyaz Yazı */
    border-bottom: 2px solid #3498db; /* Alt çizgi aynı renk (birleşme için) */
}

/* === SCROLL BARS === */
QScrollBar:vertical {
    border: none; background: #f1f1f1; width: 10px; margin: 0; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #bdc3c7; min-height: 20px; border-radius: 5px;
}
QScrollBar::handle:vertical:hover { background: #95a5a6; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

QScrollBar:horizontal {
    border: none; background: #f1f1f1; height: 10px; margin: 0; border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #bdc3c7; min-width: 20px; border-radius: 5px;
}

/* === TÜM BALONCUKLAR İÇİN ORTAK STANDART (TOOLTIP) === */
QToolTip {
    background-color: rgba(255, 255, 255, 200);
    color: #2c3e50;
    border: 1px solid #3498db;
    border-radius: 4px;
    padding: 8px 10px;
    font-size: 12px;
}
/* Özel Durum: Tablo içindeki baloncuklar için ekstra zorlama */
QTableView QToolTip, QTableWidget QToolTip {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
}
/* === SAĞ TIK MENÜLERİ (QMenu) === */
QMenu {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
    border-radius: 6px;
    padding: 6px;
}
QMenu::item {
    background-color: transparent;
    padding: 8px 18px;
    border-radius: 4px;
    color: #2c3e50;
}
QMenu::item:selected {
    background-color: #e8f6f3;
    color: #16a085;
}
QMenu::separator {
    height: 1px;
    background: #ecf0f1;
    margin: 6px 8px;
}

/* === QComboBox AÇILAN LİSTE (popup) === */
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
    selection-background-color: #e8f6f3;
    selection-color: #16a085;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 6px 10px;
}

/* === TABLO HÜCRELERİNİN KALINLAŞMASINI BASKILA === */
QTableView::item, QTableWidget::item {
    font-weight: normal;
}
"""
