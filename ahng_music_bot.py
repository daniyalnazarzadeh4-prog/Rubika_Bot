# -*- coding: utf-8 -*-
"""
AHNG MUSIC - ربات موزیک روبیکا (Rubika Bot API v3)
Python + requests + SQLite

اجرا:  BOT_TOKEN=xxxx python ahng_music_bot.py

نکته‌ی دکمه‌ها: کلیک دکمه‌ی شیشه‌ای ساده از راه getUpdates به ربات نمی‌رسد.
برای همین همه‌ی دکمه‌ها از نوع «لینک» هستند و ربات را با ?start=کد باز می‌کنند؛
ربات آن را مثل یک پیام /start عادی می‌خواند و کار دکمه را انجام می‌دهد.
اگر دکمه‌ای کار نکرد، مدیر می‌تواند همان کار را با دستور متنی انجام دهد (/upload ...).
"""

import os
import re
import time
import sqlite3
import logging
import requests
from urllib.parse import quote

# =====================================================
# تنظیمات
# =====================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = "ahng_music_bot"          # بدون @
ADMINS = {
    x.strip()
    for x in os.getenv("ADMINS", "u0HbMCz07b206d47b6e01988bf7610cf").split(",")
    if x.strip()
}
DB_FILE = os.getenv("DB_FILE", "ahng.db")
API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"
POLL_INTERVAL = 0.4
REQUEST_TIMEOUT = (5, 20)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("AHNG")

# =====================================================
# ارتباط با API
# =====================================================
session = requests.Session()


def call(method, **data):
    try:
        r = session.post(API + method, json=data, timeout=REQUEST_TIMEOUT)
        try:
            result = r.json()
        except ValueError:
            log.error("API NON-JSON | %s | http=%s | %s", method, r.status_code, r.text[:200])
            return {}
        if result.get("status") not in (None, "OK"):
            log.error("API ERROR | %s | %s", method, str(result)[:300])
        return result
    except Exception as e:
        log.error("REQUEST ERROR | %s | %s", method, e)
        return {}


def detect_username():
    """آیدی واقعی ربات را از خود روبیکا می‌گیرد تا لینک دکمه‌ها حتماً درست باشد."""
    global BOT_USERNAME
    res = call("getMe")
    data = res.get("data") or {}
    bot = data.get("bot") if isinstance(data.get("bot"), dict) else data
    uname = str(bot.get("username") or "").lstrip("@").strip()
    if uname and uname.lower() != BOT_USERNAME.lower():
        log.warning("BOT_USERNAME در کد %s بود ولی ربات واقعی %s است؛ از واقعی استفاده می‌شود", BOT_USERNAME, uname)
        BOT_USERNAME = uname
    log.info("GETME | ok=%s | username=%s", bool(res), uname or "?")


def ok(result):
    return bool(result) and result.get("status", "OK") == "OK"


# =====================================================
# دیتابیس
# =====================================================
db = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30)
db.executescript("""
CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, artist TEXT, file_id TEXT,
    downloads INTEGER DEFAULT 0, added_at INTEGER);
CREATE TABLE IF NOT EXISTS users(guid TEXT PRIMARY KEY, joined_at INTEGER);
CREATE TABLE IF NOT EXISTS channels(guid TEXT PRIMARY KEY, link TEXT);
""")
db.commit()

admin_state = {}            # guid ادمین -> مرحله‌ی فعلی
pending_channel_link = {}   # guid ادمین -> لینک کانالی که منتظر فوروارد است


# =====================================================
# دکمه‌ها (همه لینک‌اند)
# =====================================================
def bot_link(payload):
    return f"https://rubika.ir/{BOT_USERNAME}?start={quote(str(payload), safe='_')}"


def link_button(bid, text, url):
    return {"id": str(bid), "type": "Link", "button_text": text,
            "button_link": {"type": "url", "link_url": url}}


def action_button(action, text):
    return link_button(action, text, bot_link(action))


def keypad(rows):
    return {"rows": [{"buttons": row} for row in rows]}


def send(chat_id, text, buttons=None):
    if not chat_id:
        log.warning("SEND CANCELLED: chat_id خالی است")
        return {}
    d = {"chat_id": chat_id, "text": str(text)}
    if buttons:
        d["inline_keypad"] = buttons
    return call("sendMessage", **d)


