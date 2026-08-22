import json
import os
import hashlib
import urllib.parse
import urllib.request
import uuid
import requests
from datetime import date
from random import choice, randint, choices
from threading import Thread
from kivy.utils import platform
from random import randint, choice, choices
# =========================================================
# TEMPEL DI BARIS 14 (Menggantikan blok KivMob di fotomu)
# =========================================================

if platform == 'android':
    from jnius import autoclass, PythonJavaClass, java_method
    Activity = autoclass('org.kivy.android.PythonActivity').mActivity
    MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
    AdRequest = autoclass('com.google.android.gms.ads.AdRequest$Builder')
    RewardedAd = autoclass('com.google.android.gms.ads.rewarded.RewardedAd')
else:
    Activity = None

class KivyAdMobReward(PythonJavaClass if platform == 'android' else object):
    if platform == 'android':
        __javainterfaces__ = [
            'com/google/android/gms/ads/rewarded/RewardedAdLoadCallback',
            'com/google/android/gms/ads/OnUserEarnedRewardListener',
            'com/google/android/gms/ads/FullScreenContentCallback'
        ]
        __javacontext__ = 'app'

    def __init__(self, app_instance):
        if platform == 'android':
            super(KivyAdMobReward, self).__init__()
        self.app = app_instance
        self.rewarded_ad = None
        if platform == 'android':
            MobileAds.initialize(Activity)

    def load_rewarded_ad(self, ad_unit_id):
        if platform != 'android':
            return
        
        class LoadTask(PythonJavaClass):
            __javainterfaces__ = ['java/lang/Runnable']
            __javacontext__ = 'app'
            def __init__(self, wrapper, ad_id):
                super(LoadTask, self).__init__()
                self.wrapper = wrapper
                self.ad_id = ad_id
            
            @java_method('()V')
            def run(self):
                ad_req = AdRequest().build()
                RewardedAd.load(Activity, self.ad_id, ad_req, self.wrapper)
                
        Activity.runOnUiThread(LoadTask(self, ad_unit_id))

    if platform == 'android':
        @java_method('(Lcom/google/android/gms/ads/rewarded/RewardedAd;)V')
        def onAdLoaded(self, ad):
            self.rewarded_ad = ad
            self.rewarded_ad.setFullScreenContentCallback(self)

        @java_method('(Lcom/google/android/gms/ads/LoadAdError;)V')
        def onAdFailedToLoad(self, error):
            self.rewarded_ad = None
            Clock.schedule_once(lambda dt: self.app._iklan_gagal_load(error.getCode()), 0)

        @java_method('(Lcom/google/android/gms/ads/rewarded/RewardItem;)V')
        def onUserEarnedReward(self, reward):
            Clock.schedule_once(lambda dt: self.app._iklan_selesai(), 0)

        @java_method('()V')
        def onAdDismissedFullScreenContent(self):
            self.rewarded_ad = None
            if hasattr(self.app, 'ADMOB_REWARDED_ID'):
                self.load_rewarded_ad(self.app.ADMOB_REWARDED_ID)

        @java_method('(Lcom/google/android/gms/ads/AdError;)V')
        def onAdFailedToShowFullScreenContent(self, adError):
            self.rewarded_ad = None
            Clock.schedule_once(lambda dt: self.app._iklan_selesai(), 0)

    def show_rewarded_ad(self):
        if platform != 'android':
            Clock.schedule_once(lambda dt: self.app._iklan_selesai(), 0)
            return

        if self.rewarded_ad:
            class ShowTask(PythonJavaClass):
                __javainterfaces__ = ['java/lang/Runnable']
                __javacontext__ = 'app'
                def __init__(self, wrapper, ad):
                    super(ShowTask, self).__init__()
                    self.wrapper = wrapper
                    self.ad = ad
                
                @java_method('()V')
                def run(self):
                    self.ad.show(Activity, self.wrapper)
                    
            Activity.runOnUiThread(ShowTask(self, self.rewarded_ad))
        else:
            Clock.schedule_once(lambda dt: self.app._iklan_gagal_load("BELUM_READY"), 0)


# URL utama Firebase kamu
FIREBASE_URL = "https://triple8spin-default-rtdb.firebaseio.com"


# 1. FUNGSI UNTUK MENDAPATKAN ID UNIK PEMAIN (khusus HP ini)
def dapatkan_id_pemain():
    file_id = "user_id.txt"
    if os.path.exists(file_id):
        with open(file_id, "r") as f:
            return f.read().strip()
    else:
        id_baru = f"player_{uuid.uuid4().hex[:8]}"
        with open(file_id, "w") as f:
            f.write(id_baru)
        return id_baru

ID_PEMAIN = dapatkan_id_pemain()


# 2. FUNGSI KIRIM DATA ONLINE (VERSI AMAN / ANTI-CHEAT)
def simpan_data_online(id_pemain, data_dict):
    """Menyimpan saldo dan data pemain langsung ke Server Firebase"""
    if data_dict.get("poin_saat_ini", 0) < 0:
        data_dict["poin_saat_ini"] = 0

    try:
        url = f"{FIREBASE_URL}/pemain/{id_pemain}.json"
        response = requests.put(url, json=data_dict, timeout=5)

        if response.status_code == 200:
            print("[FIREBASE] Data berhasil disimpan secara online!")
            return True
        else:
            print("Gagal simpan ke Firebase:", response.status_code)
            return False
    except Exception as e:
        print("Koneksi internet bermasalah, gagal terhubung ke server:", e)
        return False


# 3. FUNGSI AMBIL DATA ONLINE
def muat_data_online(id_pemain):
    """Membaca saldo pemain langsung dari Server Firebase"""
    try:
        url = f"{FIREBASE_URL}/pemain/{id_pemain}.json"
        response = requests.get(url, timeout=5)

        if response.status_code == 200 and response.json() is not None:
            print("[FIREBASE] Data berhasil dimuat dari server!")
            return response.json()
        else:
            print("Buka pemain baru / data tidak ditemukan.")
            return None
    except Exception as e:
        print("Gagal mengambil data online:", e)
        return None


# ==============================================
# KONFIGURASI GOOGLE ADMOB (TEST ID RESMI GOOGLE)
# ==============================================
ADMOB_APP_ID      = "ca-app-pub-3940256099942544~3347511713"  # Test App ID
ADMOB_BANNER_ID   = "ca-app-pub-3940256099942544/6300978111"  # Test Banner ID
ADMOB_REWARDED_ID = "ca-app-pub-3940256099942544/5224354917"  # Test Rewarded ID

# ==============================================
# KONFIGURASI PENGAMAN DATA
# ==============================================
KUNCI_RAHASIA = "KEY_cicak_didinding"
FILE_DATA = "data_pemain.json"

def buat_hash(data_dict):
    data_to_hash = {k: v for k, v in data_dict.items() if k != 'checksum'}
    data_str = json.dumps(data_to_hash, sort_keys=True)
    return hashlib.sha256((data_str + KUNCI_RAHASIA).encode()).hexdigest()

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.network.urlrequest import UrlRequest
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

# ==============================================
# DATA BOT TELEGRAM
# ==============================================
TELEGRAM_TOKEN = "8990109821:AAHmHqcatGW-Oh1gTG7AscDwNhESWJGyQ4w"
TELEGRAM_CHAT_ID = "6837620159"

def kirim_notif_telegram(pesan):
    def send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = urllib.parse.urlencode(
                {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": pesan,
                    "parse_mode": "Markdown",
                }
            ).encode("utf-8")
            req = urllib.request.Request(url, data=payload)
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"Gagal kirim notif Telegram: {e}")

    Thread(target=send, daemon=True).start()

# ==============================================
# KONFIGURASI GAME & TAMPILAN
# ==============================================
Window.clearcolor = (0.07, 0.07, 0.07, 1)

SUARA_MUSIK = True
SUARA_EFEK = True
BAHASA = "ID"

def format_uang(rp, lang="ID"):
    if lang == "EN":
        usd = rp / 15000
        if usd < 0.01 and usd > 0:
            return f"${usd:.4f}"
        return f"${usd:.2f}"
    return f"Rp {rp:,}".replace(",", ".")

