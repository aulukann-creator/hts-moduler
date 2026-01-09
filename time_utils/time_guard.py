import base64
import hashlib
import socket
import struct
import time
from datetime import datetime

try:
    import winreg
except Exception:
    winreg = None
class TimeVerifier:
    """
    Sistem saatine güvenmek yerine NTP sunucularından gerçek zamanı alır.
    İnternet yoksa mecburen sistem saatine döner.
    """
    NTP_SERVERS = ['pool.ntp.org', 'time.google.com', 'time.windows.com']

    @staticmethod
    def get_network_time(timeout=2):
        """NTP sunucularından güncel zamanı dener."""
        ntp_packet = bytearray(48)
        ntp_packet[0] = 0x1B

        for server in TimeVerifier.NTP_SERVERS:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                    client.settimeout(timeout)
                    client.sendto(ntp_packet, (server, 123))
                    data, address = client.recvfrom(48)

                    if data:
                        t = struct.unpack('!12I', data)[10]
                        t -= 2208988800 # 1900 -> 1970 epoch
                        return datetime.fromtimestamp(t)
            except Exception:
                continue
        return None

    @staticmethod
    def get_current_time():
        """Önce ağı dener, olmazsa sistem saatini döndürür."""
        net_time = TimeVerifier.get_network_time()
        return net_time if net_time else datetime.now()


class TrustedTimeStore:
    """
    Registry'de 'bariz tarih' içermeden güvenilir zaman damgasını saklar.
    Birden fazla yere yazar/okur (basit kopyala-yapıştır saldırılarını zorlaştırır).
    """
    ROOTS = [
        (winreg.HKEY_CURRENT_USER,  r"Software\Classes\.htsm"),
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"),
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]

    @staticmethod
    def _k(seed: str) -> bytes:
        h = hashlib.sha256(seed.encode("utf-8")).digest()
        return h

    @staticmethod
    def _xor(data: bytes, key: bytes) -> bytes:
        out = bytearray(len(data))
        for i, b in enumerate(data):
            out[i] = b ^ key[i % len(key)]
        return bytes(out)

    @staticmethod
    def _pack(epoch: int, seed: str) -> str:
        ep = struct.pack("!Q", max(0, int(epoch)))
        chk = hashlib.sha256(ep + seed.encode("utf-8")).digest()[:8]
        raw = ep + chk
        key = TrustedTimeStore._k(seed)
        enc = TrustedTimeStore._xor(raw, key)
        return base64.b64encode(enc).decode("ascii")

    @staticmethod
    def _unpack(token: str, seed: str) -> int | None:
        try:
            enc = base64.b64decode(token.encode("ascii"))
            key = TrustedTimeStore._k(seed)
            raw = TrustedTimeStore._xor(enc, key)
            if len(raw) != 16:
                return None
            ep = raw[:8]
            chk = raw[8:]
            exp_chk = hashlib.sha256(ep + seed.encode("utf-8")).digest()[:8]
            if chk != exp_chk:
                return None
            epoch = struct.unpack("!Q", ep)[0]
            return int(epoch)
        except Exception:
            return None

    @staticmethod
    def _value_name(seed: str, idx: int) -> str:
        h = hashlib.sha256(f"{seed}|{idx}".encode("utf-8")).hexdigest()
        return "v" + h[:12]

    @staticmethod
    def write(epoch: int, seed: str) -> None:
        token0 = TrustedTimeStore._pack(epoch, seed + "|a")
        token1 = TrustedTimeStore._pack(epoch, seed + "|b")
        token2 = TrustedTimeStore._pack(epoch, seed + "|c")

        tokens = [token0, token1, token2]
        if winreg is None:
            return  # veya uygun fallback
        for i, (root, path) in enumerate(TrustedTimeStore.ROOTS):
            try:
                with winreg.CreateKey(root, path) as k:
                    name = TrustedTimeStore._value_name(seed, i)
                    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, tokens[i % len(tokens)])
            except Exception:
                pass

    @staticmethod
    def read_best(epoch_floor: int, seed: str) -> int | None:
        """
        Birden fazla yerden okur, en büyük (en ileri) epoch'u döndürür.
        epoch_floor verilirse, ondan küçükleri yok sayar.
        """
        best = None
        for i, (root, path) in enumerate(TrustedTimeStore.ROOTS):
            try:
                with winreg.OpenKey(root, path) as k:
                    name = TrustedTimeStore._value_name(seed, i)
                    val, _ = winreg.QueryValueEx(k, name)
                    if not isinstance(val, str) or not val:
                        continue

                    for suffix in ("|a", "|b", "|c"):
                        ep = TrustedTimeStore._unpack(val, seed + suffix)
                        if ep is None:
                            continue
                        if int(epoch_floor) and ep < int(epoch_floor):
                            continue
                        if best is None or ep > best:
                            best = ep
            except Exception:
                continue
        return best

    @staticmethod
    def read_all_raw(seed: str) -> list[str]:
        """
        Kendi value'larımızın ham string değerlerini döndürür (digest için).
        Bulunamayanlar '' döner.
        """
        raws: list[str] = []
        for i, (root, path) in enumerate(TrustedTimeStore.ROOTS):
            try:
                with winreg.OpenKey(root, path) as k:
                    name = TrustedTimeStore._value_name(seed, i)
                    val, _ = winreg.QueryValueEx(k, name)
                    raws.append(val if isinstance(val, str) else "")
            except Exception:
                raws.append("")
        return raws

    @staticmethod
    def state_digest(seed: str) -> str:
        """
        Registry'deki 3 noktanın durum özetini (hash) üretir.
        RAM'de saklayıp değişiklikleri yakalamak için kullanılır.
        """
        raws = TrustedTimeStore.read_all_raw(seed)
        blob = ("|".join(raws)).encode("utf-8", errors="ignore")
        return hashlib.sha256(blob).hexdigest()


