# -*- کدگذاری: utf-8 -*-
«»»
AHNG MUSIC - Ø±Ø¨Ø§Øª Ù…ÙˆØ²ÛŒÚ© Ø±ÙˆØ¨ÛŒÚ©Ø§ (Rubika Bot API v3)

Ø§Ø¬Ø±Ø§:
    BOT_TOKEN=xxxx PUBLIC_URL=https://Ø¢Ø¯Ø±Ø³-Ø¹Ù…ÙˆÙ…ÛŒ-Ø³Ø±ÙˆØ±-Ø´Ù…Ø§ پایتون ahng_music_bot.py

Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ (ساده):
    Ø±ÙˆØ®ÛŒÚ©Ø§ ©Ù„ÛŒÚ© Ø§ÛŒÙ† ØÚ©Ù…Ù‡â€ŒÙ‡Ø§ Ø±Ø§ Ù ØˆØ·ØØ² (ReceiveInlineMessage) Ø¨Ø±Ø§ÛŒ Ø±Ø¨Ø§Øª Ù…ÛŒâ€ŒÙ Ø±Ø³ØªØ¯ØŒ
    Ù†Ù‡ Ø§Ø² Ø±Ø§Ù‡ getUpdates. Ø¨Ø±Ø§ÛŒ Ù‡Ù…ÛŒÙ† Ø±Ø¨Ø§Øª ÛŒÚ© Ø³Ø±ÙˆØ±Ú©ÙˆÚ†Ú©. Ø¢Ø¯Ø±Ø³Ø´ Ø±Ø§
    Ø¨Ø§ updateBotEndpoints Ø¨Ù‡ Ø±ÙˆØ¨ÛŒÚ©Ø§ Ù…ÛŒâ€ŒØ¯Ù‡ØØ¯. Ø¨Ø±Ø§ÛŒ Ø§ÛŒÙ† Ú©Ø§Ø± Ø¨Ø§ÛŒØ¯ PUBLIC_URL (Ø¢Ø¯Ø±Ø³ https Ø¹Ù…ÙˆÙ…ÛŒ
    Ø³Ø±ÙˆØ±/Ù‡Ø§Ø³Øª) ØªÙ†Ø¸ÛŒÙ… Ø´Ø¯Ù‡ Ø¨Ø§Ø´Ø¯. Ø§Ú¯Ø± ØªÙ†Ø¸ÛŒÙ… Ù†Ø¨Ø§Ø´Ø¯ ÛŒØ§Ø« ØØ§Ù„Øª Ù‚Ø¯ÛŒÙ…ÛŒ
    (Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ù„ÛŒÙ†Ú© + ?start=) Ø¨Ø±Ù…ÛŒâ€ŒÚ¯Ø±ØØØ¯.

ØØÚ©Ù… Ù„ÛŒÙ†Ú© Ø§Ø³Øª (Ø¨Ø§Ø² Ú©Ø±Ø¯Ù† Ø±Ø¨Ø§Øª Ø¨Ø§ ?start=song_N)ØŒ
Ú†ÙˆÙ† Ø¯Ø± Ú©Ø§Ù†Ø§Ù„ Ù„Ø§Ø²Ù… Ø§Ø³Øª Ú©Ø§Ø±Ø¨Ø± ÙˆØ§Ø±Ø¯ Ø±Ø¨Ø§Øª.
«»»

وارد کردن سیستم عامل
واردات مجدد
وارد کردن json
زمان واردات
وارد کردن هش‌لیب
وارد کردن sqlite3
ورود به سیستم واردات
وارد کردن نخ
درخواست‌های واردات
از http.server، BaseHTTPRequestHandler و ThreadingHTTPServer را وارد کنید.
از urllib.parse import quote

# =====================================================
# ØªÙ†Ø¸ÛŒÙ…Ø§Øª
# =====================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = "ahng_music_bot" # Ø¨Ø¯ÙˆÙ† @
مدیران = {
    x.strip()
    برای x در os.getenv("ADMINS", "u0HbMCz07b206d47b6e01988bf7610cf").split(",")
    اگر x.strip()
}
DB_FILE = os.getenv("DB_FILE", "ahng.db")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")).strip().rstrip("/")
پورت = int(os.getenv("پورت"، "8080"))
API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"
WEBHOOK_PATH = "/hook/" + hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:20]
فاصله نظرسنجی = 0.4
REQUEST_TIMEOUT = (5، 20)

USE_INLINE = False # Ø§Ú¯Ø± ÙˆØ¨â€ŒÙ‡ÙˆÚ© Ø¨Ø§ Ù…ÙˆÙ Ù‚ÛŒØª Ø«Ø¨Øª Ø´Ø¯ True Ù…ÛŒâ€ņÚ
قفل = threading.RLock()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
ورود = logging.getLogger("AHNG")

# =====================================================
# Ø§Ø±ØªØ¨Ø§Ø· Ø¨Ø§ API
# =====================================================
جلسه = درخواست‌ها.جلسه()


فراخوانی def(متد، **داده):
    امتحان کنید:
        r = session.post(API + method, json=data, timeout=REQUEST_TIMEOUT)
        امتحان کنید:
            نتیجه = r.json()
        به جز ValueError:
            log.error("API غیر JSON | %s | http=%s | %s", method, r.status_code, r.text[:200])
            برگرداندن {}
        اگر result.get("status") در (هیچکدام، "OK") نباشد:
            log.error("خطای API | %s | %s", متد, str(result)[:300])
        نتیجه بازگشتی
    به جز استثنا به عنوان e:
        log.error("درخواست خطا | %s | %s", متد, e)
        برگرداندن {}


def ok(نتیجه):
    تابع ()return bool و تابع ()result.get("status", "OK") == "OK" را برمی‌گرداند.