# =====================================================
# کانال‌ها و عضویت
# =====================================================
def channels():
    return db.execute("SELECT guid, link FROM channels").fetchall()


def is_member(user_guid):
    if not user_guid:
        return False
    for guid, _ in channels():
        res = call("getChatMember", chat_id=guid, user_id=user_guid)
        status = str((res.get("data") or {}).get("status", "")).lower()
        if status not in ("member", "creator", "admin", "owner"):
            return False
    return True


def channel_list(chat_id):
    items = channels()
    if not items:
        return send(chat_id, "📭 هنوز کانالی ثبت نشده است.")
    text = "📋 کانال‌های ثبت‌شده:\n\n" + "\n".join(
        f"{i}. {g}\n{l}" for i, (g, l) in enumerate(items, 1))
    return send(chat_id, text)


# =====================================================
# آهنگ‌ها
# =====================================================
def song_link(song_id):
    return bot_link(f"song_{song_id}")


def get_song(song_id):
    return db.execute("SELECT title, artist, file_id FROM songs WHERE id=?", (song_id,)).fetchone()


def send_song(chat_id, song_id):
    song = get_song(song_id)
    if not song:
        return send(chat_id, "❌ آهنگ موردنظر پیدا نشد.")
    title, artist, file_id = song
    res = call("sendFile", chat_id=chat_id, file_id=file_id,
               text=f"🎵 {title}\n🎤 {artist}\n\n@{BOT_USERNAME}")
    if ok(res):
        db.execute("UPDATE songs SET downloads=downloads+1 WHERE id=?", (song_id,))
        db.commit()
        log.info("SONG SENT | song=%s | chat=%s", song_id, chat_id)
    return res


def join_prompt(chat_id, payload):
    rows = [[link_button(f"channel_{i}", f"📢 کانال {i + 1}", link)]
            for i, (_, link) in enumerate(channels())]
    rows.append([action_button(f"joined_{payload}", "✅ تأیید عضویت")])
    send(chat_id, "🔒 برای دریافت آهنگ ابتدا در کانال‌های زیر عضو شوید، سپس «تأیید عضویت» را بزنید:",
         keypad(rows))


def deliver(chat_id, user_guid, payload):
    if not payload.startswith("song_"):
        return
    song_id = payload[5:]
    if not song_id.isdigit() or not get_song(song_id):
        return send(chat_id, "❌ آهنگ پیدا نشد.")
    if channels() and not is_member(user_guid):
        return join_prompt(chat_id, payload)
    return send_song(chat_id, song_id)


def save_song(message, sender):
    f = message.get("file") or {}
    file_id = f.get("file_id")
    if not file_id:
        return None
    title = (f.get("file_name") or "آهنگ").rsplit(".", 1)[0]
    artist = "-"
    caption = (message.get("text") or "").strip()
    if "|" in caption:
        t, a = [x.strip() for x in caption.split("|", 1)]
        title, artist = (t or title), (a or "-")
    db.execute("INSERT INTO songs(title,artist,file_id,downloads,added_at) VALUES(?,?,?,0,?)",
               (title, artist, file_id, int(time.time())))
    db.commit()
    song_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    log.info("SONG SAVED | id=%s | title=%s | by=%s", song_id, title, sender)
    return song_id, title, artist


def post_to_channels(song_id, caption):
    song = get_song(song_id)
    if not song:
        return 0
    file_id = song[2]
    kp = keypad([[link_button(f"song_{song_id}", "🎧 دریافت آهنگ", song_link(song_id))]])
    done = 0
    for guid, _ in channels():
        res = call("sendFile", chat_id=guid, file_id=file_id, text=caption, inline_keypad=kp)
        if ok(res):
            done += 1
        log.info("PUBLISH | channel=%s | ok=%s", guid, ok(res))
    return done


# =====================================================
# آمار
# =====================================================
def stats(chat_id):
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    songs, downloads = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(downloads),0) FROM songs").fetchone()
    best = db.execute(
        "SELECT title, downloads FROM songs ORDER BY downloads DESC LIMIT 10").fetchall()
    text = (f"📊 آمار AHNG MUSIC\n\n👤 کاربران: {users}\n🎵 آهنگ‌ها: {songs}\n"
            f"⬇️ دانلودها: {downloads}\n\n🏆 ۱۰ آهنگ پردانلود:\n\n")
    text += ("\n".join(f"{i}. {t} | {c} دانلود" for i, (t, c) in enumerate(best, 1))
             if best else "هنوز آهنگی ثبت نشده است.")
    return send(chat_id, text)