TEKS = {
    "ID": {
        "promo_win": "[color=ffffff]Raih Kemenangan Hingga [/color][color=34d399]5x POIN![/color]",
        "judul": "[color=34d399]LUCKY[/color][color=fbbf24]8[/color] [color=ffffff]SPIN[/color]",
        "bermain": "BERMAIN SLOT",
        "jackpot_3": "[color=34d399]JACKPOT 3x '8'! +{}[/color]",
        "hoki_2": "[color=34d399]HOKI 2x '8'! +{}[/color]",
        "dapat_1": "[color=34d399]DAPAT 1x '8'! +{}[/color]",
        "kembar_3": "[color=fbbf24]3 KEMBAR! BONUS +30 POIN[/color]",
        "kembar_2": "[color=fbbf24]2 KEMBAR! BONUS +10 POIN[/color]",
        "zonk": "[color=888888]ZONK! Belum beruntung.[/color]",
        "hoki_bonus": "[color=fbbf24]HOKI! HADIAHMU DILIPATGANDAKAN {x}x!\nBonus Tambahan +{poin} POIN![/color]",
        "dapat_bonus": "[color=fbbf24]SELAMAT! KAMU MENDAPAT +{} POIN![/color]",
        "bonus_iklan_wajib": "[color=fbbf24][+] Bonus Iklan Wajib: +{} POIN ditambahkan![/color]",
        "iklan": "BONUS IKLAN",
        "tarik": "TARIK UANG",
        "riwayat": "RIWAYAT",
        "status_proses": "PROSES (1x24 JAM)",
        "dukungan": "DUKUNGAN",
        "catatan": "CATATAN",
        "pengaturan_suara": "PENGATURAN SUARA",
        "tombol_suara": "SUARA",
        "musik_on": "MUSIK LATAR: ON",
        "musik_off": "MUSIK LATAR: OFF",
        "efek_on": "SUARA TOMBOL & EFEK: ON",
        "efek_off": "SUARA TOMBOL & EFEK: OFF",
        "masukkan_taruhan": "DAPATKAN [color=fbbf24]POIN[/color] IKLAN, TUKAR MENJADI [color=34d399]HADIAH[/color] PADA LUCKY [color=fbbf24]888[/color] SPIN",
        "proses_wd": "PROSES 1x24 JAM PENARIKAN",
        "saldo": "SALDO POIN : {} [color=fbbf24]POIN[/color] | [color=34d399]PENGHASILAN : {}[/color]",
        "stat": "MENANG : {}x | TARIK HARI INI : {}/{}",
        "tunggu": "Memuat Iklan... Mohon Tunggu",
        "taruhan": "Taruhan Poin (Min 10)",
        "kembali": "KEMBALI",
        "isi_angka": "MASUKKAN TARUHAN DULU!",
        "batas_taruh": "MINIMAL TARUHAN 10 POIN!",
        "poin_kurang": "POIN TIDAK CUKUP!",
        "pilih_nominal": "MENU PENARIKAN SALDO",
        "taruh_kurang": "PENGHASILAN TIDAK MENCUKUPI!",
        "id_kosong": "MASUKKAN ID / NO HP DULU!",
        "batas_hari": "BATAS TARIK HARI INI HABIS!",
        "proses_detail": "PENARIKAN {} VIA {} SEDANG DIPROSES. MOHON TUNGGU 1x24 JAM.",
        "ubah_bahasa": "ENGLISH",
        "isi_id": "No. OVO / ID Binance",
        "tanpa_riwayat": "Belum ada riwayat penarikan.",
        "pilih_kotak": "PILIH 1 KOTAK HADIAH UNTUK KLAIM BONUS!",
        "kotak_nama": "KOTAK",
        "ambil_hadiah": "AMBIL HADIAH & KEMBALI",
        "nonton_lagi": "KLAIM LAGI",
        "gandakan_poin": ">> LIPAT GANDAKAN POIN (2x - 5x)",
        "welcome_title": "WELCOME BONUS PEMAIN BARU!",
        "welcome_desc": "Selamat datang! Ambil bonus awalmu untuk mulai bermain slot!",
        "welcome_claim": "KLAIM +500 POIN SEKARANG",
        "status_guest": "[color=888888]Status: Akun Tamu (Guest)[/color]",
        "status_member": "[color=34d399]Status: Terdaftar ({})[/color]",
        "teks_catatan": "CATATAN & ATURAN SLOT LUCKY 8:\n\n1. Konversi: 10 POIN = Rp 1 Nilai Dasar.\n2. Muncul 1x Angka 8 = Rp 1 x (Taruhan/10)\n3. Muncul 2x Angka 8 = Rp 2 x (Taruhan/10)\n4. Muncul 3x Angka 8 = Rp 5 x (Taruhan/10) [JACKPOT]\n5. 3 Angka Kembar non-8 = +30 POIN\n6. 2 Angka Kembar non-8 = +10 POIN",
        "teks_dukungan": "BANTUAN & DUKUNGAN:\n\nJika mengalami kendala, hubungi:\nEmail: support@lucky8slot.com\nVersi Game: 2.1.0\nTerima kasih telah bermain!",
    },
    "EN": {
        "promo_win": "[color=ffffff]Win Up to [/color][color=34d399]5x POINTS![/color]",
        "judul": "[color=34d399]LUCKY[/color][color=fbbf24]8[/color] [color=ffffff]SPIN[/color]",
        "bermain": "PLAY SLOT",
        "jackpot_3": "[color=34d399]JACKPOT 3x '8'! +{}[/color]",
        "hoki_2": "[color=34d399]LUCKY 2x '8'! +{}[/color]",
        "dapat_1": "[color=34d399]GOT 1x '8'! +{}[/color]",
        "kembar_3": "[color=fbbf24]3 OF A KIND! BONUS +30 PTS[/color]",
        "kembar_2": "[color=fbbf24]2 OF A KIND! BONUS +10 PTS[/color]",
        "zonk": "[color=888888]ZONK! No luck this time.[/color]",
        "hoki_bonus": "[color=fbbf24]LUCKY! YOUR REWARD IS MULTIPLIED BY {x}x!\nExtra Bonus +{poin} POINTS![/color]",
        "dapat_bonus": "[color=fbbf24]CONGRATS! YOU GOT +{} POINTS![/color]",
        "bonus_iklan_wajib": "[color=fbbf24][+] Bonus: +{} POINTS added![/color]",
        "iklan": "BONUS POIN",
        "tarik": "WITHDRAW",
        "riwayat": "HISTORY",
        "status_proses": "PROCESSING (1x24 HOURS)",
        "dukungan": "SUPPORT",
        "catatan": "NOTES",
        "pengaturan_suara": "SOUND SETTINGS",
        "tombol_suara": "SOUNDS",
        "musik_on": "BG MUSIC: ON",
        "musik_off": "BG MUSIC: OFF",
        "efek_on": "BUTTON & FX SOUND: ON",
        "efek_off": "BUTTON & FX SOUND: OFF",
        "masukkan_taruhan": "GET [color=fbbf24]POINTS[/color], EXCHANGE FOR [color=34d399]REWARDS[/color] ON LUCKY [color=fbbf24]888[/color] SPIN",
        "proses_wd": "WITHDRAWAL PROCESS 1x24 HOURS",
        "saldo": "BALANCE POINT : {} [color=fbbf24]PTS[/color] | [color=34d399]CASH : {}[/color]",
        "stat": "WIN : {}x | WITHDRAW TODAY : {}/{}",
        "tunggu": "Loading Ads... Please Wait",
        "taruhan": "Bet Points (Min 10)",
        "kembali": "BACK",
        "isi_angka": "ENTER BET FIRST!",
        "batas_taruh": "MINIMUM BET IS 10 POINTS!",
        "poin_kurang": "NOT ENOUGH POINTS!",
        "pilih_nominal": "WITHDRAWAL MENU",
        "taruh_kurang": "EARNINGS NOT ENOUGH!",
        "id_kosong": "ENTER ID / PHONE NO FIRST!",
        "batas_hari": "DAILY LIMIT REACHED!",
        "proses_detail": "WITHDRAWAL OF {} VIA {} IS BEING PROCESSED. PLEASE WAIT 1x24 HOURS.",
        "ubah_bahasa": "BAHASA ID",
        "isi_id": "OVO No. / Binance ID",
        "tanpa_riwayat": "No withdrawal history yet.",
        "pilih_kotak": "PICK 1 MYSTERY BOX TO CLAIM BONUS!",
        "kotak_nama": "BOX",
        "ambil_hadiah": "CLAIM REWARD & RETURN",
        "nonton_lagi": "CLAIM AGAIN",
        "gandakan_poin": ">> MULTIPLY POINTS (2x - 5x)",
        "welcome_title": "NEW PLAYER WELCOME BONUS!",
        "welcome_desc": "Welcome! Claim your starter bonus to play slots now!",
        "welcome_claim": "CLAIM +500 POINTS NOW",
        "status_guest": "[color=888888]Status: Guest Account[/color]",
        "status_member": "[color=34d399]Status: Registered ({})[/color]",
        "teks_catatan": "LUCKY 8 SLOT RULES:\n\n1. Conversion: 10 POINTS = Rp 1 Base Value.\n2. Hit 1x Number 8 = Rp 1 x (Bet/10)\n3. Hit 2x Number 8 = Rp 2 x (Bet/10)\n4. Hit 3x Number 8 = Rp 5 x (Bet/10) [JACKPOT]\n5. 3 Triple non-8 = +30 POINTS\n6. 2 Double non-8 = +10 POINTS",
        "teks_dukungan": "HELP & SUPPORT:\n\nIf you have issues, contact:\nEmail: support@lucky8slot.com\nVersi Game: 2.1.0\nThank you for playing!",
    },
}