نام کاربری را شناسایی کنید():
    """Ø¢ÛŒØ¯ÛŒ ÙˆØ§Ù‚Ø¹ÛŒ Ø±Ø¨Ø§Øª Ø±Ø§ Ø§Ø² Ø®ÙˆØ¯ Ø±ÙˆØ¨ÛŒÚ©Ø§ Ù…ÛŒâ€ŒÚ¯Û Ù„ÛŒÙ†Ú©â€ŒÙ‡Ø§ ØØªÙ…Ø§Ù‹ ØØØ±Ø³Øª Ø¨Ø§Ø´Ù†Ø¯."""
    نام کاربری_ربات سراسری
    res = فراخوانی("getMe")
    data = res.get("data") یا {}
    اگر isinstance(data.get("bot"), dict) باشد، در غیر این صورت داده را دریافت می‌کند. bot = data.get("bot")
    uname = str(bot.get("username") or "").lstrip("@").strip()
    اگر uname و uname.lower() != BOT_USERNAME.lower() باشد:
        log.warning("BOT_USERNAME Ø¯Ø± Ú©Ø¯ %s Ø¨ÙˆØ¯ ÙˆÙ„ÛŒ Ø±Ø¨Ø§Øª ÙˆØ§Ù‚Ø¹ÛŒ %s Ø§Ø³ØªØŒ› Ø§Ø³ØªÙ Ø§Ø¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯، BOT_USERNAME، نام نام)
        نام کاربری_BOT = بدون نام
    log.info("GETME | ok=%s | username=%s", bool(res), uname یا "?")


# =====================================================
# Ø¯ÛŒØªØ§Ø¨ÛŒØ³
# =====================================================
db = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30)
db.executescript("""
ایجاد جدول در صورت عدم وجود آهنگ‌ها (
    افزایش خودکار کلید اصلی عدد صحیح شناسه
    متن عنوان، متن هنرمند، شناسه فایل، متن
    دانلودهای INTEGER DEFAULT 0، added_at INTEGER)؛
ایجاد جدول اگر وجود نداشته باشد کاربران(راهنما متن کلید اصلی، join_at عدد صحیح)؛
ایجاد جدول در صورت عدم وجود کانال‌ها (متن راهنما، کلید اصلی، متن پیوند)؛
"")
db.commit()

admin_state = {} # guid Ø§Ø¯Ù…ÛŒÙ† -> Ù…Ø±ØÙ„Ù‡â€ŒÛŒ Ø¹Ù„ÛŒ
pending_channel_link = {} # guid Ø¯Ù…ÛŒÙ† -> Ù„ÛŒÙ†Ú© Ú©ÙÙ†Ø§Ù„ÛŒ ©Ù‡ . Ø§Ø³Øª


# =====================================================
# Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§
# =====================================================
def bot_link(بار مفید):
    return f"https://rubika.ir/{BOT_USERNAME}?start={quote(str(payload), safe='_')}"


دکمه لینک (پیشنهاد، متن، آدرس اینترنتی):
    return {"id": str(bid), "type": "Link", "button_text": text,
            "button_link": {"type": "url", "link_url": url}}


دکمه ساده (پیشنهاد، متن):
    return {"id": str(bid), "type": "Simple", "button_text": text}


دکمه عمل (عمل، متن):
    """Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ Ø§Ø³ØªØŒ ÙˆÚ¯Ø±Ù†Ù‡ Ù„ÛŒÙ†Ú© ?start=."""
    اگر USE_INLINE باشد:
        بازگرداندن simple_button(action, text)
    دکمه_پیوند_را_برگردانید(عمل، متن، لینک_ربات(عمل))


صفحه کلید تعریف (ردیف‌ها):
    return {"rows": [{"buttons": row} برای ردیف در ردیف‌ها]}


ارسال def(chat_id, text, buttons=None):
    اگر chat_id نباشد:
        log.warning("ارسال لغو شد: chat_id Ø®Ø§Ù„ÛŒ Ø§Ø³Øª")
        برگرداندن {}
    d = {"chat_id": chat_id, "text": str(text)}
    اگر دکمه‌ها:
        d["inline_keypad"] = دکمه‌ها
    res = call("sendMessage", **d)
    اگر دکمه‌ها و نه ok(res):
        log.error("ارسال با صفحه کلید ناموفق بود -> دوباره امتحان کردن بدون دکمه | %s", str(res)[:300])
        res = call("sendMessage", chat_id=chat_id, text=str(text))
    بازگرداندن اطلاعات


تابع def send_file(chat_id, file_id, text, buttons=None):
    d = {"شناسه_چت": شناسه_چت، "شناسه_فایل": شناسه_فایل، "متن": متن}
    اگر دکمه‌ها:
        d["inline_keypad"] = دکمه‌ها
    res = فراخوانی("sendFile", **d)
    اگر دکمه‌ها و نه ok(res):
        log.error("ارسال فایل با صفحه کلید ناموفق بود -> تلاش مجدد بدون دکمه | %s", str(res)[:300])
        res = call("sendFile", chat_id=chat_id, file_id=file_id, text=text)
    بازگرداندن اطلاعات


# =====================================================
# Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§ Ùˆ Ø¹Ø¶ÙˆÛŒØª Ø§ØØ¨Ø§Ø±ÛŒ
# =====================================================
کانال‌های تعریف‌شده():
    return db.execute("SELECT guid, link FROM channels").fetchall()


عضو_کاربر(راهنمای_کاربر):
    """Ù‡Ø± Ø¨Ø§Ø± Ø§Ø² Ø±ÙˆØ¨ÛŒÚ©Ø§ Ù…ÛŒâ€ŒÙ¾Ø±Ø³Ø¯ (Ú©Ø´ Ù†Ù…ÛŒâ€ŒÚ©ÙØŒÚØØ³ï) Ú©Ù‡ Ø§Ø² Ú©Ø§Ù†Ø§Ù„ Ø®Ø§Ø±Ø¬ Ø´ÙˆØ¯ Ø¯ÙˆØ¨Ø§Ø±Ù‡ Ù‚Ù Ù„ Ù…ÛŒâ€ŒØ´ÙˆØ¯."""
    اگر user_guid نباشد:
        مقدار نادرست را برمی‌گرداند
    برای راهنما، _ در channels():
        res = call("getChatMember", chat_id=guid, user_id=user_guid)
        status = str((res.get("data") or {}).get("status", "")).lower()
        log.info("بررسی اعضا | کانال=%s | کاربر=%s | وضعیت=%s", guid, user_guid, status یا "?")
        اگر وضعیت در ("عضو"، "خالق"، "مدیر"، "مالک") نباشد:
            مقدار نادرست را برمی‌گرداند
    بازگشت درست


لیست_کانال_تعریف‌شده(شناسه_چت):
    آیتم‌ها = کانال‌ها()
    اگر موارد نباشند:
        return send(chat_id, "ðŸ“ Ù‡Ù†ÙˆØ² Ú©Ø§Ù†Ø§Ù„ÛŒ Ø«Ø¨Øª Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª.")
    متن = "ðŸ“‹ Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø«Ø¨Øªâ€ŒØ´Ø¯Ù‡:\n\n" + "\n".join(
        تابع f"{i}. {g}\n{l}" برای i و (g و l) در enumerate(items, 1))
    ارسال بازگشتی(chat_id, text)


# =====================================================
# Ø¢Ù‡Ù†Ú¯â€ŒÙ‡Ø§
# =====================================================
لینک_آهنگ_دف(شناسه_آهنگ):
    return bot_link(f"song_{song_id}")


def get_song(song_id):
    return db.execute("SELECT title, artist, file_id FROM songs WHERE id=?", (song_id,)).fetchone()


def send_song(chat_id, song_id):
    آهنگ = get_song(song_id)
    اگر آهنگ نباشد:
        return send(chat_id, "â Œ Ø¢Ù‡Ù†Ú¯ Ù…ÙˆØ±Ø¯Ù†Ø¸Ø± Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯.")
    عنوان، هنرمند، file_id = آهنگ
    res = call("sendFile", chat_id=chat_id, file_id=file_id,
               text=f"ðŸŽµ {title}\nðŸŽ¤ {هنرمند}\n\n@{BOT_USERNAME}")
    اگر مشکلی نیست (res):
        db.execute("به‌روزرسانی آهنگ‌ها، تعداد دانلودها را تنظیم کن=دانلودها+1 WHERE id=?", (song_id,))
        db.commit()
        log.info("آهنگ ارسال شد | آهنگ=%s | چت=%s", song_id, chat_id)
    بازگرداندن اطلاعات


تابع `join_prompt` (شناسه چت، مقدار داده):
    ردیف‌ها = [[link_button(f"channel_{i}", f"ðŸ“¢ Ø¹Ø¶ÙˆÛŒØª Ø¯Ø± Ú©Ø§Ù†Ø§Ù„ {i + 1}", لینک)]
            برای i، (_، لینک) در enumerate(channels())]
    rows.append([action_button(f"joined_{payload}", "âœ… Ø¹Ø¶Ùˆ Ø´Ø¯Ù…")])
    send(chat_id, "ðŸ"' Ø¨Ø±Ø§ÛŒ ØØØ±ÛŒØ§Ù Ø¢Ù‡Ù†Ú¯ Ø§Ø¨ØªØ¯Ø§ Ø´ÙˆÛŒØ¯ØŒ Ø³Ù¾Ø³ Ø¹Ø¶Ùˆ Ø´Ø¯Ù…Â» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯:",
         صفحه کلید (ردیف ها))


تحویل def(chat_id، user_guid، payload):
    اگر payload.startswith("song_") نباشد:
        بازگشت
    song_id = payload[5:]
    اگر song_id.isdigit() نباشد یا get_song(song_id) نباشد:
        return send(chat_id, "â Œ Ø¢Ù‡Ù†Ú¯ Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯.")
    اگر channels() و is_member(user_guid) نباشد:
        تابع join_prompt(chat_id, payload) را برمی‌گرداند.
    تابع send_song(chat_id, song_id) را برمی‌گرداند.


def save_song(پیام، فرستنده):
    f = message.get("file") یا {}
    شناسه فایل = f.get("شناسه فایل")
    اگر file_id نباشد:
        هیچ کدام را برنگردانید
    title = (f.get("file_name") or "Ø¢Ù‡Ù†Ú¯").rsplit(".", 1)[0]
    هنرمند = "-"
    عنوان = (message.get("text") یا "").strip()
    اگر "|" در عنوان باشد:
        t، a = [x.strip() برای x در caption.split("|", 1)]
        عنوان، هنرمند = (t یا عنوان)، (a یا "-")
    db.execute("وارد کردن آهنگ‌ها(عنوان، هنرمند، شناسه فایل، دانلودها، اضافه شده در) مقادیر(?,?,?,0,?)",
               (عنوان، هنرمند، شناسه فایل، int(time.time())))
    db.commit()
    song_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    log.info("آهنگ ذخیره شد | شناسه=%s | عنوان=%s | توسط=%s", شناسه آهنگ, عنوان, فرستنده)
    بازگرداندن شناسه آهنگ، عنوان، هنرمند


def final_post(chat_id, song_id, text):
    """Ù¾Ø³Øª Ù†Ù‡Ø§ÛŒÛŒ: Ø¢Ù‡Ù†Ú¯ + Ù…ØªÙ† + Ø¯Ú©Ù…Ù‡â€ŒÛŒ Øª Ø¢Ù‡Ù†Ú¯ (Ù„ÛŒÙ†Ú© Ø¨Ù‡ Ø±Ø¨Ø§Øª)."""
    آهنگ = get_song(song_id)
    اگر آهنگ نباشد:
        return send(chat_id, "â Œ Ø¢Ù‡Ù†Ú¯ Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯.")
    kp = صفحه کلید([[link_button(f"song_{song_id}", "حذف آهنگ", song_link(song_id))]])
    return send_file(chat_id, song[2], f"{text}\n\n@{BOT_USERNAME}", kp)


# =====================================================
# Ø¢Ù…Ø§Ø±
# =====================================================
آمار دف (چت_آیدی):
    کاربران = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    آهنگ‌ها، دانلودها = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(downloads),0) FROM songs").fetchone()
    بهترین = db.execute(
        "انتخاب عنوان، دانلودها از آهنگ‌ها، مرتب‌سازی بر اساس دانلودها، محدودیت حجمی ۱۰").fetchall()
    text = (f"ðŸ“Š Ø¢Ù…Ø§Ø± AHNG MUSIC\n\nðŸ'¤ Ú©Ø§Ø±Ø¨Ø±Ø§Ù†: {users}\nðŸŽµ
            f"â¬‡ï¸ Ø¯Ø§Ù†Ù„ÙˆØ¯Ù‡Ø§: {downloads}\n\nðŸ † Û±Û° Ø¢Ù‡Ù†Ú¯ Ù¾Ø±ØØ¯Ø§Ù†ÙÙ":
    متن += ("\n".join(f"{i}. {t} | {c} Ø¯Ø§Ù†Ù„ÙˆØ¯" برای i، (t، c) در enumerate(best، 1))
             if best else "Ù‡Ù†ÙˆØ² Ø¢Ù‡Ù†Ú¯ÛŒ Ø«Ø¨Øª Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª.")
    ارسال بازگشتی(chat_id, text)


# =====================================================
# Ù¾Ù†Ù„ Ù…Ø¯ÛŒØ±
# =====================================================
def is_admin(راهنما):
    راهنمای بازگشت در بخش مدیریت


شناسه‌ی چت (admin_panel):
    ردیف‌ها = [
        [action_button("adm_add", "حذف"), action_button("adm_upload", "حذف"")],
        [action_button("adm_addch"، "ðŸ“¢ Ø«Ø¨Øª Ú©Ø§Ù†Ø§Ù„")، action_button("adm_stats"، "ðŸ"Š Ø¢Ù…Ø§Ø±")]،
        [action_button("adm_channels", "ðŸ“‹ Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§")],
    ]
    ارسال بازگشتی(chat_id,
                "ðŸ› Ù¾Ù†Ù„ Ù…ØÛŒØ±ÛŒØª AHNG MUSIC\nÛŒÚ©ÛŒ Ø§Ø² Ú©Ù†ÛŒØ¯:\n\n"
                "(Ø¯Ø³ØªÙˆØ±Ù‡Ø§ÛŒ Ù…ØªÙ†ÛŒ: /add /upload /addch /stats /channels /cancel)"،
                صفحه کلید (ردیف ها))


تابع def handle_action(action, chat_id, sender)
    """©Ø§Ø± Ù‡Ø± Ø¯Ú©Ù…Ù‡ (Ú†Ù‡ Ú©Ù„ÛŒÚ © Ø¯Ø³ØªÙˆØ± Ù…ØªÙ†ÛŒ)."""
    log.info("دکمه | اکشن=%s | فرستنده=%s | چت=%s", اکشن, فرستنده, chat_id)

    اگر action.startswith("adm_") باشد:
        اگر is_admin(sender) نباشد:
            log.warning("اقدام مدیر از طرف غیر مدیر نادیده گرفته شد: %s", فرستنده)
            بازگشت

        اگر اکشن == "adm_add" باشد:
            admin_state[sender] = {"mode": "await_add"}
            return send(chat_id, "• Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ ÛŒØ§ Ù ÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.\n"
                                 "(Ø¯Ø± Ú©Ù¾Ø´Ù† Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯: Ø§Ø³Ù… Ø¢ÙáÙ Ø®ÙˆØ§Ù†Ù†Ø¯Ù‡)")
        اگر اکشن == "adm_upload" باشد:
            admin_state[sender] = {"mode": "await_upload"}
            return send(chat_id, "ðŸš€ Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ ÛŒØ§ Ù ÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.\n"
                                 "(Ø¯Ø± Ú©Ù¾Ø´Ù† Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯: Ø§Ø³Ù… Ø¢ÙáÙ Ø®ÙˆØ§Ù†Ù†Ø¯Ù‡)")
        اگر اکشن == "adm_stats" باشد:
            آمار بازگشتی (chat_id)
        اگر اکشن == "adm_channels" باشد:
            لیست کانال‌ها (چت_آیدی) را برمی‌گرداند
        اگر اکشن == "adm_addch" باشد:
            admin_state[sender] = {"mode": "await_channel"}
            return send(chat_id, "ðŸ“¢ Ø¢ÛŒØ¯ÛŒ Ú©Ø§Ù†Ø§Ù„ Ø±Ø§ Ø¨Ù Ø±Ø³ØªÛŒØ¯ (Ù…Ø«Ù„ @AhngOfficial).\n"
                                 "Ø¹Ø¯ ÛŒÚ© Ù¾Ø³Øª Ø§Ø² Ù‡Ù…Ø§Ù† Ú©Ø§Ù†Ø§Ù„ Ø¨Ø±Ø§ÛŒ Ù…Ù† Ù ÙˆØ±Ù. Ú©Ù†ÛŒØ¯.\n"
                                 "Ø±Ø¨Ø§Øª Ø¨Ø§ÛŒØ¯ Ø§Ø¯Ù…ÛŒÙ† Ú©Ø§Ù†Ø§Ù„ Ø¨Ø§Ø´Ø¯.")
        اگر اکشن == "adm_cancel" باشد:
            admin_state.pop(فرستنده، هیچکدام)
            pending_channel_link.pop(فرستنده، هیچکدام)
            بازگشت ارسال (chat_id, "â Œ Ù„ØºÙˆ Ø´Ø¯. Ø¨Ø±Ø§ÛŒ Ù¾Ù†Ù„: /panel")
        اگر action.startswith("adm_text_") باشد:
            sid = action[len("adm_text_"):]
            admin_state[sender] = {"mode": "await_post_text", "sid": sid}
            return send(chat_id, "âœ ï¸ Ù…ØªÙ† Ù¾Ø³Øª Ø±Ø§ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯ Ùˆ Ø¨Ù Ø±Ø³ØªÛŒØ¯:"
        اگر action.startswith("adm_done_") باشد:
            sid = action[len("adm_done_"):]
            st = admin_state.get(sender) یا {}
            اگر st.get("mode") != "await_done" یا str(st.get("sid") != sid:
                return send(chat_id, "â Œ Ø§ÛŒÙ† ØØØ±Ø®ÙˆØ§Ø³Øª Ù…Ù†Ù‚Ø¶ÛŒ Ø´Ø¯Ù‡. Ø´Ø±ÙˆØ¹ Ú©Ù†ÛŒØ¯: /panel")
            admin_state.pop(فرستنده، هیچکدام)
            send(chat_id, "âœ… Ù¾Ø³Øª Ø¢Ù…Ø§Ø¯Ù‡ Ø´Ø¯. Ù¾ÛŒØ§Ù… Ú©Ù†ÛŒØ¯ ðŸ'‡")
            تابع ()final_post را برمی‌گرداند ("chat_id", sid, st.get("text", ""))
        بازگشت

    اگر action.startswith("joined_song_") باشد:
        song_id = action[len("joined_song_"):]
        اگر song_id.isdigit() نباشد:
            بازگشت
        اگر is_member(فرستنده):
            تابع send_song(chat_id, song_id) را برمی‌گرداند.
        return send(chat_id, "â Œ Ù‡Ù†ÙˆØ² Ø¹Ø¶Ùˆ Ú©Ø§Ù†Ø§Ù„ Ù†ÛŒØ³ØªÛŒØ¯. Ø¹Ø¶Ùˆ Ø´ÙˆÛÙ Ø¯ÙˆØ¨Ø§Ø±Ù‡ Â«Ø¹Ø¶Ùˆ Ø´Ø¯Ù…Â» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯.")


COMMAND_ACTIONS = {"/add": "adm_add", "/upload": "adm_upload", "/addch": "adm_addch",
                   "/stats": "adm_stats", "/channels": "adm_channels", "/cancel": "adm_cancel"}


تابع def handle_admin(پیام، شناسه چت، فرستنده، متن):
    """Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù…Ø¯ÛŒØ±. Ø§Ú¯Ø± Ú†ÛŒØ²ÛŒ Ù†ØªÛŒØ¬Ù‡â€ŒÛŒ ØºÛŒØ± هیچ Ø¨Ø±Ù…ÛŒâ€ŒÚ¯Ø±Ø¯Ø§Ù†Ø¯."""
    f = پیام.دریافت("فایل")
    fwd = message.get("forwarded_from") یا {}
    st = admin_state.get(sender) یا {}
    حالت = st.get("حالت")

    # Û±) Ù ÙˆØ±ÙˆØ§Ø±Ø¯ Ù¾Ø³Øª Ú©Ø§Ù†Ø§Ù„ Ø¨Ø±Ø§ÛŒ Ø«Ø¨Øª Ú©Ø§Ù†Ø§ÙØØ³Ø¨Ù
    اگر fwd و فرستنده در pending_channel_link باشند:
        راهنما = fwd.get("from_chat_id")
        اگر راهنما نباشد:
            return send(chat_id, "â Œ Ø´Ù†Ø§Ø³Ù‡â€ŒÛŒ Ú©Ø§Ù†Ø§Ù„ Ø§Ø² Ù¾ÛŒØ§Ù… Ù Ù†Ø´Ø¯.")
        لینک = pending_channel_link.pop(فرستنده)
        db.execute("مقادیر را در کانال‌ها (راهنما، لینک) وارد یا جایگزین کن(?,?)", (راهنما، لینک))
        db.commit()
        log.info("کانال ذخیره شد | %s", راهنما)
        return send(chat_id, "âœ… Ú©Ø§Ù†Ø§Ù„ Ø«Ø¨Øª Ø´Ø¯. ÛŒØ§Ø¯ØªØ§Ù† Ø¨Ø§Ø´Ø¯ Ø±Ø¨Ø§Øª Ø¯ØØ±Ù Ø§Ø¯Ù…ÛŒÙ† Ø¨Ø§Ø´Ø¯.")

    # Û²) ØØ±ÛŒØ§Ù Øª Ù Ø§ÛŒÙ„ Ø¢Ù‡Ù†Ú¯
    اگر ف:
        ذخیره شده = save_song(پیام، فرستنده)
        اگر ذخیره نشد:
            return send(chat_id, "â Œ Ù Ø§ÛŒÙ„ Ø¢Ù‡Ù†Ú¯ Ø´Ù†Ø§Ø³Ø§ÛŒÛŒ Ù†Ø´Ø¯.")
        سید، عنوان، هنرمند = ذخیره شده
        لینک = لینک_آهنگ(sid)
        اگر حالت == "await_upload" باشد:
            # Ø¢Ù‡Ù†Ú¯ Ø¨Ø§ Ø¯Ú©Ù… Ù…Ø¯ÛŒØ± Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ù‡Ù…Ø§Ù† ØØ¸Ù‡ Ù…ØªÙ† Ø±Ø§ Ù‡Ù… Ø¨Ù Ø±Ø³ØªØØ
            admin_state[sender] = {"mode": "await_post_text", "sid": sid}
            kp = صفحه کلید ([[action_button(f"adm_text_{sid}", "âœ ï¸ Ø«Ø¨Øª Ù…ØªÙ† Ù¾Ø³Øª")]])
            send_file(chat_id, f.get("file_id"), f"ðŸŽµ {title}\nðŸŽ¤ {artist}", kp)
            ارسال بازگشتی (chat_id، f"âœ… Ø°Ø®ÛŒØ±Ù‡ Ø´Ø¯: {title} - {artist}\n\n"
                                 f"ðŸ"— Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ:\n{link}\n\n"
                                 "Ø¯Ú©Ù…Ù‡â€ŒÛŒ Â«Ø«Ø¨Øª Ù…ØªÙ† Ù¾Ø³ØªÂ» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯ ÛŒØ§ Ù…Ø³ Ù¾Ø³Øª Ø±Ø§ Ø¨Ù Ø±Ø³ØªÛŒØ¯.")
        admin_state.pop(فرستنده، هیچکدام)
        return send(chat_id, f"âœ… ØØ®ÛŒØ±Ù‡ ØØØ¯: {title} - {artist}\n\nðŸ”— Ù„ÛŒÙ†Ú© ØªØªØ¯:\n{link}")

    # Û³) ØªÙˆØ±Ù‡Ø§ (/start Ùˆ Ù†Ø§Ø´Ù†Ø§Ø® Ø§Ø¯Ø§Ù…Ù‡ Ù¾ÛŒØØØ§ Ú©Ù†Ù†Ø¯)
    اگر متن با ("/") شروع شود:
        cmd = text.split()[0].lower()
        اگر cmd در COMMAND_ACTIONS باشد:
            تابع handle_action(command_actions[cmd], chat_id, sender) را برمی‌گرداند.
        اگر cmd == "/done" و mode == "await_done" باشد:
            تابع handle_action(f"adm_done_{st['sid']}", chat_id, sender) را برمی‌گرداند.
        اگر text.startswith("/delchannel "):
            db.execute("حذف از کانال‌های WHERE guid=?", (text.split(maxsplit=1)[1].strip(),))
            db.commit()
            return send(chat_id, "âœ… Ú©Ø§Ù†Ø§Ù„ ØØ°Ù Ø´Ø¯.")
        اگر متن با ("/del") شروع شود:
            sid = text.split(maxsplit=1)[1].strip()
            اگر sid.isdigit() نباشد:
                return send(chat_id, "â Œ Ø´Ù†Ø§Ø³Ù‡â€ŒÛŒ Ø¢Ù‡Ù†Ú¯ Ù…Ø¹ØªØ¨Ø± Ù†ÛŒØ³Øª.")
            db.execute("حذف از آهنگ‌ها از کجا id=?", (sid,))
            db.commit()
            return send(chat_id, "âœ… Ø¢Ù‡Ù†Ú¯ ØØ°Ù Ø´Ø¯.")
        هیچ کدام را برنگردانید

    # Û´) Ù…Ø±ØÙÙ‡â€ŒÙ‡Ø§ÛŒ
    اگر حالت == "await_post_text" و متن:
        admin_state[sender] = {"mode": "await_song_link", "sid": st["sid"], "text": text}
        return send(chat_id, "âœ… Ù…ØªÙ† Ø«Ø¨Øª Ø´Ø¯.\nðŸ”— ØØ§Ù„Ø§ Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ Ø¢Ù‡Ù†Ú¯ Ø±ØªÛ¯:\n\n" + song_link(st["sid"]))

    اگر حالت == "await_song_link" و متن:
        m = re.search(r"song_(\d+)", text)
        اگر m یا m.group(1) نباشد!= str(st["sid"]):
            return send(chat_id, "â Œ Ù„ÛŒÙ†Ú© ØØ±Ø³Øª Ù†ÛŒØ³Øª. Ù„ÛŒÙ†Ú© . Ø±Ø³ØªÛŒØ¯:\n" + آهنگ_پیوند (st["sid"]))
        st["mode"] = "منتظر_انجام شدن"
        admin_state[sender] = st
        kp = صفحه کلید([[action_button(f"adm_done_{st['sid']}", "``````",
                      action_button("adm_cancel"، "â Œ Ù„ØºÙˆ")]])
        return send(chat_id, "âœ… Ù„ÛŒÙ†Ú© ØªØ£ÛŒÛŒØ¯ Ø´Ø¯. Â«ØªÙ…Ø§Ù…Â» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯ ØªØ§ Ù Ù†Ù‡Ø§ÛŒÛŒ Ø¨Ø±Ø§ÛŒØªØ§Ù† Ø§Ø±Ø³Ø§Ù„ Ø´ÙˆØ¯.", kp)

    اگر حالت mode == "await_done" باشد و متن در ("ØªÙ…Ø§Ù…", "ØªÙ…Ø§Ù….") باشد:
        تابع handle_action(f"adm_done_{st['sid']}", chat_id, sender) را برمی‌گرداند.

    اگر حالت == "await_channel" و متن:
        اول = متن.split()[0]
        اگر first.startswith("@") و len(first) > 2 باشد:
            لینک = "https://rubika.ir/" + اول[1:]
        الیف "rubika.ir/" در ابتدا یا "rubika.me/" در ابتدا:
            لینک = اول
        دیگری:
            return send(chat_id, "â Œ Ù„ÛŒÙ†Ú© ÛŒØ§ Ø¢ÛŒØ¯ÛŒ Ú©Ø§Ù†Ø§Ù„ Ù…Ø¹ØªØ¨Ø± Ù†ÛŒØ³Øª.")
        pending_channel_link[sender] = لینک
        admin_state.pop(فرستنده، هیچکدام)
        return send(chat_id, "âœ… Ù„ÛŒÙ†Ú© Ø¯Ø±ÛŒØ§Ù Øª Ø´Ø¯. ØØ§ÙØ§ ÛŒÚ© Ø§Ø§² Ø¨Ø±Ø§ÛŒ Ù…Ù† Ù ÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.")

    هیچ کدام را برنگردانید


# =====================================================
# Ù¾ÛŒØ§Ù…â€Ù‡Ø§
# =====================================================
شروع فرآیند (chat_id، فرستنده، payload):
    log.info("شروع | فرستنده=%s | بار مفید=%s", فرستنده, بار مفید)
    اگر payload.startswith("song_"):
        تحویل (شناسه چت، فرستنده، بار مفید) را برمی‌گرداند
    اگر payload.startswith(("adm_", "joined_song_")):
        تابع handle_action(payload, chat_id, sender) را برمی‌گرداند.
    اگر بار مفید نباشد:
        اگر is_admin(فرستنده):
            برگرداندن پنل مدیریت (چت آی‌دی)
        return send(chat_id, "Ø³Ù„Ø§Ù… ðŸ'‹ Ø¨Ù‡ آهنگ موزیک Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒØ¯.\n"
                             "Ø¨Ø±Ø§ÛŒ Ø¯Ø±ÛŒØ§Ù Ø¢Ù‡Ù†Ú¯ Ø§Ø² Ø¯Ú©Ù…Ù‡â€ŒÛŒ ØØØ§Ù†Ù„ÙˆØ¯ Ø²ÛŒ Ø³Øªâ€ŒÙ‡Ø§ÛŒ Ú©Ø§Ù†Ø§Ù„ Ø§ØªÙ


تابع def handle_message(پیام، شناسه چت):
    اگر isinstance(message, dict) نباشد:
        بازگشت
    فرستنده = پیام.دریافت("شناسه_فرستنده", شناسه_چت)
    متن = (message.get("text") or "").strip()
    aux = message.get("aux_data") یا {}
    اگر فرستنده نباشد:
        بازگشت
    اگر chat_id در بخش مدیریت باشد:
        فرستنده = شناسه چت

    db.execute("مقادیر(?,?) را در users(guid, join_at) وارد یا نادیده بگیر", (sender, int(time.time())))
    db.commit()
    log.info("پیام | فرستنده=%s | متن=%s", فرستنده, متن[:100])

    اگر متن == "/myid" باشد:
        return send(chat_id, f"ðŸ†” Ø´Ù†Ø§Ø³Ù‡â€ŒÛŒ Ø´Ù…Ø§:\n{فرستنده}\n\nðŸ'¬ Ø´Ù†Ø§Ø³Ù‡â€ŒÛŒ)Ø_ª"
    اگر متن == "/ping" باشد:
        return send(chat_id, f"pong âœ… Ø±Ø¨Ø§Øª Ø±ÙˆØ´Ù† Ø§Ø³Øª. Ø¯Ú©Ù… 'ØºÛŒØ±Ù Ø¹Ø§Ù„ (ØØ§Ù„Øª Ù„ÛŒÙ†Ú©)'}")

    اگر aux.get("button_id"):
        تابع handle_action(aux["button_id"], chat_id, sender) را برمی‌گرداند.

    اگر is_admin(sender) و handle_admin(message, chat_id, sender, text) برابر با None نباشند:
        بازگشت

    اگر متن == "/panel" باشد:
        اگر is_admin(sender) باشد، admin_panel(chat_id) را برمی‌گرداند، در غیر این صورت هیچکدام

    اگر text.startswith("/start") یا aux.get("start_id") باشد:
        قطعات = text.split(maxsplit=1)
        اگر text.startswith("/start") و len(parts) > 1 باشد، payload = parts[1].strip() در غیر این صورت (aux.get("start_id") یا "")
        تابع ()process_start(chat_id, sender, payload) را برمی‌گرداند.


def handle_inline(im, fallback_chat=None):
    """Ú©Ù„ÛŒÚ© Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ (Ø§Ø² ÙˆØ¨â€ŒÙ‡ÙˆÚ© ÛŒØ§ getUpdates).""
    اگر isinstance(im, dict) نباشد:
        بازگشت
    bid = (im.get("aux_data") or {}).get("button_id")
    ‎chat_id = im.get("chat_id")‎ یا ‎fallback_chat‎
    فرستنده = im.get("sender_id")
    اگر chat_id در بخش مدیریت باشد:
        فرستنده = فرستنده یا شناسه چت
    log.info("کلیک درون خطی | دکمه=%s | فرستنده=%s | چت=%s", پیشنهاد، فرستنده، chat_id)
    اگر bid و chat_id و sender باشند:
        handle_action(پیشنهاد، chat_id، فرستنده)


def process_update(u):
    اگر isinstance(u, dict) نباشد:
        بازگشت
    t = u.get("نوع")
    اگر t == "پیام حذف شده" باشد:
        بازگشت
    اگر t == "پیام جدید" باشد:
        امتحان کنید:
            handle_message(u.get("new_message") or {}, u.get("chat_id"))
        به جز استثنا:
            log.exception("خطای مدیریت پیام")
        بازگشت
    اگر u.get("inline_message"):
        log.info("به‌روزرسانی درون‌خطی (نظرسنجی) | %s", str(u["inline_message"])[:200])
        امتحان کنید:
            handle_inline(u["inline_message"], u.get("chat_id"))
        به جز استثنا:
            log.exception("خطای کنترل‌کننده درون‌خطی")
        بازگشت
    log.info("به‌روزرسانی دیگر | %s", str(u)[:300])


# =====================================================
# ÙˆØ®â€ŒÙ‡ÙˆÚ© (Ø¨Ø±Ø§ÛŒ Ú©Ù„ÛŒÚ© Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ø´ÛŒØ´Ù‡â€Ø§ÛŒ)
# =====================================================
def handle_webhook(داده):
    امتحان کنید:
        log.info("WEBHOOK | %s", str(data)[:300])
        به‌روزرسانی = data.get("به‌روزرسانی") یا {}
        im = data.get("inline_message") یا upd.get("new_message")
        اگر نه من:
            بازگشت
        با قفل:
            handle_inline(im, update.get("chat_id"))
    به جز استثنا:
        log.exception("خطای کنترل‌کننده وب‌هوک")


کلاس هوک (BaseHTTPRequestHandler):
    def _reply(خود، کد = 200):
        ارسال_پاسخ_خود(کد)
        self.send_header("نوع محتوا", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"OK"}')

    تعریف do_POST(خود):
        اگر self.path.split("?")[0] != WEBHOOK_PATH:
            بازگشت به self._reply(404)
        امتحان کنید:
            n = int(self.headers.get("طول-محتوا") یا 0)
            data = json.loads(self.rfile.read(n).decode("utf-8", "ignore") or "{}")
        به جز استثنا:
            داده = {}
        پاسخ به خود (200)
        threading.Thread(target=handle_webhook, args=(data,), daemon=True).start()

    تعریف do_GET(خود):
        پاسخ به خود (200)

    def log_message(خود، *args):
        عبور


شروع_وب‌هوک ():
    """Ø³Ø±ÙˆØ±Ø±Ø§ Ø¨Ø§Ù„Ø§ Ù…ÛŒâ€ŒØ¢ÙˆØ±ØØ¯ Ø¢ØØØØ±Ø³ Ø±Ø§ Ø¨Ù‡ Ù…ÛŒâ€Ø¯Ù‡Ø¯ Ø§Ú¯Ø± Ù†Ø´ØØŒ ØØ§ÙØª Ù„ÛŒÙ†Ú©. Ù…ÛŒâ€ŒÙ…Ø§Ù†Ø¯."""
    USE_INLINE سراسری
    اگر PUBLIC_URL نباشد:
        log.warning("PUBLIC_URL ØªÙ†Ø¸ÛŒÙ… Ù†Ø´Ø¯Ù‡ -> ©Ø§Ø± Ù…ÛŒâ€ŒÚ©Ù†Ù†ØØØŒ Ù†Ù‡ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ.")
        بازگشت
    امتحان کنید:
        سرور = ThreadingHTTPServer(("0.0.0.0", PORT), Hook)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        log.info("سرور وب هوک | پورت=%s | مسیر=%s", پورت, WEBHOOK_PATH)
    به جز استثنا به عنوان e:
        log.error("سرور وب هوک با خطا مواجه شد | %s", e)
        بازگشت
    آدرس اینترنتی = آدرس اینترنتی عمومی + مسیر وب هوک
    res = call("updateBotEndpoints", url=url, type="ReceiveInlineMessage")
    USE_INLINE = ok(res) و bool(res)
    log.info("ثبت وب هوک | تایید=%s | آدرس اینترنتی=%s | درون خطی=%s", تایید(res), آدرس اینترنتی, USE_INLINE)
    اگر نه USE_INLINE:
        log.warning("Ø«Ø¨Øª ÙˆØ¨â€ŒÙ‡ÙˆÚ© Ø¬ÙˆØ§Ø¨ Ù†ØØØ§Ø¯ ->


# =====================================================
# ØÙ„Ù‚Ù‡â€ŒÛŒ Ø§ØµÙ„ÛŒ
# =====================================================
تابع def skip_backlog():
    """Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ÛŒ Ù‚Ø¯ÛŒÙ…ÛŒÙ Ø²Ù…Ø§Ù† Ø®Ø§Ù…ÙˆØ´ Ø¨ÙˆØØØ¯Ù† Ø±Ø§Ù Ù…ÛŒâ€ŒÚ©Ù†Ø¯."""
    افست، صرف نظر شده = هیچکدام، 0
    برای _ در محدوده (20):
        d = {"حد": ۱۰۰}
        اگر جبران شود:
            d["offset_id"] = افست
        داده = (call("getUpdates", **d).get("data") یا {})
        ups = data.get("updates") یا []
        رد شد += لن(یو پی اس)
        nxt = data.get("next_offset_id")
        اگر nxt:
            افست = nxt
        اگر len(ups) < 100 باشد:
            استراحت
    log.info("%s به‌روزرسانی قدیمی رد شد", رد شد)
    بازگشت آفست


تابع اصلی ():
    اگر BOT_TOKEN نباشد:
        raise SystemExit("BOT_TOKEN ØªÙ†Ø¸ÛŒÙ… Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª.")
    log.info("آهنگ شروع شد | ربات=@%s | مدیران=%s", BOT_USERNAME, len(ADMINS))
    نام کاربری را شناسایی کنید()
    شروع_وب‌هوک()
    افست = skip_backlog()
    اگر os.getenv("NOTIFY_ADMINS", "1") == "1":
        برای یک مدیر:
            r = send(a, "âœ… Ø±Ø¨Ø§Øª Ø±ÙˆØ´Ù† Ø´Ø¯.\n"
                        f"Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ: Ù„ÛŒÙ†Ú©)'}")
            log.info("اطلاعیه شروع به کار | مدیر=%s | تایید=%s", a, ok(r))
            اگر خوب باشد(r):
                پنل مدیریت(a)
    در حالی که درست است:
        امتحان کنید:
            d = {"حد": ۱۰۰}
            اگر جبران شود:
                d["offset_id"] = افست
            res = فراخوانی("getUpdates", **d)
            اگر res یا res.get("status") در (هیچکدام، "OK") نباشد:
                زمان.خواب(2)
                ادامه
            data = res.get("data") یا {}
            برای u در data.get("updates") یا []:
                با قفل:
                    به‌روزرسانی فرآیند(u)
            اگر داده.دریافت("next_offset_id"):
                افست = داده["next_offset_id"]
            زمان.خواب(POLL_INTERVAL)
        به جز وقفه کیبورد:
            log.info("ربات متوقف شد")
            استراحت
        به جز استثنا:
            log.exception("خطای حلقه اصلی")
            زمان.خواب(3)


اگر __name__ == "__main__":
    اصلی ()