# =====================================================
# پنل مدیر
# =====================================================
def is_admin(guid):
    return guid in ADMINS


def admin_panel(chat_id):
    rows = [
        [action_button("adm_add", "➕ افزودن آهنگ"), action_button("adm_upload", "🚀 آپلود و انتشار")],
        [action_button("adm_addch", "📢 ثبت کانال"), action_button("adm_stats", "📊 آمار")],
        [action_button("adm_channels", "📋 کانال‌ها")],
    ]
    return send(chat_id,
                "🛠 پنل مدیریت AHNG MUSIC\nیکی از گزینه‌ها را انتخاب کنید:\n\n"
                "(اگر دکمه‌ها کار نکردند: /add  /upload  /addch  /stats  /channels  /cancel)",
                keypad(rows))


def handle_action(action, chat_id, sender):
    """کار هر دکمه (چه از لینک دکمه، چه از دستور متنی)."""
    log.info("BUTTON | action=%s | sender=%s", action, sender)

    if action.startswith("adm_"):
        if not is_admin(sender):
            log.warning("IGNORED admin action from non-admin: %s", sender)
            return

        if action == "adm_add":
            admin_state[sender] = {"mode": "await_add"}
            return send(chat_id, "➕ آهنگ را ارسال یا فوروارد کنید.\n"
                                 "(در کپشن می‌توانید بنویسید: اسم آهنگ | خواننده)")
        if action == "adm_upload":
            admin_state[sender] = {"mode": "await_upload"}
            return send(chat_id, "🚀 آهنگ را ارسال یا فوروارد کنید.\n"
                                 "(در کپشن می‌توانید بنویسید: اسم آهنگ | خواننده)")
        if action == "adm_stats":
            return stats(chat_id)
        if action == "adm_channels":
            return channel_list(chat_id)
        if action == "adm_addch":
            admin_state[sender] = {"mode": "await_channel"}
            return send(chat_id, "📢 لینک یا آیدی کانال را بفرستید (مثل @mychannel).\n"
                                 "بعد یک پست از همان کانال برای من فوروارد کنید.\n"
                                 "ربات باید ادمین کانال باشد.")
        if action == "adm_cancel":
            admin_state.pop(sender, None)
            pending_channel_link.pop(sender, None)
            return send(chat_id, "❌ لغو شد. برای پنل: /panel")
        if action.startswith("adm_post_"):
            song_id = action[len("adm_post_"):]
            st = admin_state.get(sender) or {}
            if st.get("mode") != "await_confirm" or str(st.get("sid")) != song_id:
                return send(chat_id, "❌ این درخواست منقضی شده. دوباره از پنل شروع کنید: /panel")
            if not channels():
                return send(chat_id, "❌ کانالی ثبت نشده. اول «ثبت کانال» را بزنید.")
            n = post_to_channels(song_id, f"{st.get('text', '')}\n\n@{BOT_USERNAME}")
            admin_state.pop(sender, None)
            if n:
                return send(chat_id, f"✅ در {n} کانال منتشر شد.")
            return send(chat_id, "❌ انتشار انجام نشد. ربات باید ادمین کانال باشد.")
        return

    if action.startswith("joined_song_"):
        song_id = action[len("joined_song_"):]
        if not song_id.isdigit():
            return
        if is_member(sender):
            return send_song(chat_id, song_id)
        return send(chat_id, "❌ هنوز عضو همه‌ی کانال‌ها نیستید. عضو شوید و دوباره «تأیید عضویت» را بزنید.")


COMMAND_ACTIONS = {"/add": "adm_add", "/upload": "adm_upload", "/addch": "adm_addch",
                   "/stats": "adm_stats", "/channels": "adm_channels", "/cancel": "adm_cancel"}