class TrustedTimeGuard:
    """
    - Uygulama açılışında NTP zorunlu (istersen kapatılabilir)
    - Güvenilir zamanı registry'ye yazar
    - Sanal saat: trusted_start + (perf_counter delta)
    - Sistem saati geri alınırsa tespit eder ve lisansı kilitler
    - EK: Registry durumunu RAM'de checksum ile izler (geri yükleme/silme tespiti)
    """
    _initialized = False
    _seed = ""
    _trusted_start_epoch = 0
    _perf_start = 0.0
    _last_persist_epoch = 0
    _last_ntp_try = 0.0
    _tamper = False
    _tamper_reason = ""

    # EK: bellek checksum
    _mem_digest = ""

    # toleranslar
    MAX_BACKWARD_SECONDS = 60         # 60 sn'den fazla geri -> manipülasyon
    PERSIST_EVERY_SECONDS = 10 * 60   # 10 dakikada bir registry tazele
    NTP_RETRY_MIN_SECONDS = 30 * 60   # 30 dakikada bir NTP dene (online ise)

    @staticmethod
    def _is_online() -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1.0).close()
            return True
        except Exception:
            return False

    @staticmethod
    def _refresh_mem_digest() -> None:
        try:
            TrustedTimeGuard._mem_digest = TrustedTimeStore.state_digest(TrustedTimeGuard._seed)
        except Exception:
            TrustedTimeGuard._mem_digest = ""

    @staticmethod
    def bootstrap(require_online: bool = True) -> None:
        """
        Program açılırken çağır: NTP al, registry yaz, sanal saati başlat.
        require_online=True ise NTP alamazsa uygulamayı açma mantığı.
        """
        from security.security import LicenseManager
        if TrustedTimeGuard._initialized:
            return

        fp = LicenseManager.device_fingerprint()
        TrustedTimeGuard._seed = hashlib.sha256(("HTSMercek|" + fp).encode("utf-8")).hexdigest()

        net_time = TimeVerifier.get_network_time(timeout=2)
        sys_dt = datetime.now()
        if net_time is not None:
            diff = abs((sys_dt - net_time).total_seconds())
            if diff > 10 * 60:
                raise RuntimeError(
                    "Sistem tarihi ile gerçek zaman arasında büyük fark var.\n"
                    "Lütfen sistem tarih/saat ayarlarınızı kontrol edin."
                )
        if require_online and net_time is None:
            raise RuntimeError("İnternet bağlantısı gerekli (lisans doğrulaması için tarih alınamadı).")

        now_dt = net_time if net_time else datetime.now()
        now_epoch = int(now_dt.timestamp())

        stored = TrustedTimeStore.read_best(epoch_floor=0, seed=TrustedTimeGuard._seed)
        if stored is not None and stored > now_epoch:
            now_epoch = stored

        # registry'ye yaz
        TrustedTimeStore.write(now_epoch, TrustedTimeGuard._seed)

        TrustedTimeGuard._trusted_start_epoch = now_epoch
        TrustedTimeGuard._perf_start = time.perf_counter()
        TrustedTimeGuard._last_persist_epoch = now_epoch
        TrustedTimeGuard._last_ntp_try = time.perf_counter()

        # EK: RAM digest
        TrustedTimeGuard._refresh_mem_digest()

        TrustedTimeGuard._initialized = True

    @staticmethod
    def now() -> datetime:
        if not TrustedTimeGuard._initialized:
            return datetime.now()
        delta = time.perf_counter() - TrustedTimeGuard._perf_start
        cur_epoch = TrustedTimeGuard._trusted_start_epoch + int(delta)
        return datetime.fromtimestamp(cur_epoch)

    @staticmethod
    def check_and_update() -> None:
        """
        Periyodik çağır:
        - sistem saati çok geri mi?
        - registry'deki zamanla tutarlı mı?
        - registry değerleri kurcalandı mı? (RAM digest)
        - online ise ara sıra NTP ile ileri güncelle
        """
        if not TrustedTimeGuard._initialized or TrustedTimeGuard._tamper:
            return

        virtual_now = TrustedTimeGuard.now()
        virtual_epoch = int(virtual_now.timestamp())

        # 0) EK: Registry snapshot/digest değişti mi?
        try:
            cur_digest = TrustedTimeStore.state_digest(TrustedTimeGuard._seed)
            if TrustedTimeGuard._mem_digest and cur_digest != TrustedTimeGuard._mem_digest:
                stored_best = TrustedTimeStore.read_best(epoch_floor=0, seed=TrustedTimeGuard._seed)
                # Registry geri alındı / silindi / eski snapshot yüklendi:
                rollback_tol = TrustedTimeGuard.PERSIST_EVERY_SECONDS + 30  # 10 dk + 30 sn güven payı

                if stored_best is None or stored_best < (virtual_epoch - rollback_tol):
                    TrustedTimeGuard._tamper = True
                    TrustedTimeGuard._tamper_reason = "Zaman kayıtları değiştirildi / geri yüklendi (registry manipülasyonu)."
                    return
                # başka instance yazmış olabilir -> kabul et, digest'i güncelle
                TrustedTimeGuard._mem_digest = cur_digest
        except Exception:
            pass

        # 1) Sistem saatini geri alma kontrolü (virtual'a göre)
        sys_epoch = int(datetime.now().timestamp())
        if sys_epoch < (virtual_epoch - TrustedTimeGuard.MAX_BACKWARD_SECONDS):
            TrustedTimeGuard._tamper = True
            TrustedTimeGuard._tamper_reason = "Sistem saati geri alındı / zaman manipülasyonu tespit edildi."
            return

        # 2) Registry en iyi değer (çok daha ileriyse registry'yi baz al)
        stored = TrustedTimeStore.read_best(epoch_floor=0, seed=TrustedTimeGuard._seed)
        if stored is not None and stored > (virtual_epoch + 120):
            TrustedTimeGuard._trusted_start_epoch = stored
            TrustedTimeGuard._perf_start = time.perf_counter()
            virtual_epoch = stored

        # 3) Periyodik persist (registry tazele)
        if (virtual_epoch - TrustedTimeGuard._last_persist_epoch) >= TrustedTimeGuard.PERSIST_EVERY_SECONDS:
            TrustedTimeStore.write(virtual_epoch, TrustedTimeGuard._seed)
            TrustedTimeGuard._last_persist_epoch = virtual_epoch
            TrustedTimeGuard._refresh_mem_digest()

        # 4) Online ise seyrek NTP refresh (ileri götürür)
        if TrustedTimeGuard._is_online():
            if (time.perf_counter() - TrustedTimeGuard._last_ntp_try) >= TrustedTimeGuard.NTP_RETRY_MIN_SECONDS:
                TrustedTimeGuard._last_ntp_try = time.perf_counter()
                ntp = TimeVerifier.get_network_time(timeout=2)
                if ntp:
                    ntp_epoch = int(ntp.timestamp())
                    if ntp_epoch > (virtual_epoch + 30):
                        TrustedTimeGuard._trusted_start_epoch = ntp_epoch
                        TrustedTimeGuard._perf_start = time.perf_counter()
                        TrustedTimeStore.write(ntp_epoch, TrustedTimeGuard._seed)
                        TrustedTimeGuard._last_persist_epoch = ntp_epoch
                        TrustedTimeGuard._refresh_mem_digest()

    @staticmethod
    def is_tampered() -> bool:
        return TrustedTimeGuard._tamper

    @staticmethod
    def tamper_reason() -> str:
        return TrustedTimeGuard._tamper_reason or "Zaman manipülasyonu tespit edildi."