DAFTAR_ID = [
    "User_7821 baru saja mencairkan Rp 1.000 via OVO!",
    "Player_3902 berhasil mendapat JACKPOT 8.8.8!",
    "User_1109 baru saja mencairkan Rp 500 via BINANCE!",
    "Player_8843 mengklaim Bonus +500 POIN!",
    "User_5512 baru saja mencairkan Rp 100 via OVO!",
]
DAFTAR_EN = [
    "User_7821 just withdrew Rp 1.000 via OVO!",
    "Player_3902 hit JACKPOT 8.8.8!",
    "User_1109 just withdrew Rp 500 via BINANCE!",
    "Player_8843 claimed +500 POINTS Bonus!",
    "User_5512 just withdrew Rp 1.000 via OVO!",
]

def data_pemain_default():
    return {
        "poin_saat_ini": 1000,
        "penghasilan": 0,
        "jumlah_menang": 0,
        "jumlah_penarikan_hari_ini": 0,
        "tanggal_terakhir_penarikan": "",
        "riwayat_penarikan": [],
        "welcome_claimed": False,
        "no_hp": "",
    }

def muat_data():
    """Muat data LOKAL dulu (instan, tidak perlu tunggu internet).
    Data online disinkronkan belakangan lewat sinkronkan_data_online()."""
    default = data_pemain_default()
    if not os.path.exists(FILE_DATA):
        return default
    try:
        with open(FILE_DATA, "r") as f:
            data = json.load(f)
            if data.get('checksum') != buat_hash(data):
                return default
            return {**default, **data}
    except Exception:
        return default

def sinkronkan_data_online(callback_selesai=None):
    """Ambil data dari Firebase di background thread, supaya tidak bikin
    tampilan macet menunggu koneksi internet."""
    def tugas():
        data_online = muat_data_online(ID_PEMAIN)
        if data_online:
            data_gabungan = {**data_pemain_default(), **data_online}
            pemain.update(data_gabungan)
            simpan_data(pemain)
        if callback_selesai:
            Clock.schedule_once(lambda dt: callback_selesai(), 0)
    Thread(target=tugas, daemon=True).start()