def handle_admin(message, chat_id, sender, text):
    """پیام‌های مدیر. اگر چیزی را پردازش کرد، نتیجه‌ی غیر None برمی‌گرداند."""
    f = message.get("file")
    fwd = message.get("forwarded_from") or {}
    st = admin_state.get(sender) or {}
    mode = st.get("mode")

    # ۱) دریافت فایل آهنگ
    if f:
        saved = save_song(message, sender)
        if not saved:
            return send(chat_id, "❌ فایل آهنگ شناسایی نشد.")
        sid, title, artist = saved
        if mode == "await_upload":
            admin_state[sender] = {"mode": "await_post_text", "sid": sid}
            return send(chat_id, f"✅ ذخیره شد: {title} - {artist}\n\n✍️ حالا متن پست را بفرستید:")
        admin_state.pop(sender, None)
        return send(chat_id, f"✅ ذخیره شد: {title} - {artist}\n\n🔗 لینک اختصاصی:\n{song_link(sid)}")

    # ۲) فوروارد پست کانال برای ثبت کانال
    if fwd and sender in pending_channel_link:
        guid = fwd.get("from_chat_id")
        if not guid:
            return send(chat_id, "❌ شناسه‌ی کانال از پیام فورواردشده گرفته نشد.")
        link = pending_channel_link.pop(sender)
        db.execute("INSERT OR REPLACE INTO channels(guid, link) VALUES(?,?)", (guid, link))
        db.commit()
        log.info("CHANNEL SAVED | %s", guid)
        return send(chat_id, "✅ کانال ثبت شد. یادتان باشد ربات در کانال ادمین باشد.")

    # ۳) دستورها (/start و ناشناخته‌ها را رد می‌کند تا ادامه پیدا کنند)
    if text.startswith("/"):
        cmd = text.split()[0].lower()
        if cmd in COMMAND_ACTIONS:
            return handle_action(COMMAND_ACTIONS[cmd], chat_id, sender)
        if text.startswith("/delchannel "):
            db.execute("DELETE FROM channels WHERE guid=?", (text.split(maxsplit=1)[1].strip(),))
            db.commit()
            return send(chat_id, "✅ کانال حذف شد.")
        if text.startswith("/del "):
            sid = text.split(maxsplit=1)[1].strip()
            if not sid.isdigit():
                return send(chat_id, "❌ شناسه‌ی آهنگ معتبر نیست.")
            db.execute("DELETE FROM songs WHERE id=?", (sid,))
            db.commit()
            return send(chat_id, "✅ آهنگ حذف شد.")
        return None

    # ۴) مرحله‌های متنی
    if mode == "await_post_text" and text:
        admin_state[sender] = {"mode": "await_song_link", "sid": st["sid"], "text": text}
        return send(chat_id, "✅ متن ثبت شد.\n🔗 حالا لینک اختصاصی همین آهنگ را بفرستید:\n\n" + song_link(st["sid"]))

    if mode == "await_song_link" and text:
        m = re.search(r"song_(\d+)", text)
        if not m or m.group(1) != str(st["sid"]):
            return send(chat_id, "❌ لینک درست نیست. لینک همین آهنگ را بفرستید:\n" + song_link(st["sid"]))
        st["mode"] = "await_confirm"
        admin_state[sender] = st
        kp = keypad([[action_button(f"adm_post_{st['sid']}", "✅ تأیید نهایی"),
                      action_button("adm_cancel", "❌ لغو")]])
        return send(chat_id, f"📋 پیش‌نمایش پست:\n\n{st['text']}\n\n@{BOT_USERNAME}\n\nمنتشر شود؟", kp)

    if mode == "await_channel" and text:
        first = text.split()[0]
        if first.startswith("@") and len(first) > 2:
            link = "https://rubika.ir/" + first[1:]
        elif "rubika.ir/" in first or "rubika.me/" in first:
            link = first
        else:
            return send(chat_id, "❌ لینک یا آیدی کانال معتبر نیست.")
        pending_channel_link[sender] = link
        admin_state.pop(sender, None)
        return send(chat_id, "✅ لینک دریافت شد. حالا یک پست از همان کانال برای من فوروارد کنید.")

    return None


# =====================================================
# پیام‌ها
# =====================================================
def process_start(chat_id, sender, payload):
    log.info("START | sender=%s | payload=%s", sender, payload)
    if payload.startswith("song_"):
        return deliver(chat_id, sender, payload)
    if payload.startswith(("adm_", "joined_song_")):
        return handle_action(payload, chat_id, sender)
    if not payload:
        if is_admin(sender):
            return admin_panel(chat_id)
        return send(chat_id, "سلام 👋 به AHNG MUSIC خوش آمدید.\n"
                             "برای دریافت آهنگ از دکمه‌ی دانلود زیر پست‌های کانال استفاده کنید.")


