import os
import sys

from security.security import LicenseManager
from time_utils.time_guard import TrustedTimeGuard
from ui.main_window import LicenseGateDialog, enforce_normal_table_fonts, apply_light_combobox_popup, TooltipManager, \
    MainWindow, _quit_app, restart_application
from ui.dialog import ModernDialog
from utils.constants import QSS_LIGHT
from utils.constants import APP_DIR
assert isinstance(QSS_LIGHT, object)
from utils.constants import QSS_LIGHT

try:
    os.add_dll_directory(APP_DIR)  # Py3.8+
except Exception:
    pass
if getattr(sys, "frozen", False):
    os.environ["PATH"] = APP_DIR + os.pathsep + os.environ.get("PATH", "")

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(APP_DIR, "ms-playwright")

from PyQt6.QtWidgets import (
    QApplication, QComboBox, QMessageBox, QToolTip
)
from PyQt6.QtCore import (QSize, QTimer)
from PyQt6.QtGui import (QPalette, QIcon, QColor, QFont)
import warnings

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="openpyxl"
)

if __name__ == "__main__":

    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("HTSMercek")
        except Exception:
            pass
    app = QApplication(sys.argv)

    assets_path = os.path.join(APP_DIR, "assets")
    ico_path = os.path.join(assets_path, "app_icon.ico")
    png_path = os.path.join(assets_path, "logo.png")

    app_icon = QIcon()
    if os.path.exists(ico_path):
        for sz in (16, 24, 32, 48, 64, 128, 256):
            app_icon.addFile(ico_path, QSize(sz, sz))
    if os.path.exists(png_path):
        app_icon.addFile(png_path)

    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    tip_pal = QPalette()
    tip_pal.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    tip_pal.setColor(QPalette.ColorRole.ToolTipText, QColor("#2c3e50"))
    QToolTip.setPalette(tip_pal)
    QToolTip.setFont(QFont("Segoe UI", 10))

    app.setStyleSheet(QSS_LIGHT)
    _tooltip_mgr = TooltipManager(app)

    # ✅ AÇILIŞTA ONLINE ZORUNLU (NTP bootstrap)
    try:
        TrustedTimeGuard.bootstrap(require_online=True)
    except Exception as e:
        try:
            # ModernDialog varsa onu kullan
            if "ModernDialog" in globals():
                ModernDialog.show_error(None, "İnternet Gerekli", f"Uygulama açılışı için internet bağlantısı gereklidir.\n\nDetay: {e}")
            else:
                QMessageBox.critical(None, "İnternet Gerekli", f"Uygulama açılışı için internet bağlantısı gereklidir.\n\nDetay: {e}")
        finally:
            _quit_app()
        sys.exit(app.exec())  # quit timer'ı işlesin

    # ✅ Lisans kontrolü (yoksa kullanıcıya Lisans Yükle/Kapat seçeneği)
    try:
        _lic = LicenseManager.ensure_valid_or_raise()
    except Exception as e:
        msg = QMessageBox(None)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Lisans Gerekli")
        msg.setText("Lisans bulunamadı veya hatalı. Uygulama kapatılacak.")
        msg.setInformativeText(str(e))

        btn_load = msg.addButton("Lisans Yükle", QMessageBox.ButtonRole.AcceptRole)
        btn_exit = msg.addButton("Kapat", QMessageBox.ButtonRole.RejectRole)

        msg.setStyleSheet("""
            QMessageBox {
                background: #ffffff;
                font-family: "Segoe UI";
                font-size: 10.5pt;
            }
            QLabel { color: #1f2d3d; }
            QPushButton {
                background: #0f766e;
                color: white;
                border: 0px;
                padding: 8px 14px;
                border-radius: 8px;
                min-width: 110px;
            }
            QPushButton:hover { background: #115e59; }
        """)

        msg.exec()

        if msg.clickedButton() == btn_exit:
            _quit_app()
            sys.exit(app.exec())

        gate = LicenseGateDialog(None)
        if gate.exec() != 1:
            _quit_app()
            sys.exit(app.exec())

        try:
            _lic = LicenseManager.ensure_valid_or_raise()
        except Exception as ee:
            try:
                if "ModernDialog" in globals():
                    ModernDialog.show_error(None, "Lisans Hatası", f"Lisans doğrulaması başarısız.\n\nDetay: {ee}")
                else:
                    QMessageBox.critical(None, "Lisans Hatası", f"Lisans doğrulaması başarısız.\n\nDetay: {ee}")
            finally:
                _quit_app()
            sys.exit(app.exec())

    win = MainWindow()
    if not app_icon.isNull():
        win.setWindowIcon(app_icon)

    for cb in win.findChildren(QComboBox):
        try:
            apply_light_combobox_popup(cb)
        except Exception:
            pass

    # ✅ 6 saat sonra: uyarı -> OK -> restart
    _MAX_UPTIME_MS = 6 * 60 * 60 * 1000

    def _uptime_restart():
        try:
            if "ModernDialog" in globals():
                ModernDialog.show_warning(
                    win,
                    "Yeniden Başlatma",
                    "En fazla açık kalma sınırına ulaşıldı.\nProgram kendisini yeniden başlatacak."
                )
            else:
                QMessageBox.warning(
                    win,
                    "Yeniden Başlatma",
                    "En fazla açık kalma sınırına ulaşıldı.\nProgram kendisini yeniden başlatacak."
                )
        finally:
            restart_application()

    QTimer.singleShot(_MAX_UPTIME_MS, _uptime_restart)

    # ✅ Zaman manipülasyon kontrolü (5 dakikada bir)
    _guard_timer = QTimer(win)
    _guard_timer.setInterval(5 * 60 * 1000)

    def _tick_guard():
        try:
            TrustedTimeGuard.check_and_update()
            if TrustedTimeGuard.is_tampered():
                try:
                    if "ModernDialog" in globals():
                        ModernDialog.show_error(None, "Zaman Hatası", TrustedTimeGuard.tamper_reason())
                    else:
                        QMessageBox.critical(None, "Zaman Hatası", TrustedTimeGuard.tamper_reason())
                finally:
                    _quit_app()
        except Exception:
            # sessiz geç
            pass

    _guard_timer.timeout.connect(_tick_guard)
    _guard_timer.start()

    try:
        enforce_normal_table_fonts(win)
    except Exception:
        pass

    win.showMaximized()
    sys.exit(app.exec())