def simpan_data(data):
    try:
        data['checksum'] = buat_hash(data)
        with open(FILE_DATA, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

pemain = muat_data()
MAKSIMAL_TARIK = 5

suara_klik = suara_benar = suara_putar = suara_poin = musik_latar = None

def muat_suara():
    global suara_klik, suara_benar, suara_putar, suara_poin, musik_latar
    try:
        if os.path.exists("poin.wav"):
            suara_poin = SoundLoader.load("poin.wav")
        if os.path.exists("klik.mp3"):
            suara_klik = SoundLoader.load("klik.mp3")
        if os.path.exists("benar.mp3"):
            suara_benar = SoundLoader.load("benar.mp3")
        if os.path.exists("putar.mp3"):
            suara_putar = SoundLoader.load("putar.mp3")
        if os.path.exists("soundtrack.mp3"):
            musik_latar = SoundLoader.load("soundtrack.mp3")
            if musik_latar:
                musik_latar.loop = True
                musik_latar.volume = 0.3 if SUARA_MUSIK else 0
                musik_latar.play()
    except Exception:
        pass
def update_musik():
    try:
        if musik_latar:
            musik_latar.volume = 0.3 if SUARA_MUSIK else 0
    except Exception:
        pass

def mainkan_poin():
    if not SUARA_EFEK or not suara_poin:
        return
    try:
        if suara_poin.state == 'play':
            suara_poin.stop()
        suara_poin.play()
    except Exception:
        pass

def mainkan_klik():
    try:
        if SUARA_EFEK and suara_klik:
            suara_klik.play()
    except Exception:
        pass

def mainkan_benar():
    try:
        if SUARA_EFEK and suara_benar:
            suara_benar.play()
    except Exception:
        pass

def mainkan_putar():
    if not SUARA_EFEK or not suara_putar:
        return
    try:
        suara_putar.volume = 1.0
        if suara_putar.state == 'play':
            suara_putar.stop()
        suara_putar.play()
    except Exception:
        pass

def hentikan_putar():
    try:
        if suara_putar:
            suara_putar.stop()
    except Exception:
        pass

def format_item_slot(item, is_mid=False, pos="center"):
    item_str = str(item)
    if is_mid:
        if item_str == '8':
            val = "[color=fbbf24]8[/color]"
        else:
            val = f"[color=ffffff]{item_str}[/color]"

        if pos == "left":
            return f"[color=fbbf24]>[/color]  {val}"
        elif pos == "right":
            return f"{val}  [color=fbbf24]<[/color]"
        else:
            return val
    else:
        if item_str == '8':
            return f"[color=fbbf24]{item_str}[/color]"
        else:
            return f"[color=888888]{item_str}[/color]"

class CardBox(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[28])
        self.bind(pos=self.up, size=self.up)

    def up(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Tombol(Button):
    def __init__(self, bg_color=(0.98, 0.42, 0.55, 1), **kw):
        on_press_func = kw.pop("on_press", None)
        super().__init__(**kw)
        if on_press_func:
            self.bind(on_press=on_press_func)

        self.font_size = "13sp"
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self.bg_color_obj = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[24])
        self.bind(pos=self.up, size=self.up)

    def up(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Input(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.font_size = "18sp"
        self.bold = True
        self.halign = "center"
        self.foreground_color = (0.83, 0.68, 0.21, 1)  # Warna Gold/Emas
        self.background_color = (0.2, 0.2, 0.2, 1)     # Abu-abu gelap
        self.background_normal = ''
        self.background_active = ''
        self.multiline = False
        self.padding = [10, 8, 10, 8]

class RewardsHandler(RewardedListenerInterface):
    def __init__(self, app_ref):
        self.app_ref = app_ref

    def on_rewarded(self, reward_name, reward_amount):
        pass

    def on_rewarded_video_ad_started(self):
        pass

    def on_rewarded_video_ad_completed(self):
        Clock.schedule_once(
            lambda dt: getattr(self.app_ref, "_iklan_selesai", lambda: None)(), 0
        )

    def on_rewarded_video_ad_closed(self):
        # Otomatis muat ulang rewarded ad saat iklan ditutup
        if platform == 'android' and getattr(self.app_ref, 'ads', None):
            try:
                self.app_ref.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
            except Exception as e:
                print(f"Gagal memuat ulang iklan: {e}")

    def on_rewarded_video_ad_failed_to_load(self, error_code):
        Clock.schedule_once(
            lambda dt: getattr(self.app_ref, "_iklan_gagal_load", lambda err=error_code: None)(error_code), 0
        )

# ==============================================
# KELAS UTAMA APLIKASI
# ==============================================
class Aplikasi(App):
    def on_start(self):
        self.ads_error = None
        if platform == 'android':
            try:
                self.ads = KivMob(ADMOB_APP_ID)
                self.ads.new_banner(ADMOB_BANNER_ID, True)
                self.ads.request_banner()
                self.ads.show_banner()

                self.ads.set_rewarded_ad_listener(RewardsHandler(self))
                self.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
            except Exception as e:
                print(f"Gagal Inisialisasi AdMob: {e}")
                self.ads = None
        else:
            self.ads = None

        sinkronkan_data_online(lambda: getattr(self, "simpan_tampil", lambda: None)())
        
        self.cek_internet()
        Clock.schedule_interval(self.cek_internet, 5)

    def cek_internet(self, *args):
        UrlRequest(
            "https://clients3.google.com/generate_204", 
            on_success=self.koneksi_lancar,
            on_failure=self.koneksi_terputus,
            on_error=self.koneksi_terputus,
            timeout=3
        )

    def koneksi_lancar(self, req, result):
        if hasattr(self, 'popup_internet') and self.popup_internet:
            self.popup_internet.dismiss()
            self.popup_internet = None

    def koneksi_terputus(self, req, error):
        if not getattr(self, 'popup_internet', None):
            teks_peringatan = Label(
                text="[color=ffb822]TIDAK ADA KONEKSI INTERNET![/color]\n\nHarap nyalakan Data/WiFi\nuntuk melanjutkan permainan.",
                markup=True,
                halign="center"
            )
            self.popup_internet = Popup(
                title="Koneksi Terputus",
                title_color=(0.83, 0.68, 0.21, 1),
                separator_color=(0.83, 0.68, 0.21, 1),
                content=teks_peringatan,
                size_hint=(0.85, 0.4),
                auto_dismiss=False 
            )
            self.popup_internet.open()

    def build(self):
        Clock.schedule_once(lambda d: muat_suara(), 0.5)
        self.ADMOB_REWARDED_ID = "ca-app-pub-3940256099942544/5224354917"
        self.ads = KivyAdMobReward(self)
        self.ads.load_rewarded_ad(self.ADMOB_REWARDED_ID)
        self.popup_internet = None 
        self.ticker = None
        self.metode_terpilih = "OVO"
        self.nominal_terpilih = 5000
        self.sisa_auto = 0
        self.bonus_kotak_terakhir = 0
        self.spin_gratis_tersisa = 5
         # 1. Inisialisasi variabel status iklan
        self._iklan_sudah_jalan = False
        self._iklan_lanjut_fungsi = None
        self._iklan_beri_bonus = False
        
        # 2. Inisialisasi AdMob (Pastikan ADMOB_REWARDED_ID sudah didefinisikan)
        self.ADMOB_REWARDED_ID = "ca-app-pub-3940256099942544/5224354917" # Ganti dengan ID asli Anda
        self.ads = KivyAdMobReward(self)
        self.ads.load_rewarded_ad(self.ADMOB_REWARDED_ID)

        l = BoxLayout(orientation="vertical", padding=10, spacing=6)

        # 1. LOGO ATAS
        file_judul = "logo_judul.png" if os.path.exists("logo_judul.png") else None
        if file_judul:
            self.judul = Image(
                source=file_judul,
                size_hint_y=None,
                height='60dp',
                allow_stretch=True,
                keep_ratio=True,
            )
            l.add_widget(self.judul)
        else:
            self.lbl_head = Label(
                text="[b][color=34d399]TRIPLE[/color][color=fbbf24]8[/color] [color=ffffff]SPIN[/color][/b]",
                markup=True,
                font_size="22sp",
                size_hint_y=None,
                height='45dp'
            )
            l.add_widget(self.lbl_head)

        # 2. AREA KHUSUS IKLAN BANNER (Premium Dark Theme)
        self.banner_ad_container = BoxLayout(
            size_hint_y=None,
            height='50dp',
            padding=[4, 2, 4, 2]
        )
        
        with self.banner_ad_container.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.rect_ad = RoundedRectangle(pos=self.banner_ad_container.pos, size=self.banner_ad_container.size, radius=[8])
            Color(0.83, 0.68, 0.21, 1)
            self.line_ad = Line(rounded_rectangle=(self.banner_ad_container.x, self.banner_ad_container.y, self.banner_ad_container.width, self.banner_ad_container.height, 8), width=1)
        
        self.banner_ad_container.bind(
            pos=lambda inst, val: setattr(self.rect_ad, 'pos', val) or setattr(self.line_ad, 'rounded_rectangle', (val[0], val[1], inst.width, inst.height, 8)),
            size=lambda inst, val: setattr(self.rect_ad, 'size', val) or setattr(self.line_ad, 'rounded_rectangle', (inst.x, inst.y, val[0], val[1], 8))
        )

        lbl_placeholder = Label(
            text="[color=888888][ AREA IKLAN BANNER ][/color]",
            markup=True,
            font_size="11sp",
            halign="center"
        )
        self.banner_ad_container.add_widget(lbl_placeholder)
        l.add_widget(self.banner_ad_container)

        # 3. SALDO & STATUS
        self.saldo_lbl = Label(
            text="",
            markup=True,
            font_size="12sp",
            size_hint_y=None,
            height='40dp',
            halign="center",
        )
        
        with self.saldo_lbl.canvas.before:
            Color(0.15, 0.15, 0.18, 0.9)
            self.bg_saldo = RoundedRectangle(
                pos=self.saldo_lbl.pos, 
                size=self.saldo_lbl.size, 
                radius=[8,]
            )
            
        def update_bg_saldo(instance, value):
            self.bg_saldo.pos = instance.pos
            self.bg_saldo.size = instance.size
            
        self.saldo_lbl.bind(pos=update_bg_saldo, size=update_bg_saldo)
        l.add_widget(self.saldo_lbl)

        # 4. KOTAK KONTEN UTAMA
        self.utama = CardBox(
            orientation="vertical", padding=[8, 45, 8, 8], spacing=4, size_hint_y=1.0
        )
        self.utama.bg_color.rgba = (0.08, 0.08, 0.08, 1)
        self.btn_poin_cepat = Tombol(
            text=TEKS[BAHASA]["iklan"],
            bg_color=(0.85, 0.55, 0, 1),
            font_size="12sp",
            size_hint_y=None,
            height='36dp',
        )
        self.btn_poin_cepat.bind(on_press=lambda b: getattr(self, "dapat_poin", lambda: None)())
        self.utama.add_widget(self.btn_poin_cepat)

        self.info = Label(
            text="",
            markup=True,
            font_size="10sp",
            size_hint_y=0.12,
            halign="center",
            valign="middle",
        )
        self.info.bind(size=self.info.setter("text_size"))
        self.utama.add_widget(self.info)

        self.slot_notif = BoxLayout(size_hint_y=0.06)

        self.berita = Label(
            text="", markup=True, font_size="11sp", halign="center",
            color=(0.9, 0.9, 0.9, 1),
        )
        with self.berita.canvas.before:
            self.berita_bg_color = Color(0.15, 0.15, 0.15, 1)
            self.berita_bg = RoundedRectangle(
                pos=self.berita.pos, size=self.berita.size, radius=[14]
            )
        self.berita.bind(
            pos=lambda inst, val: setattr(self.berita_bg, "pos", val),
            size=lambda inst, val: setattr(self.berita_bg, "size", val),
        )
        
        self.slot_notif.add_widget(self.berita)
        self.utama.add_widget(self.slot_notif)

        self.pemisah = Widget(size_hint_y=None, height="2dp")
        with self.pemisah.canvas:
            Color(0.83, 0.68, 0.21, 1)
            self.pemisah_line = Line(points=[0, 0, 0, 0], width=1.2)
        self.pemisah.bind(pos=self._update_pemisah if hasattr(self, '_update_pemisah') else lambda *a: None, 
                          size=self._update_pemisah if hasattr(self, '_update_pemisah') else lambda *a: None)

        # Dashboard Promo
        self.banner_promo = CardBox(
            orientation="vertical",
            padding=8,
            spacing=4,
            size_hint_y=0.42
        )
        self.banner_promo.bg_color.rgba = (0.12, 0.12, 0.12, 1)

        self.lbl_jackpot_title = Label(
            text="[b][color=fbbf24]= GRAND JACKPOT =[/color][/b]",
            markup=True,
            font_size="15sp",
            halign="center",
            size_hint_y=0.25
        )
        
        self.lbl_jackpot_num = Label(
            text="[b][color=34d399]>[/color] [color=fbbf24]8  8  8[/color] [color=34d399]<[/color][/b]",
            markup=True,
            font_size="32sp",
            halign="center",
            size_hint_y=0.50
        )
        
        self.lbl_jackpot_sub = Label(
            text=TEKS[BAHASA]["promo_win"],
            markup=True,
            font_size="11sp",
            halign="center",
            size_hint_y=0.25
        )

        self.banner_promo.add_widget(self.lbl_jackpot_title)
        self.banner_promo.add_widget(self.lbl_jackpot_num)
        self.banner_promo.add_widget(self.lbl_jackpot_sub)

        # Slot Matrix 3x3 Interaktif dengan Bingkai
        self.box_slot = GridLayout(
            cols=3, rows=3, spacing=4, size_hint_y=0.42, padding=[8, 8, 8, 8]
        )
        
        with self.box_slot.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.rect_slot = RoundedRectangle(pos=self.box_slot.pos, size=self.box_slot.size, radius=[12])
            Color(0.83, 0.68, 0.21, 1)
            self.line_slot = Line(rounded_rectangle=(self.box_slot.x, self.box_slot.y, self.box_slot.width, self.box_slot.height, 12), width=1)
            
        self.box_slot.bind(
            pos=lambda inst, val: setattr(self.rect_slot, 'pos', val) or setattr(self.line_slot, 'rounded_rectangle', (val[0], val[1], inst.width, inst.height, 12)),
            size=lambda inst, val: setattr(self.rect_slot, 'size', val) or setattr(self.line_slot, 'rounded_rectangle', (inst.x, inst.y, val[0], val[1], 12))
        )

        self.slot_top1 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)
        self.slot_top2 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)
        self.slot_top3 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)

        self.slot1 = Label(text="[color=fbbf24]>[/color]  [color=fbbf24]8[/color]", font_size="42sp", bold=True, halign="center", markup=True)
        self.slot2 = Label(text="[color=fbbf24]8[/color]", font_size="42sp", bold=True, halign="center", markup=True)
        self.slot3 = Label(text="[color=fbbf24]8[/color]  [color=fbbf24]<[/color]", font_size="42sp", bold=True, halign="center", markup=True)

        self.slot_bot1 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)
        self.slot_bot2 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)
        self.slot_bot3 = Label(text="[[] 8 ]", font_size="26sp", color=(0.6, 0.6, 0.6, 0.6), bold=True, halign="center", markup=True)

        self.box_slot.add_widget(self.slot_top1)
        self.box_slot.add_widget(self.slot_top2)
        self.box_slot.add_widget(self.slot_top3)

        self.box_slot.add_widget(self.slot1)
        self.box_slot.add_widget(self.slot2)
        self.box_slot.add_widget(self.slot3)

        self.box_slot.add_widget(self.slot_bot1)
        self.box_slot.add_widget(self.slot_bot2)
        self.box_slot.add_widget(self.slot_bot3)

        self.utama.add_widget(self.banner_promo)

        self.layar = BoxLayout(orientation="vertical", spacing=10, size_hint_y=0.40)
        self.utama.add_widget(self.layar)
        l.add_widget(self.utama)

        Clock.schedule_once(lambda d: getattr(self, "mulai_loading", lambda: None)(), 0.1)

        return l
    def ganti_bahasa(self, b):
        global BAHASA
        BAHASA = "EN" if BAHASA == "ID" else "ID"
        self.lbl_jackpot_sub.text = TEKS[BAHASA]["promo_win"]
        if hasattr(self, "mulai_menu"):
            self.mulai_menu()

    def set_info_sementara(self, pesan, durasi=3.5):
        self.info.text = pesan
        Clock.unschedule(self._bersihkan_info)
        Clock.schedule_once(self._bersihkan_info, durasi)

    def _bersihkan_info(self, dt):
        self.info.text = ""

    def tunggu_iklan(self, lanjut_fungsi, beri_bonus=False):
        self._iklan_sudah_jalan = False
        self._iklan_lanjut_fungsi = lanjut_fungsi
        self._iklan_beri_bonus = beri_bonus

        if hasattr(self, 'ads') and self.ads:
            # Panggil iklan
            self.ads.show_rewarded_ad()
        else:
            # Bypass jika ads gagal diinisialisasi
            self._iklan_selesai()

    def set_info_sementara(self, pesan, durasi=3.5):
        if hasattr(self, 'info'):
            self.info.text = pesan
            Clock.schedule_once(lambda dt: setattr(self.info, 'text', ''), durasi)


        # Batas waktu tunggu supaya tidak macet jika di PC atau jika iklan belum siap
        timeout = 6 if ad_shown else 0.8
        Clock.schedule_once(lambda d: getattr(self, "_iklan_selesai", lambda: None)(), timeout)
        
     def _iklan_selesai(self):
        if getattr(self, '_iklan_sudah_jalan', False):
            return
        self._iklan_sudah_jalan = True

        lanjut_fungsi = self._iklan_lanjut_fungsi
        beri_bonus = self._iklan_beri_bonus
        bonus_poin = 0
        if beri_bonus:
            bonus_poin = randint(20, 80)
            pemain["poin_saat_ini"] += bonus_poin
            mainkan_poin()
            self.simpan_tampil()

        lanjut_fungsi()

        if beri_bonus and bonus_poin > 0:
            msg = TEKS[BAHASA]["bonus_iklan_wajib"].format(bonus_poin)
            self.set_info_sementara(msg, 3.5)

        if hasattr(self, 'ads'):
            try:
                self.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
            except Exception:
                pass
                
        if getattr(self, 'ads_error', None):
            self.ads_error = None
                
    # --- PENAMBAHAN FUNGSI POPUP ERROR IKLAN ---
    def tampilkan_popup_error(self, judul, pesan):
        box = BoxLayout(orientation='vertical', padding=10, spacing=15)
        lbl = Label(text=pesan, halign='center', markup=True, font_size="13sp")
        btn = Button(
            text="Tutup", 
            size_hint_y=0.4, 
            background_normal='', 
            background_color=(0.8, 0.2, 0.2, 1) # Tombol merah
        )
        box.add_widget(lbl)
        box.add_widget(btn)
        
        pop = Popup(
            title=judul, 
            title_color=(1, 0.8, 0, 1), # Judul emas
            content=box, 
            size_hint=(0.8, 0.4),
            background_color=(0.1, 0.1, 0.1, 1) # Latar popup gelap
        )
        btn.bind(on_release=pop.dismiss)
        pop.open()

    def _iklan_gagal_load(self, error_code):
        self.ads_error = f"Kode Error AdMob: {error_code}"
        print(self.ads_error)
        
        # Munculkan Kivy Popup di Thread UI
        pesan_error = (
            f"Gagal memuat iklan (Error {error_code}).\n"
            "Pastikan koneksi internet Anda stabil\natau coba lagi beberapa saat."
        )
        Clock.schedule_once(
            lambda dt: self.tampilkan_popup_error("Iklan Belum Tersedia", pesan_error), 
            0.5
        )

    def simpan_tampil(self):
        tgl = str(date.today())
        if not pemain.get("sudah_klaim_bonus", False):
            pemain["poin_saat_ini"] += 500
            pemain["sudah_klaim_bonus"] = True
        if pemain["tanggal_terakhir_penarikan"] != tgl:
            pemain["jumlah_penarikan_hari_ini"] = 0
            pemain["tanggal_terakhir_penarikan"] = tgl


        str_uang = format_uang(pemain["penghasilan"], BAHASA)
        self.saldo_lbl.text = (
            "[b]"
            + TEKS[BAHASA]["saldo"].format(pemain["poin_saat_ini"], str_uang)
            + "[/b]\n"
            + TEKS[BAHASA]["stat"].format(
                pemain["jumlah_menang"],
                pemain["jumlah_penarikan_hari_ini"],
                MAKSIMAL_TARIK,
            )
        )
        simpan_data(pemain)

        data_kirim = dict(pemain)
        Thread(target=simpan_data_online, args=(ID_PEMAIN, data_kirim), daemon=True).start()

    def set_slot_3x3(self, top, mid, bot):
        self.slot_top1.text = format_item_slot(top[0], False)
        self.slot_top2.text = format_item_slot(top[1], False)
        self.slot_top3.text = format_item_slot(top[2], False)

        self.slot1.text = format_item_slot(mid[0], True, "left")
        self.slot2.text = format_item_slot(mid[1], True, "center")
        self.slot3.text = format_item_slot(mid[2], True, "right")

        self.slot_bot1.text = format_item_slot(bot[0], False)
        self.slot_bot2.text = format_item_slot(bot[1], False)
        self.slot_bot3.text = format_item_slot(bot[2], False)

    def tampilkan_banner_promo(self):
        if self.box_slot in self.utama.children:
            self.utama.remove_widget(self.box_slot)
        if self.banner_promo not in self.utama.children:
            self.utama.add_widget(self.banner_promo, index=1)
        self.slot_notif.size_hint_y = 0.06
        self.info.size_hint_y = 0.12
        self.info.font_size = "10sp"
        try:
            self.utama.remove_widget(self.pemisah)
        except Exception:
            pass
        
    def _update_pemisah(self, inst, val):
        y = inst.y + inst.height / 2
        self.pemisah_line.points = [inst.x, y, inst.x + inst.width, y]

    def tampilkan_grid_slot(self):
        if self.banner_promo in self.utama.children:
            self.utama.remove_widget(self.banner_promo)
        if self.box_slot not in self.utama.children:
            self.utama.add_widget(self.box_slot, index=1)
        
        # BARIS 879 & 880 (clear_widgets dan add_widget btn_poin_cepat) DIHAPUS DARI SINI
        
        self.box_slot.size_hint_y = 0.58
        self.info.size_hint_y = 0.16
        self.info.font_size = "10sp"
        if self.pemisah not in self.utama.children:
            self.utama.add_widget(self.pemisah, index=1)
      
