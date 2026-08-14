import json
import os
import hashlib
import urllib.parse
import urllib.request
from datetime import date
from random import choice, randint, choices
from threading import Thread

# Import platform Kivy untuk deteksi Android vs PC
from kivy.utils import platform
from kivmob import KivMob, RewardedListenerInterface

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
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

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
Window.clearcolor = (0.04, 0.05, 0.07, 1)

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

def muat_data():
    default = {
        "poin_saat_ini": 1000,
        "penghasilan": 0,
        "jumlah_menang": 0,
        "jumlah_penarikan_hari_ini": 0,
        "tanggal_terakhir_penarikan": "",
        "riwayat_penarikan": [],
        "welcome_claimed": False,
        "no_hp": "",
    }
    if not os.path.exists(FILE_DATA):
        return default
    try:
        with open(FILE_DATA, "r") as f:
            data = json.load(f)
            if data.get('checksum') != buat_hash(data):
                return default
            return data
    except Exception:
        return default

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
            return "[color=fbbf24][[] 8 ][/color]"
        else:
            return f"[[] {item_str} ]"

class CardBox(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self.bg_color = Color(0.12, 0.16, 0.23, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
        self.bind(pos=self.up, size=self.up)

    def up(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Tombol(Button):
    def __init__(self, bg_color=(0.15, 0.39, 0.92, 1), **kw):
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
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
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
        self.foreground_color = (0.98, 0.75, 0.14, 1)
        self.background_color = (0.08, 0.11, 0.18, 1)
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
        Clock.schedule_once(lambda dt: self.app_ref._iklan_selesai(), 0)

    def on_rewarded_video_ad_closed(self):
        pass

class Aplikasi(App):
    def on_start(self):
        try:
            self.ads = KivMob(ADMOB_APP_ID)
            self.ads.new_banner(ADMOB_BANNER_ID, True)
            self.ads.request_banner()
            self.ads.show_banner()

            self.ads.set_rewarded_ad_listener(RewardsHandler(self))
            self.ads.load_rewarded_ad(ADMOB_REWARDED_ID)
        except Exception as e:
            print(f"Gagal Inisialisasi AdMob: {e}")

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
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = "[color=fbbf24]" + TEKS[BAHASA]["pilih_kotak"] + "[/color]"

        self.sudah_buka_kotak = False
        self.bonus_kotak_terakhir = 0

        grid_kotak = BoxLayout(spacing=8, size_hint_y=0.55, padding=[4, 4, 4, 4])

        for i in range(1, 4):
            btn = Tombol(
                text=f"[BOX]\n{TEKS[BAHASA]['kotak_nama']} {i}",
                bg_color=(0.85, 0.55, 0.1, 1),
                font_size="14sp",
            )
            btn.bind(on_press=lambda inst, b=btn: self.buka_kotak_hadiah(b))
            grid_kotak.add_widget(btn)

        self.layar.add_widget(grid_kotak)

        self.btn_ganda = Tombol(
            text=TEKS[BAHASA]["gandakan_poin"],
            bg_color=(0.85, 0.25, 0.25, 1),
            size_hint_y=0.22,
        )
        self.btn_ganda.bind(
            on_press=lambda b: self.tunggu_iklan(
                self.proses_ganda_poin, beri_bonus=False
            )
        )

        self.btn_klaim_kembali = Tombol(
            text=TEKS[BAHASA]["kembali"],
            bg_color=(0.3, 0.35, 0.4, 1),
            size_hint_y=0.22,
        )
        self.btn_klaim_kembali.bind(on_press=lambda b: self.mulai_menu())
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
            bg_color=(0.85, 0.55, 0.1, 1),
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
        btn_selesai.bind(on_press=lambda b: self.mulai_menu())
        
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
        self.btn_ovo = Tombol(text="OVO [V]")
        self.btn_binance = Tombol(text="BINANCE")

        def pilih_m(m):
            mainkan_klik()
            self.metode_terpilih = m
            self.btn_ovo.text = "OVO [V]" if m == "OVO" else "OVO"
            self.btn_binance.text = "BINANCE [V]" if m == "BINANCE" else "BINANCE"

        self.btn_ovo.bind(on_press=lambda b: pilih_m("OVO"))
        self.btn_binance.bind(on_press=lambda b: pilih_m("BINANCE"))
        baris_metode.add_widget(self.btn_ovo)
        baris_metode.add_widget(self.btn_binance)
        self.layar.add_widget(baris_metode)

        v100 = format_uang(100, BAHASA)
        v500 = format_uang(500, BAHASA)
        v1000 = format_uang(1000, BAHASA)

        baris_nom = BoxLayout(spacing=6, size_hint_y=0.20)
        self.btn_n100 = Tombol(text=f"{v100} [V]")
        self.btn_n500 = Tombol(text=v500)
        self.btn_n1000 = Tombol(text=v1000)

        def pilih_n(n, btn):
            mainkan_klik()
            self.nominal_terpilih = n
            self.btn_n100.text = format_uang(100, BAHASA)
            self.btn_n500.text = format_uang(500, BAHASA)
            self.btn_n1000.text = format_uang(1000, BAHASA)
            btn.text = f"{format_uang(n, BAHASA)} [V]"

        self.btn_n100.bind(on_press=lambda b: pilih_n(100, self.btn_n100))
        self.btn_n500.bind(on_press=lambda b: pilih_n(500, self.btn_n500))
        self.btn_n1000.bind(on_press=lambda b: pilih_n(1000, self.btn_n1000))
        baris_nom.add_widget(self.btn_n100)
        baris_nom.add_widget(self.btn_n500)
        baris_nom.add_widget(self.btn_n1000)
        self.layar.add_widget(baris_nom)

        baris_aksi = BoxLayout(spacing=6, size_hint_y=0.22)
        btn_submit = Tombol(text=TEKS[BAHASA]["tarik"])
        btn_submit.bind(on_press=lambda b: self.proses_tarik_detail())

        btn_riwayat = Tombol(
            text=TEKS[BAHASA]["riwayat"], bg_color=(0.2, 0.4, 0.6, 1)
        )
        btn_riwayat.bind(on_press=lambda b: self.menu_riwayat())

        btn_kembali = Tombol(
            text=TEKS[BAHASA]["kembali"], bg_color=(0.3, 0.35, 0.4, 1)
        )
        btn_kembali.bind(
            on_press=lambda b: self.tunggu_iklan(self.mulai_menu, beri_bonus=True)
        )

        baris_aksi.add_widget(btn_submit)
        baris_aksi.add_widget(btn_riwayat)
        baris_aksi.add_widget(btn_kembali)
        self.layar.add_widget(baris_aksi)

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
            bg_color=(0.3, 0.35, 0.4, 1),
            size_hint_y=0.25,
        )
        kmb.bind(on_press=lambda b: self.menu_tarik())
        self.layar.add_widget(kmb)

    def menu_catatan(self):
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = TEKS[BAHASA]["teks_catatan"]
        self.tampilkan_banner_promo()
        kmb = Tombol(text=TEKS[BAHASA]["kembali"])
        kmb.bind(on_press=lambda b: self.mulai_menu())
        self.layar.add_widget(kmb)

    def menu_dukungan(self):
        mainkan_klik()
        self.layar.clear_widgets()
        self.info.text = TEKS[BAHASA]["teks_dukungan"]
        self.tampilkan_banner_promo()
        kmb = Tombol(text=TEKS[BAHASA]["kembali"])
        kmb.bind(on_press=lambda b: self.mulai_menu())
        self.layar.add_widget(kmb)

    def mulai_loading(self):
        Window.clearcolor = (0.04, 0.05, 0.07, 1)
        if hasattr(self, "utama"):
            self.utama.bg_color.rgba = (0.08, 0.11, 0.18, 1)

        self.layar.clear_widgets()
        if self.banner_promo in self.utama.children:
            self.banner_promo.size_hint_y = 0
            self.banner_promo.opacity = 0
        self.info.size_hint_y = 0
        self.berita.size_hint_y = 0

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
                text="[b][color=FFD700]SLOT\n888[/color][/b]",
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
        self.berita.size_hint_y = 0.06
        
        if not pemain.get("welcome_claimed", False):
            self.layar_welcome_bonus()
        else:
            self.mulai_menu()

if __name__ == "__main__":
    Aplikasi().run()