def handle_message(message, chat_id):
    if not isinstance(message, dict):
        return
    sender = message.get("sender_id", chat_id)
    text = (message.get("text") or "").strip()
    aux = message.get("aux_data") or {}
    if not sender:
        return
    if chat_id in ADMINS:            # اگر guid چت را در ADMINS گذاشته باشند
        sender = chat_id

    db.execute("INSERT OR IGNORE INTO users(guid, joined_at) VALUES(?,?)", (sender, int(time.time())))
    db.commit()
    log.info("MESSAGE | sender=%s | text=%s", sender, text[:100])

    if text == "/myid":
        return send(chat_id, f"🆔 شناسه‌ی شما:\n{sender}\n\n💬 شناسه‌ی چت:\n{chat_id}")
    if text == "/ping":
        return send(chat_id, "pong ✅ ربات روشن است.")

    # اگر روبیکا شناسه‌ی دکمه را در aux_data بفرستد
    if aux.get("button_id"):
        return handle_action(aux["button_id"], chat_id, sender)

    if is_admin(sender) and handle_admin(message, chat_id, sender, text) is not None:
        return

    if text == "/panel":
        return admin_panel(chat_id) if is_admin(sender) else None

    if text.startswith("/start") or aux.get("start_id"):
        parts = text.split(maxsplit=1)
        # کد start یا داخل متن است یا داخل aux_data.start_id
        payload = parts[1].strip() if text.startswith("/start") and len(parts) > 1 else (aux.get("start_id") or "")
        return process_start(chat_id, sender, payload)


def process_update(u):
    if not isinstance(u, dict):
        return
    t = u.get("type")
    if t == "RemovedMessage":
        return
    if t == "NewMessage":
        try:
            handle_message(u.get("new_message") or {}, u.get("chat_id"))
        except Exception:
            log.exception("MESSAGE HANDLER ERROR")
        return
    if u.get("inline_message"):      # اگر روبیکا کلیک دکمه‌ی ساده را هم فرستاد
        im = u["inline_message"]
        bid = (im.get("aux_data") or {}).get("button_id")
        log.info("INLINE UPDATE | %s", str(im)[:200])
        if bid:
            try:
                handle_action(bid, im.get("chat_id") or u.get("chat_id"), im.get("sender_id"))
            except Exception:
                log.exception("INLINE HANDLER ERROR")
        return
    log.info("OTHER UPDATE | %s", str(u)[:300])


# =====================================================
# حلقه‌ی اصلی
# =====================================================
def skip_backlog():
    """پیام‌های قدیمیِ زمان خاموش بودن را رد می‌کند تا ربات دوباره جوابشان را ندهد."""
    offset, skipped = None, 0
    for _ in range(20):
        d = {"limit": 100}
        if offset:
            d["offset_id"] = offset
        data = (call("getUpdates", **d).get("data") or {})
        ups = data.get("updates") or []
        skipped += len(ups)
        nxt = data.get("next_offset_id")
        if nxt:
            offset = nxt
        if len(ups) < 100:
            break
    log.info("SKIPPED %s old updates", skipped)
    return offset


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN تنظیم نشده است.")
    log.info("AHNG MUSIC STARTED | bot=@%s | admins=%s", BOT_USERNAME, len(ADMINS))
    detect_username()
    offset = skip_backlog()
    if os.getenv("NOTIFY_ADMINS", "1") == "1":
        for a in ADMINS:
            r = send(a, "✅ ربات روشن شد.")
            log.info("STARTUP NOTICE | admin=%s | ok=%s", a, ok(r))
            if ok(r):
                admin_panel(a)
    while True:
        try:
            d = {"limit": 100}
            if offset:
                d["offset_id"] = offset
            res = call("getUpdates", **d)
            if not res or res.get("status") not in (None, "OK"):
                time.sleep(2)
                continue
            data = res.get("data") or {}
            for u in data.get("updates") or []:
                process_update(u)
            if data.get("next_offset_id"):
                offset = data["next_offset_id"]
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            log.info("BOT STOPPED")
            break
        except Exception:
            log.exception("MAIN LOOP ERROR")
            time.sleep(3)


if __name__ == "__main__":
    main()