#_________________________________
    def layar_welcome_bonus(self):
        mainkan_benar()
        self.layar.clear_widgets()
        self.info.text = (
            "[color=fbbf24]" + TEKS[BAHASA]["welcome_desc"] + "[/color]" # Ubah ke warna emas
        )

        box_bonus = BoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=0.85
        )

        file_peti = "peti.png" if os.path.exists("peti.png") else ("peti.jpg" if os.path.exists("peti.jpg") else None)

        if file_peti:
            img_peti = Image(
                source=file_peti,
                size_hint_y=0.65,
                allow_stretch=True,
                keep_ratio=True
            )
            box_bonus.add_widget(img_peti)
        else:
            lbl_gift = Label(
                text="[+]\n[b][color=fbbf24]+500 POIN[/color][/b]",
                markup=True,
                font_size="28sp",
                halign="center",
            )
            box_bonus.add_widget(lbl_gift)

        btn_klaim = Tombol(
            text=TEKS[BAHASA]["welcome_claim"],
            bg_color=(0.85, 0.55, 0, 1), # Emas elegan
            font_size="15sp",
            size_hint_y=0.35,
        )
        def klaim_welcome(b):
            mainkan_benar()
            pemain["poin_saat_ini"] += 500
            pemain["welcome_claimed"] = True
            self.simpan_tampil()
            self.mulai_menu()                               
                                                        
        btn_klaim.bind(on_press=klaim_welcome)
        box_bonus.add_widget(btn_klaim)

        self.layar.add_widget(box_bonus)

    def mulai_menu(self):
        self.asal_halaman = "menu"
        mainkan_klik()
        self.sisa_auto = 0
        self.slot_notif.clear_widgets()
        self.slot_notif.add_widget(self.berita)
        self.layar.clear_widgets()
        self.simpan_tampil()
        self.info.text = TEKS[BAHASA]["masukkan_taruhan"]
        
        self.tampilkan_banner_promo()
        self.utama.canvas.ask_update()
        Window.canvas.ask_update()

        if self.ticker:
            self.ticker.cancel()
        daftar = DAFTAR_ID if BAHASA == "ID" else DAFTAR_EN
        self.ticker = Clock.schedule_interval(
            lambda d: setattr(self.berita, "text", choice(daftar)), 3.5
        )

        baris_opsi = BoxLayout(spacing=12, size_hint_y=0.20)
        self.btn_bahasa = Tombol(
            text=TEKS[BAHASA]["ubah_bahasa"], bg_color=(0.2, 0.2, 0.2, 1) # Abu gelap
        )
        self.btn_bahasa.bind(on_press=self.ganti_bahasa)

        self.btn_suara = Tombol(
            text=TEKS[BAHASA]["tombol_suara"], bg_color=(0.2, 0.2, 0.2, 1) # Abu gelap
        )
        self.btn_suara.bind(on_press=lambda b: self.menu_suara())

        baris_opsi.add_widget(self.btn_bahasa)
        baris_opsi.add_widget(self.btn_suara)
        self.layar.add_widget(baris_opsi)

        b1 = Tombol(
            text=TEKS[BAHASA]["bermain"],
            bg_color=(0.85, 0.55, 0, 1), # Emas solid untuk tombol utama
            font_size="18sp",
            size_hint_y=0.28,
        )
        b1.bind(
            on_press=lambda b: self.tunggu_iklan(
                self.buka_permainan, beri_bonus=True
            )
        )
        self.layar.add_widget(b1)

        baris_fitur = BoxLayout(spacing=12, size_hint_y=0.25)
        
        # Pastikan b3 didefinisikan dengan benar
        b3 = Tombol(
            text=TEKS[BAHASA]["tarik"], 
            bg_color=(0.15, 0.15, 0.15, 1) # Gelap
        )
        b3.bind(on_press=lambda b: self.menu_tarik())
        
        # Hapus baris add_widget(b2) dan pastikan hanya b3 yang ditambahkan
        baris_fitur.add_widget(b3)
        self.layar.add_widget(baris_fitur)


        baris_info = BoxLayout(spacing=12, size_hint_y=0.25)
        b_catatan = Tombol(
            text=TEKS[BAHASA]["catatan"], bg_color=(0.12, 0.12, 0.12, 1)
        )
        b_catatan.bind(on_press=lambda b: self.menu_catatan())
        b_dukungan = Tombol(
            text=TEKS[BAHASA]["dukungan"], bg_color=(0.12, 0.12, 0.12, 1)
        )
        b_dukungan.bind(on_press=lambda b: self.menu_dukungan())
        baris_info.add_widget(b_catatan)
        baris_info.add_widget(b_dukungan)
        self.layar.add_widget(baris_info)

    def menu_suara(self):
        if self.ticker:
            self.ticker.cancel()
        self.slot_notif.clear_widgets()
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = (
            "[color=fbbf24]" + TEKS[BAHASA]["pengaturan_suara"] + "[/color]"
        )

        box_suara = BoxLayout(
            orientation="vertical", spacing=8, size_hint_y=0.85
        )

        txt_m = (
            TEKS[BAHASA]["musik_on"] if SUARA_MUSIK else TEKS[BAHASA]["musik_off"]
        )
        color_m = (0.16, 0.65, 0.38, 1) if SUARA_MUSIK else (0.6, 0.15, 0.15, 1) # Merah gelap
        btn_m = Tombol(text=txt_m, bg_color=color_m, size_hint_y=0.30)

        txt_e = TEKS[BAHASA]["efek_on"] if SUARA_EFEK else TEKS[BAHASA]["efek_off"]
        color_e = (0.16, 0.65, 0.38, 1) if SUARA_EFEK else (0.6, 0.15, 0.15, 1)
        btn_e = Tombol(text=txt_e, bg_color=color_e, size_hint_y=0.30)

        def toggle_musik(b):
            global SUARA_MUSIK
            SUARA_MUSIK = not SUARA_MUSIK
            update_musik()
            mainkan_klik()
            self.menu_suara()

        def toggle_efek(b):
            global SUARA_EFEK
            SUARA_EFEK = not SUARA_EFEK
            mainkan_klik()
            self.menu_suara()

        btn_m.bind(on_press=toggle_musik)
        btn_e.bind(on_press=toggle_efek)

        box_suara.add_widget(btn_m)
        box_suara.add_widget(btn_e)

        kmb = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.2, 0.2, 0.2, 1), # Abu gelap
            size_hint_y=0.30,
        )
        kmb.bind(on_press=lambda b: self.mulai_menu())
        box_suara.add_widget(kmb)

        self.layar.add_widget(box_suara)
        
    def tutup_hadiah(self, *args):
        if getattr(self, 'asal_halaman', 'menu') == "slot":
            self.buka_permainan()
        else:
            self.mulai_menu()


    def buka_permainan(self):
        self.asal_halaman = "slot"
        if self.ticker:
            self.ticker.cancel()

        self.tampilkan_grid_slot()

        self.info.text = "[color=888888]Tekan SPIN untuk mulai![/color]"

        self.set_slot_3x3(['?', '?', '?'], ['?', '?', '?'], ['?', '?', '?'])
        self.taruhan = 10
        self.sisa_auto = 0
        self.klik_spin1_counter = 0

        self.tampilkan_kontrol_spin()

    def tampilkan_kontrol_spin(self):
        self.layar.clear_widgets()

        self.input_taruh = Input(
            text=str(self.taruhan),
            hint_text=TEKS[BAHASA]["taruhan"],
            size_hint_y=0.18,
            background_normal='',
            background_active='',
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(0.83, 0.68, 0.21, 1)
        )

        lbl_taruhan = Label(
            text="[color=888888]JUMLAH TARUHAN[/color]",
            markup=True, font_size="12sp", size_hint_y=0.05, halign="center"
        )
        self.layar.add_widget(lbl_taruhan)
        self.layar.add_widget(self.input_taruh)

        self.b_spin1 = Tombol(
            text="SPIN 1x", bg_color=(0.85, 0.55, 0, 1), size_hint_y=0.25 # Tombol Spin utama Emas
        )
        self.b_spin1.bind(on_press=lambda b: self.cek_dan_spin(1))
        self.layar.add_widget(self.b_spin1)

        grid_auto = GridLayout(cols=3, spacing=4, size_hint_y=0.25)
        # Warna gradasi abu-abu untuk Auto Spin
        warna_auto = [(0.25, 0.25, 0.25, 1), (0.25, 0.25, 0.25, 1), (0.25, 0.25, 0.25, 1)]
        for (count, warna) in zip([10, 50, 100], warna_auto):
            btn = Tombol(text=f"{count}x", bg_color=warna)
            btn.bind(on_press=lambda inst, c=count: self.cek_dan_spin(c))
            grid_auto.add_widget(btn)
        self.layar.add_widget(grid_auto)

        kmb = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.1, 0.1, 0.1, 1),
            size_hint_y=0.22,
        )
        kmb.bind(
            on_press=lambda b: self.tunggu_iklan(self.mulai_menu, beri_bonus=True)
        )
        self.layar.add_widget(kmb)
        
            def cek_dan_spin(self, jumlah_spin):
        try:
            self.taruhan = int(self.input_taruh.text.strip())
        except Exception:
            self.info.text = "[color=f87171]" + TEKS[BAHASA]["isi_angka"] + "[/color]"
            return

        if self.taruhan < 10:
            self.info.text = (
                "[color=f87171]" + TEKS[BAHASA]["batas_taruh"] + "[/color]"
            )
            return

        if pemain["poin_saat_ini"] < self.taruhan:
            self.info.text = (
                "[color=f87171]" + TEKS[BAHASA]["poin_kurang"] + "[/color]"
            )
            return

        if self.sisa_auto > 0:
            self.sisa_auto = 0
            return

        if jumlah_spin == 1:
            self.klik_spin1_counter += 1
            if self.klik_spin1_counter % 10 == 0:
                self.tunggu_iklan(
                    lambda: self._mulai_spin_setelah_iklan(jumlah_spin),
                    beri_bonus=True,
                )
                return
            self._mulai_spin(jumlah_spin)
        else:
            self.tunggu_iklan(
                lambda: self._mulai_spin_setelah_iklan(jumlah_spin), beri_bonus=True
            )

    def _mulai_spin(self, jumlah_spin):
        self.sisa_auto = jumlah_spin
        self.b_spin1.text = "STOP"
        self.jalan_loop_spin()

    def _mulai_spin_setelah_iklan(self, jumlah_spin):
        self.tampilkan_kontrol_spin()
        self._mulai_spin(jumlah_spin)

    def jalan_loop_spin(self):
        if self.sisa_auto <= 0 or pemain["poin_saat_ini"] < self.taruhan:
            self.sisa_auto = 0
            self.simpan_tampil()
            return

        pemain["poin_saat_ini"] -= self.taruhan
        self.simpan_tampil()

        self.langkah_sisa = 15
        mainkan_putar()
        self.jalankan_animasi_putar()

    def jalankan_animasi_putar(self):
        if self.langkah_sisa > 0:
            top_rand = [randint(0, 9), randint(0, 9), randint(0, 9)]
            mid_rand = [randint(0, 9), randint(0, 9), randint(0, 9)]
            bot_rand = [randint(0, 9), randint(0, 9), randint(0, 9)]
            
            self.set_slot_3x3(top_rand, mid_rand, bot_rand)
            self.langkah_sisa -= 1
            Clock.schedule_once(lambda dt: self.jalankan_animasi_putar(), 0.08)
        else:
            self.kalkulasi_hasil_slot()


    def kalkulasi_hasil_slot(self):
        simbol = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        bobot  = [9.6, 9.6, 9.6, 9.6, 9.6, 9.6, 9.6, 9.6, 13.5, 9.3]

        top_res = [randint(0, 9), randint(0, 9), randint(0, 9)]
        mid_res = choices(simbol, weights=bobot, k=3)
        bot_res = [randint(0, 9), randint(0, 9), randint(0, 9)]

        self.set_slot_3x3(top_res, mid_res, bot_res)

        d1, d2, d3 = mid_res[0], mid_res[1], mid_res[2]
        digits = [d1, d2, d3]
        count_8 = digits.count(8)

        nilai_dasar_rp = self.taruhan // 10
        hentikan_putar()

        if count_8 >= 1:
            mainkan_benar()
            
            if count_8 == 3:
                hadiah_rp = nilai_dasar_rp * 5
            elif count_8 == 2:
                hadiah_rp = nilai_dasar_rp * 2
            else:
                hadiah_rp = nilai_dasar_rp * 1

            pemain["penghasilan"] += hadiah_rp
            pemain["jumlah_menang"] += 1
            
            uang_str = format_uang(hadiah_rp, BAHASA)

            if count_8 == 3:
                pesan = TEKS[BAHASA]["jackpot_3"].format(uang_str)
            elif count_8 == 2:
                pesan = TEKS[BAHASA]["hoki_2"].format(uang_str)
            else:
                pesan = TEKS[BAHASA]["dapat_1"].format(uang_str)

            self.info.text = pesan
        elif d1 == d2 == d3:
            mainkan_poin()
            pemain["poin_saat_ini"] += 30
            self.info.text = TEKS[BAHASA]["kembar_3"]
        elif d1 == d2 or d2 == d3 or d1 == d3:
            mainkan_poin()
            pemain["poin_saat_ini"] += 10
            self.info.text = TEKS[BAHASA]["kembar_2"]
        else:
            self.info.text = TEKS[BAHASA]["zonk"]

        self.simpan_tampil()
        self.sisa_auto -= 1

        if self.sisa_auto > 0 and pemain["poin_saat_ini"] >= self.taruhan:
            self.b_spin1.text = "STOP"
            Clock.schedule_once(lambda dt: self.jalan_loop_spin(), 0.5)
        else:
            self.b_spin1.text = "SPIN 1x"

    def dapat_poin(self):
        self.tunggu_iklan(self.layar_kotak_hadiah, beri_bonus=False)

    def layar_kotak_hadiah(self):
        if self.ticker:
            self.ticker.cancel()
        self.slot_notif.clear_widgets()
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = "[color=fbbf24]" + TEKS[BAHASA]["pilih_kotak"] + "[/color]"

        self.sudah_buka_kotak = False
        self.bonus_kotak_terakhir = 0

        grid_kotak = BoxLayout(spacing=8, size_hint_y=0.55, padding=[4, 4, 4, 4])

        for i in range(1, 4):
            btn = Tombol(
                text=f"[BOX]\n{TEKS[BAHASA]['kotak_nama']} {i}",
                bg_color=(0.83, 0.68, 0.21, 1), # Emas Gelap
                font_size="14sp",
            )
            btn.bind(on_press=lambda inst, b=btn: self.buka_kotak_hadiah(b))
            grid_kotak.add_widget(btn)

        self.layar.add_widget(grid_kotak)

        self.btn_ganda = Tombol(
            text=TEKS[BAHASA]["gandakan_poin"],
            bg_color=(0.6, 0.15, 0.15, 1), # Merah Gelap Elegan
            size_hint_y=0.22,
        )
        self.btn_ganda.bind(
            on_press=lambda b: self.tunggu_iklan(
                self.proses_ganda_poin, beri_bonus=False
            )
        )

        self.btn_klaim_kembali = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.2, 0.2, 0.2, 1),
            size_hint_y=0.22,
        )
        self.btn_klaim_kembali.bind(on_press=self.tutup_hadiah)

        self.layar.add_widget(self.btn_klaim_kembali)

    def buka_kotak_hadiah(self, btn):
        if self.sudah_buka_kotak:
            return

        self.sudah_buka_kotak = True
        mainkan_klik()

        self.bonus_kotak_terakhir = randint(10, 20)
        pemain["poin_saat_ini"] += self.bonus_kotak_terakhir
        mainkan_poin()
        self.simpan_tampil()

        btn.text = f"[+]\n+{self.bonus_kotak_terakhir}\nPOIN!"
        btn.bg_color_obj.rgba = (0.16, 0.65, 0.38, 1)

        self.info.text = TEKS[BAHASA]["dapat_bonus"].format(self.bonus_kotak_terakhir)

        self.layar.remove_widget(self.btn_klaim_kembali)
        self.layar.add_widget(self.btn_ganda)
        self.btn_klaim_kembali.text = TEKS[BAHASA]["ambil_hadiah"]
        self.btn_klaim_kembali.bg_color_obj.rgba = (0.16, 0.65, 0.38, 1)
        self.layar.add_widget(self.btn_klaim_kembali)

    def proses_ganda_poin(self):
        if self.bonus_kotak_terakhir <= 0:
            self.mulai_menu()
            return

        mainkan_klik()
        pengganda = randint(2, 5)
        poin_tambahan = self.bonus_kotak_terakhir * (pengganda - 1)
        pemain["poin_saat_ini"] += poin_tambahan
        self.simpan_tampil()
        mainkan_poin()
        teks_template = TEKS[BAHASA]["hoki_bonus"]
        self.info.text = teks_template.format(
            x=pengganda, 
            poin=poin_tambahan
        )

        self.layar.clear_widgets()
        
        box_opsi = BoxLayout(orientation="vertical", spacing=8, size_hint_y=0.7)
        
        btn_nonton_lagi = Tombol(
            text=TEKS[BAHASA]["nonton_lagi"],
            bg_color=(0.83, 0.68, 0.21, 1), # Emas gelap
            font_size="15sp",
            size_hint_y=0.5,
        )
        btn_nonton_lagi.bind(on_press=lambda b: self.dapat_poin())

        btn_selesai = Tombol(
            text=TEKS[BAHASA]["ambil_hadiah"],
            bg_color=(0.16, 0.65, 0.38, 1),
            font_size="15sp",
            size_hint_y=0.5,
        )
        btn_selesai.bind(on_press=self.tutup_hadiah)

        
        box_opsi.add_widget(btn_nonton_lagi)
        box_opsi.add_widget(btn_selesai)
        
        self.layar.add_widget(box_opsi)

    def menu_tarik(self):
        mainkan_klik()
        self.sisa_auto = 0
        self.layar.clear_widgets()

        if pemain.get("no_hp"):
            txt_status = TEKS[BAHASA]["status_member"].format(pemain["no_hp"])
        else:
            txt_status = TEKS[BAHASA]["status_guest"]

        self.info.text = (
            "[color=fbbf24]"
            + TEKS[BAHASA]["pilih_nominal"]
            + f"[/color]\n{txt_status}"
        )

        self.metode_terpilih = "OVO"
        self.nominal_terpilih = 100

        no_default = pemain.get("no_hp", "")
        self.input_id_tarik = Input(
            text=no_default, hint_text=TEKS[BAHASA]["isi_id"], size_hint_y=0.20
        )
        self.layar.add_widget(self.input_id_tarik)

        baris_metode = BoxLayout(spacing=6, size_hint_y=0.20)
        self.btn_ovo = Tombol(text="OVO [V]", bg_color=(0.3, 0.3, 0.3, 1))
        self.btn_binance = Tombol(text="BINANCE", bg_color=(0.15, 0.15, 0.15, 1))

        def pilih_m(m):
            mainkan_klik()
            self.metode_terpilih = m
            self.btn_ovo.text = "OVO [V]" if m == "OVO" else "OVO"
            self.btn_ovo.bg_color_obj.rgba = (0.3, 0.3, 0.3, 1) if m == "OVO" else (0.15, 0.15, 0.15, 1)
            self.btn_binance.text = "BINANCE [V]" if m == "BINANCE" else "BINANCE"
            self.btn_binance.bg_color_obj.rgba = (0.3, 0.3, 0.3, 1) if m == "BINANCE" else (0.15, 0.15, 0.15, 1)

        self.btn_ovo.bind(on_press=lambda b: pilih_m("OVO"))
        self.btn_binance.bind(on_press=lambda b: pilih_m("BINANCE"))
        baris_metode.add_widget(self.btn_ovo)
        baris_metode.add_widget(self.btn_binance)
        self.layar.add_widget(baris_metode)

        v100 = format_uang(100, BAHASA)
        v500 = format_uang(500, BAHASA)
        v1000 = format_uang(1000, BAHASA)

        baris_nom = BoxLayout(spacing=6, size_hint_y=0.20)
        self.btn_n100 = Tombol(text=f"{v100} [V]", bg_color=(0.3, 0.3, 0.3, 1))
        self.btn_n500 = Tombol(text=v500, bg_color=(0.15, 0.15, 0.15, 1))
        self.btn_n1000 = Tombol(text=v1000, bg_color=(0.15, 0.15, 0.15, 1))

        def pilih_n(n, btn):
            mainkan_klik()
            self.nominal_terpilih = n
            self.btn_n100.text = format_uang(100, BAHASA)
            self.btn_n500.text = format_uang(500, BAHASA)
            self.btn_n1000.text = format_uang(1000, BAHASA)
            
            # Reset warna tombol
            self.btn_n100.bg_color_obj.rgba = (0.15, 0.15, 0.15, 1)
            self.btn_n500.bg_color_obj.rgba = (0.15, 0.15, 0.15, 1)
            self.btn_n1000.bg_color_obj.rgba = (0.15, 0.15, 0.15, 1)
            
            # Highlight tombol terpilih
            btn.text = f"{format_uang(n, BAHASA)} [V]"
            btn.bg_color_obj.rgba = (0.3, 0.3, 0.3, 1)

        self.btn_n100.bind(on_press=lambda b: pilih_n(100, self.btn_n100))
        self.btn_n500.bind(on_press=lambda b: pilih_n(500, self.btn_n500))
        self.btn_n1000.bind(on_press=lambda b: pilih_n(1000, self.btn_n1000))
        baris_nom.add_widget(self.btn_n100)
        baris_nom.add_widget(self.btn_n500)
        baris_nom.add_widget(self.btn_n1000)
        self.layar.add_widget(baris_nom)

        baris_aksi = BoxLayout(spacing=6, size_hint_y=0.22)
        btn_submit = Tombol(text=TEKS[BAHASA]["tarik"], bg_color=(0.85, 0.55, 0, 1)) # Emas
        btn_submit.bind(on_press=lambda b: self.proses_tarik_detail())

        btn_riwayat = Tombol(
            text=TEKS[BAHASA]["riwayat"], bg_color=(0.2, 0.2, 0.2, 1) # Abu gelap
        )
        btn_riwayat.bind(on_press=lambda b: self.menu_riwayat())

        btn_kembali = Tombol(
            text=TEKS[BAHASA]["kembali"], bg_color=(0.1, 0.1, 0.1, 1) # Sangat gelap
        )
        btn_kembali.bind(
            on_press=lambda b: self.tunggu_iklan(self.mulai_menu, beri_bonus=True)
        )

        baris_aksi.add_widget(btn_submit)
        baris_aksi.add_widget(btn_riwayat)
        baris_aksi.add_widget(btn_kembali)
        self.layar.add_widget(baris_aksi)
