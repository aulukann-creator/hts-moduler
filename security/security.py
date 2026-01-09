import base64
import ctypes
import hashlib
import json
import os
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ui.dialog import ModernDialog
from time_utils.time_guard import TrustedTimeGuard

try:
    import winreg
except Exception:
    winreg = None
@dataclass(frozen=True)
class LicenseInfo:
    product: str
    license_id: str
    customer: str
    device: str
    exp: str
    features: list[str]


class SecurityGuard:
    """
    Uygulamanın güvenliğini artırır.
    Debugger (Hata ayıklayıcı) veya analiz araçlarını tespit eder.
    """
    @staticmethod
    def is_being_debugged() -> bool:
        """
        Windows API kullanarak programın bir debugger tarafından
        izlenip izlenmediğini kontrol eder.
        """
        try:
            # Kernel32 IsDebuggerPresent kontrolü
            if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
                return True

            # Uzaktan Debugger kontrolü (CheckRemoteDebuggerPresent)
            is_remote_debugger = ctypes.c_bool(False)
            process_handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.CheckRemoteDebuggerPresent(process_handle, ctypes.byref(is_remote_debugger))
            if is_remote_debugger.value:
                return True

        except Exception:
            pass
        return False


class CrashGuard:
    """
    Beklenmedik hataları yakalar, log dosyasına yazar ve
    kullanıcıya düzgün bir hata mesajı gösterir.
    """
    import traceback
    APP_NAME = "HTSMercek_Logs"

    @staticmethod
    def install():
        """Global hata yakalayıcıyı aktif eder."""
        sys.excepthook = CrashGuard._handle_exception

    @staticmethod
    def _handle_exception(exc_type, exc_value, exc_traceback):
        """Hata oluştuğunda tetiklenen fonksiyon."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 1. Hatayı Formatla
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # 2. Log Klasörü Oluştur (Belgelerim/HTSMercek_Logs)
        log_dir = os.path.join(os.path.expanduser("~"), "Documents", CrashGuard.APP_NAME)
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"crash_{timestamp}.txt")

        # 3. Dosyaya Yaz
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"--- HATA RAPORU ({timestamp}) ---\n")
                f.write(f"Ürün: HTS Mercek\n")
                f.write(f"Sistem: {sys.platform}\n\n")
                f.write(error_msg)
        except Exception:
            pass

        # 4. Kullanıcıya Bilgi Ver
        try:
            app = QApplication.instance()
            if app:
                short_error = str(exc_value)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Beklenmedik Hata")
                msg.setText("Programda beklenmedik bir hata oluştu ve kapatılması gerekiyor.")
                msg.setInformativeText(f"Hata Raporu şuraya kaydedildi:\n{log_file}\n\nHata Detayı:\n{short_error}")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        except:
            pass

        sys.exit(1)


class LicenseManager:
    PUBLIC_KEY_B64 = "yWxlAFxgu+xwxdD/0PBpmYggpHeZItx+4xw+FZ7PFEg="

    APP_DIR_NAME = "HTSMercek"
    LICENSE_FILENAME = "license.json"
    _fingerprint_cache: str | None = None

    @staticmethod
    def appdata_dir() -> str:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, LicenseManager.APP_DIR_NAME)
        os.makedirs(d, exist_ok=True)
        return d

    @staticmethod
    def license_path() -> str:
        return os.path.join(LicenseManager.appdata_dir(), LicenseManager.LICENSE_FILENAME)

    @staticmethod
    def device_fingerprint() -> str:
        """
        GÜVENLİK GÜNCELLEMESİ:
        Eski powershell yöntemi yerine Native Windows API ve Registry kullanır.
        Daha hızlıdır ve CMD/Powershell penceresi açmaz.
        """
        if LicenseManager._fingerprint_cache:
            return LicenseManager._fingerprint_cache

        # 1. Adım: MachineGuid (Registry)
        machine_guid = "UNKNOWN_GUID"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                val, _ = winreg.QueryValueEx(key, "MachineGuid")
                if val:
                    machine_guid = str(val).strip()
        except Exception:
            pass

        # 2. Adım: C Sürücüsü Seri Numarası (Kernel32 - Native)
        hdd_serial = 0
        try:
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
            serialNumber = ctypes.c_DWORD()
            maxComponentLength = ctypes.c_DWORD()
            fileSystemFlags = ctypes.c_DWORD()

            ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p("C:\\"),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                ctypes.byref(serialNumber),
                ctypes.byref(maxComponentLength),
                ctypes.byref(fileSystemFlags),
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer)
            )
            hdd_serial = serialNumber.value
        except Exception:
            pass

        # İkisini birleştir
        raw_id = f"{machine_guid}_{hdd_serial}".strip()
        fp = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

        LicenseManager._fingerprint_cache = fp
        return fp

    @staticmethod
    def _canonical_payload(d: dict) -> bytes:
        d2 = dict(d)
        d2.pop("sig", None)
        s = json.dumps(d2, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return s.encode("utf-8")

    @staticmethod
    def _verify_signature(payload: bytes, sig_b64: str) -> bool:
        try:
            pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(LicenseManager.PUBLIC_KEY_B64))
            sig = base64.b64decode(sig_b64)
            pub.verify(sig, payload)
            return True
        except Exception:
            return False

    @staticmethod
    def load_license_from_disk() -> dict | None:
        p = LicenseManager.license_path()
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def validate_license(d: dict) -> LicenseInfo:
        """
        Lisans verisini doğrular.
        GÜNCELLEME: Tarih kontrolü için TimeVerifier (NTP) kullanır.
        """
        if not isinstance(d, dict):
            raise ValueError("Lisans formatı hatalı.")
        if d.get("product") != "HTSMercek":
            raise ValueError("Lisans ürün adı uyuşmuyor.")
        if "sig" not in d or not isinstance(d["sig"], str):
            raise ValueError("İmza yok/bozuk (sig).")

        payload = LicenseManager._canonical_payload(d)
        if not LicenseManager._verify_signature(payload, d["sig"]):
            raise ValueError("İmza doğrulanamadı (dosya değiştirilmiş olabilir).")

        expected = LicenseManager.device_fingerprint()
        if d.get("device") != expected:
            # NOT: HWID algoritması değiştiği için eski lisanslar 'cihaz uyuşmazlığı' verecektir.
            # Yeni lisans üretmeniz gerekecek.
            raise ValueError("Bu lisans bu cihaza ait değil (Donanım Kimliği Uyuşmazlığı).")

        exp = d.get("exp", "")
        try:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("exp tarihi hatalı (YYYY-MM-DD olmalı).")

        # GÜVENLİ ZAMAN KONTROLÜ
        current_now = TrustedTimeGuard.now()
        if TrustedTimeGuard.is_tampered():
            raise ValueError(TrustedTimeGuard.tamper_reason())
        if current_now.date() > exp_date:
            raise ValueError("Lisans süresi dolmuş.")

        return LicenseInfo(
            product=d.get("product", ""),
            license_id=d.get("license_id", ""),
            customer=d.get("customer", ""),
            device=d.get("device", ""),
            exp=exp,
            features=list(d.get("features") or []),
        )

    @staticmethod
    def is_valid() -> bool:
        try:
            LicenseManager.ensure_valid_or_raise()
            return True
        except Exception:
            return False

    @staticmethod
    def ensure_valid_or_raise() -> "LicenseInfo":
        # --- GÜVENLİK KONTROLÜ ---
        # Sadece exe paketinde anti-debug uygula (dev/test sürecini kilitlemesin)
        if getattr(sys, "frozen", False):
            if SecurityGuard.is_being_debugged():
                # sys.exit(0) YERİNE: çağıran taraf ModernDialog ile gösterip kapatsın
                raise RuntimeError("Güvenlik ihlali: Debugger tespit edildi.")
        # --------------------------------------

        try:
            # exe paketinde online zorunlu; dev ortamında offline'a izin ver.
            require_online = bool(getattr(sys, "frozen", False))
            TrustedTimeGuard.bootstrap(require_online=require_online)
        except Exception as _tt_err:
            # Online zorunlu modda NTP alınamazsa bootstrap zaten hata verir.
            # Bu hatayı lisans hatası olarak yukarı taşımak istiyoruz.
            raise ValueError(str(_tt_err))
        # --------------------------------------

        d = LicenseManager.load_license_from_disk()
        if not d:
            raise ValueError("Lisans bulunamadı.")
        return LicenseManager.validate_license(d)

    @staticmethod
    def require_valid(
        parent=None,
        show_message: bool = True,
        exit_on_invalid: bool = False,
    ) -> bool:
        """UI tarafından kullanılan güvenli kontrol fonksiyonu. (DEĞİŞTİRİLMEDİ)"""
        try:
            LicenseManager.ensure_valid_or_raise()
            return True
        except Exception as e:
            if show_message:
                try:
                    # ModernDialog varsa onu kullanalım, yoksa standart MessageBox
                    try:
                        ModernDialog.show_error(parent, "Lisans Hatası", f"Lisans bulunamadı veya hatalı.\n\n{e}")
                    except:
                        msg = QMessageBox(parent)
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setWindowTitle("Lisans Hatası")
                        msg.setText("Lisans bulunamadı veya hatalı.")
                        msg.setInformativeText(str(e))
                        msg.exec()
                except Exception:
                    pass

            if exit_on_invalid:
                try:
                    QTimer.singleShot(0, QApplication.quit)
                except Exception:
                    pass
            return False

    @staticmethod
    def require_valid_or_exit(parent=None, context: str = "") -> bool:
        """Kritik işlemlerde kullanılan zorunlu kontrol. (DEĞİŞTİRİLMEDİ)"""
        try:
            LicenseManager.ensure_valid_or_raise()
            return True
        except Exception as e:
            extra = f"\n\nİşlem: {context}" if context else ""
            try:
                # ModernDialog varsa kullan, yoksa hata vermesin
                if 'ModernDialog' in globals():
                    ModernDialog.show_error(
                        parent,
                        "Lisans Hatası",
                        f"Lisans doğrulanamadı. Uygulama kapatılacak.{extra}\n\nDetay: {e}"
                    )
                else:
                    QMessageBox.critical(parent, "Lisans Hatası", f"Lisans geçersiz. Program kapatılıyor.\n{e}")
            finally:
                app = QApplication.instance()
                if app is not None:
                    QTimer.singleShot(0, app.quit)
            return False