#___________________________________

    def proses_tarik_detail(self):
        no_id = self.input_id_tarik.text.strip()
        if not no_id:
            self.info.text = "[color=f87171]" + TEKS[BAHASA]["id_kosong"] + "[/color]"
            return

        if not pemain.get("no_hp"):
            pemain["no_hp"] = no_id

        nom = self.nominal_terpilih
        str_nom = format_uang(nom, BAHASA)

        if pemain["penghasilan"] < nom:
            self.info.text = (
                "[color=f87171]" + TEKS[BAHASA]["taruh_kurang"] + "[/color]"
            )
        elif pemain["jumlah_penarikan_hari_ini"] >= MAKSIMAL_TARIK:
            self.info.text = (
                "[color=fbbf24]" + TEKS[BAHASA]["batas_hari"] + "[/color]"
            )
        else:
            pemain["penghasilan"] -= nom
            pemain["jumlah_penarikan_hari_ini"] += 1

            pesan_ui = TEKS[BAHASA]["proses_detail"].format(
                str_nom, self.metode_terpilih
            )
            self.info.text = "[color=34d399]" + pesan_ui + "[/color]"

            pemain["riwayat_penarikan"].insert(
                0,
                {
                    "tanggal": str(date.today()),
                    "nominal": str_nom,
                    "metode": self.metode_terpilih,
                    "status": "status_proses",
                },
            )
            pemain["riwayat_penarikan"] = pemain["riwayat_penarikan"][:10]

            pesan_telegram = (
                "[NOTIF] PERMINTAAN PENARIKAN SALDO!\n\n"
                f"ID / No. HP: {no_id}\n"
                f"Nominal: {str_nom}\n"
                f"Metode: {self.metode_terpilih}\n"
                f"Tanggal: {date.today()}\n\n"
                "Segera lakukan transfer ke akun pemain di atas."
            )
            kirim_notif_telegram(pesan_telegram)

        self.simpan_tampil()

    def menu_riwayat(self):
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = (
            "[color=fbbf24]" + TEKS[BAHASA]["proses_wd"] + "[/color]"
        )

        box_r = BoxLayout(
            orientation="vertical", spacing=4, padding=4, size_hint_y=0.75
        )

        if not pemain["riwayat_penarikan"]:
            box_r.add_widget(
                Label(
                    text=TEKS[BAHASA]["tanpa_riwayat"],
                    font_size="13sp",
                    color=(0.6, 0.6, 0.6, 1),
                    halign="center",
                )
            )
        else:
            for item in pemain["riwayat_penarikan"][:4]:
                status_teks = TEKS[BAHASA].get(item['status'], item['status'])
                txt = (
                    f"- {item['tanggal']} | {item['nominal']} ({item['metode']}) -\n"
                    f"[color=34d399]{status_teks}[/color]"
                )
                box_r.add_widget(
                    Label(
                        text=txt,
                        markup=True,
                        font_size="11sp",
                        size_hint_y=0.25,
                        halign="center",
                    )
                )

        self.layar.add_widget(box_r)

        kmb = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.2, 0.2, 0.2, 1), # Abu-abu gelap selaras
            size_hint_y=0.25,
        )
        kmb.bind(on_press=lambda b: self.menu_tarik())
        self.layar.add_widget(kmb)

    def menu_catatan(self):
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = TEKS[BAHASA]["teks_catatan"]
        self.tampilkan_banner_promo()
        kmb = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.2, 0.2, 0.2, 1) # Abu-abu gelap selaras
        )
        kmb.bind(on_press=lambda b: self.mulai_menu())
        self.layar.add_widget(kmb)

    def menu_dukungan(self):
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = TEKS[BAHASA]["teks_dukungan"]
        self.tampilkan_banner_promo()
        kmb = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.2, 0.2, 0.2, 1) # Abu-abu gelap selaras
        )
        kmb.bind(on_press=lambda b: self.mulai_menu())
        self.layar.add_widget(kmb)

    def mulai_loading(self):
        # Disesuaikan menjadi warna gelap elegan
        Window.clearcolor = (0.07, 0.07, 0.07, 1)
        if hasattr(self, "utama"):
            self.utama.bg_color.rgba = (0.08, 0.08, 0.08, 1)

        self.layar.clear_widgets()
        if self.banner_promo in self.utama.children:
            self.banner_promo.size_hint_y = 0
            self.banner_promo.opacity = 0
        self.info.size_hint_y = 0
        self.slot_notif.size_hint_y = 0

        self.saldo_lbl.text = ""
        self.info.text = ""
        self.berita.text = ""

        file_logo = "logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else None)

        if file_logo:
            self.lbl_888 = Image(
                source=file_logo,
                size_hint_y=0.7,
                allow_stretch=True,
                keep_ratio=True,
            )
        else:
            self.lbl_888 = Label(
                text="[b][color=fbbf24]SLOT\n888[/color][/b]",
                markup=True,
                font_size="40sp",
                size_hint_y=0.7,
                halign="center",
            )

        self.lbl_loading = Label(
            text="[color=ffffff]Memuat Game...[/color]",
            markup=True,
            font_size="16sp",
            size_hint_y=0.3,
            halign="center"
        )
        
        self.layar.add_widget(self.lbl_888)
        self.layar.add_widget(self.lbl_loading)
        
        Clock.schedule_once(lambda dt: self.selesai_loading(), 1.5)

    def selesai_loading(self):
        self.banner_promo.size_hint_y = 0.42
        self.banner_promo.opacity = 1
        self.info.size_hint_y = 0.12
        self.slot_notif.size_hint_y = 0.06
        
        if not pemain.get("welcome_claimed", False):
            self.layar_welcome_bonus()
        else:
            self.mulai_menu()

if __name__ == "__main__":
    Aplikasi().run()
