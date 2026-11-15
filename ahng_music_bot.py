# -*- coding: utf-8 -*-
"""
AHNG MUSIC - ربات موسیقی روبیکا
اجرا: BOT_TOKEN=xxxx python ahng_music_bot.py
"""
import os
import re
import time
import sqlite3
import requests

# ============ تنظیمات ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMINS = {"u0HbMCz07b206d47b6e01988bf7610cf"}      # guid مدیرها (با /myid می‌گیرید)
BOT_USERNAME = "ahng_music_bot"      # آیدی ربات بدون @
DB_FILE = os.getenv("DB_FILE", "ahng.db")
API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"

# ============ دیتابیس ============
db = sqlite3.connect(DB_FILE, check_same_thread=False)
db.executescript("""
CREATE TABLE IF NOT EXISTS songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, artist TEXT, file_id TEXT, downloads INTEGER DEFAULT 0, added_at INTEGER);
CREATE TABLE IF NOT EXISTS users(guid TEXT PRIMARY KEY, joined_at INTEGER);
CREATE TABLE IF NOT EXISTS channels(guid TEXT PRIMARY KEY, link TEXT);
""")
db.commit()


# ============ API ============
def call(method, **data):
    try:
        return requests.post(API + method, json=data, timeout=30).json()
    except Exception as e:
        print("API error:", method, e)
        return {}


def send(chat_id, text, keypad=None):
    d = {"chat_id": chat_id, "text": text}
    if keypad:
        d["inline_keypad"] = keypad
    return call("sendMessage", **d)


def simple_btn(bid, text):
    return {"id": bid, "type": "Simple", "button_text": text}


def link_btn(bid, text, url):
    return {"id": bid, "type": "Link", "button_text": text,
            "button_link": {"type": "url", "link_url": url}}


def keypad(rows):
    return {"rows": [{"buttons": r} for r in rows]}


# ============ کانال‌ها و عضویت ============
def channels():
    return db.execute("SELECT guid, link FROM channels").fetchall()


def is_member(user_guid):
    """هر بار از روبیکا پرسیده می‌شود (ذخیره نمی‌شود)، پس خروج از کانال هم دیده می‌شود."""
    for guid, _ in channels():
        res = call("getChatMember", chat_id=guid, user_id=user_guid)
        status = str((res.get("data") or {}).get("status", "")).lower()
        if status not in ("member", "creator", "admin", "owner"):
            return False
    return True


def join_prompt(chat_id, payload):
    rows = [[link_btn(f"ch{i}", f"📢 کانال {i + 1}", link)] for i, (_, link) in enumerate(channels())]
    rows.append([simple_btn(f"joined:{payload}", "✅ تأیید عضویت")])
    send(chat_id, "برای دریافت آهنگ ابتدا در کانال(های) زیر عضو شوید، سپس «تأیید عضویت» را بزنید.",
         keypad(rows))


# ============ آهنگ‌ها ============
def song_link(sid):
    return f"https://rubika.ir/{BOT_USERNAME}?start=song_{sid}"


def send_song(chat_id, song_id):
    row = db.execute("SELECT title, artist, file_id FROM songs WHERE id=?", (song_id,)).fetchone()
    if not row:
        return send(chat_id, "آهنگ پیدا نشد.")
    title, artist, file_id = row
    call("sendFile", chat_id=chat_id, file_id=file_id,
         text=f"🎵 {title}\n🎤 {artist}\n\n@{BOT_USERNAME}")
    db.execute("UPDATE songs SET downloads=downloads+1 WHERE id=?", (song_id,))
    db.commit()


def deliver(chat_id, user_guid, payload):
    """دریافت آهنگ: اگر عضو نباشد عضویت اجباری، وگرنه ارسال."""
    if not payload.startswith("song_"):
        return
    if channels() and not is_member(user_guid):
        return join_prompt(chat_id, payload)
    send_song(chat_id, payload[5:])


def stats(chat_id):
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    songs, dl = db.execute("SELECT COUNT(*), COALESCE(SUM(downloads),0) FROM songs").fetchone()
    best = db.execute("SELECT id, title, downloads FROM songs ORDER BY downloads DESC LIMIT 10").fetchall()
    txt = f"📊 آمار AHNG MUSIC\n👤 کاربران: {users}\n🎵 آهنگ‌ها: {songs}\n⬇️ دانلودها: {dl}\n\n"
    txt += "\n".join(f"{i}. {t} ← {d}" for i, t, d in best)
    send(chat_id, txt)


# ============ پنل مدیر ============
def is_admin(guid):
    return guid in ADMINS


def admin_panel(chat_id):
    rows = [
        [simple_btn("adm:add", "➕ افزودن آهنگ"), simple_btn("adm:upload", "🚀 آپلود و انتشار")],
        [simple_btn("adm:addch", "📢 ثبت کانال"), simple_btn("adm:stats", "📊 آمار")],
        [simple_btn("adm:channels", "📋 کانال‌ها")],
    ]
    send(chat_id, "🛠 پنل مدیریت AHNG MUSIC\nیکی از گزینه‌ها را انتخاب کنید:", keypad(rows))


def post_to_channels(sid, caption):
    """انتشار آهنگ در کانال‌های ثبت‌شده با دکمه‌ی شیشه‌ای دریافت."""
    row = db.execute("SELECT file_id FROM songs WHERE id=?", (sid,)).fetchone()
    if not row:
        return 0
    kp = keypad([[link_btn("dl", "🎧 دریافت آهنگ", song_link(sid))]])
    ok = 0
    for guid, _ in channels():
        res = call("sendFile", chat_id=guid, file_id=row[0], text=caption, inline_keypad=kp)
        if res and res.get("status", "OK") == "OK":
            ok += 1
    return ok


# ============ پیام‌ها ============
admin_state = {}            # admin guid -> مرحله‌ی فعلی (افزودن/آپلود)
pending_channel_link = {}   # admin guid -> لینک کانالی که منتظر فوروارد پست است


def handle_admin(m, chat_id, sender, text):
    f = m.get("file")
    fwd = m.get("forwarded_from") or {}

    # ۱) فرستادن آهنگ -> ذخیره + ساخت لینک اختصاصی
    if f:
        name = (f.get("file_name") or "آهنگ").rsplit(".", 1)[0]
        title, artist = (name, "-")
        if text:
            title, artist = [x.strip() for x in (text.split("|", 1) + ["-"])[:2]]
        db.execute("INSERT INTO songs(title,artist,file_id,added_at) VALUES(?,?,?,?)",
                   (title, artist, f["file_id"], int(time.time())))
        db.commit()
        sid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        st = admin_state.get(sender) or {}
        if st.get("mode") == "await_song_upload":
            admin_state[sender] = {"mode": "saved", "sid": sid}
            return send(chat_id, f"✅ ذخیره شد: {title} - {artist}\nبرای ادامه دکمه‌ی زیر را بزنید:",
                        keypad([[simple_btn(f"adm:text:{sid}", "✍️ نوشتن متن پست")]]))
        admin_state.pop(sender, None)
        send(chat_id, f"✅ ذخیره شد: {title} - {artist}\nلینک اختصاصی (کپی کنید و در دکمه‌ی شیشه‌ای پست کانال بگذارید):")
        return send(chat_id, song_link(sid))

    # مراحل آپلود: متن پست -> لینک اختصاصی -> تأیید نهایی
    st = admin_state.get(sender) or {}
    mode = st.get("mode")
    if mode in ("await_text", "await_link") and text and not text.startswith("/"):
        sid = st["sid"]
        if mode == "await_text":
            st["text"] = text
            st["mode"] = "await_link"
            return send(chat_id, "✅ متن ثبت شد.\nحالا لینک اختصاصی آهنگ را بفرستید:\n" + song_link(sid))
        mm = re.search(r"song_(\d+)", text)
        if not mm or mm.group(1) != str(sid):
            return send(chat_id, "لینک درست نیست. لینک اختصاصی همین آهنگ را بفرستید:\n" + song_link(sid))
        st["mode"] = "await_confirm"
        return send(chat_id, f"پیش‌نمایش پست:\n\n{st['text']}\n\n@{BOT_USERNAME}\n\nتأیید می‌کنید در کانال منتشر شود؟",
                    keypad([[simple_btn(f"adm:post:{sid}", "✅ تأیید نهایی"), simple_btn("adm:cancel", "❌ لغو")]]))

    # ۲) فوروارد پست کانال -> ثبت guid کانال
    if fwd and pending_channel_link.get(sender):
        guid = fwd.get("from_chat_id")
        if guid:
            db.execute("INSERT OR REPLACE INTO channels VALUES(?,?)", (guid, pending_channel_link.pop(sender)))
            db.commit()
            return send(chat_id, "✅ کانال ثبت شد. یادتان باشد ربات در کانال ادمین باشد.")

    # ۳) لینک کانال -> تلاش برای عضو شدن + درخواست فوروارد
    first = text.split()[0] if text else ""
    is_username = first.startswith("@") and len(first) > 2 and first[1:].lower() != BOT_USERNAME.lower()
    is_link = ("rubika.ir/" in first or "rubika.me/" in first) and BOT_USERNAME.lower() not in first.lower()
    if is_username or is_link:
        if True:
            link = "https://rubika.ir/" + first[1:] if is_username else first
            pending_channel_link[sender] = link
            call("joinChannelByLink", link=link)   # ممکن است در Bot API پشتیبانی نشود
            return send(chat_id, "لینک ثبت شد. حالا یک پست از همان کانال را برای من فوروارد کنید تا شناسه‌ی کانال را بگیرم.\n"
                                 "(اگر ربات خودش عضو نشد، آن را ادمین کانال کنید.)")

    if text == "/stats":
        return stats(chat_id)
    if text == "/channels":
        return send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "کانالی ثبت نشده.")
    if text.startswith("/delchannel "):
        db.execute("DELETE FROM channels WHERE guid=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "حذف شد.")
    if text.startswith("/del "):
        db.execute("DELETE FROM songs WHERE id=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "آهنگ حذف شد.")
    return None


def handle_message(m, chat_id):
    sender = m.get("sender_id", chat_id)
    text = (m.get("text") or "").strip()
    db.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (sender, int(time.time())))
    db.commit()

    if text == "/myid":
        return send(chat_id, f"guid شما:\n{sender}")

    if sender in ADMINS and handle_admin(m, chat_id, sender, text) is not None:
        return

    if text == "/panel" and is_admin(sender):
        return admin_panel(chat_id)

    if text.startswith("/start"):
        parts = text.split()
        payload = parts[1] if len(parts) > 1 else (m.get("aux_data") or {}).get("start_id", "")
        if payload:
            return deliver(chat_id, sender, payload)
        if is_admin(sender):
            return admin_panel(chat_id)
        return send(chat_id, "سلام 👋 به AHNG MUSIC خوش آمدید.\nبرای دریافت آهنگ از دکمه‌ی دانلود زیر پست‌های کانال استفاده کنید.")


def handle_button(inline, chat_id):
    bid = (inline.get("aux_data") or {}).get("button_id", "")
    sender = inline.get("sender_id", chat_id)

    # دکمه‌های پنل مدیر: فقط برای ادمین‌ها
    if bid.startswith("adm:"):
        if not is_admin(sender):
            return
        if bid == "adm:add":
            admin_state[sender] = {"mode": "await_song_add"}
            send(chat_id, "➕ آهنگ را بفرستید یا فوروارد کنید.\n"
                          "(در کپشن می‌توانید بنویسید: اسم آهنگ | خواننده)\n"
                          "بعد از ذخیره، لینک اختصاصی آهنگ را می‌گیرید.")
        elif bid == "adm:upload":
            admin_state[sender] = {"mode": "await_song_upload"}
            send(chat_id, "🚀 آهنگ را بفرستید یا فوروارد کنید.\n"
                          "(در کپشن می‌توانید بنویسید: اسم آهنگ | خواننده)")
        elif bid.startswith("adm:text:"):
            admin_state[sender] = {"mode": "await_text", "sid": bid[9:]}
            send(chat_id, "✍️ متن پست را بنویسید و بفرستید:")
        elif bid.startswith("adm:post:"):
            st = admin_state.get(sender) or {}
            sid = bid[9:]
            if st.get("mode") != "await_confirm" or str(st.get("sid")) != sid:
                send(chat_id, "این درخواست منقضی شده. دوباره از پنل شروع کنید: /panel")
            elif not channels():
                send(chat_id, "کانالی ثبت نشده. اول «📢 ثبت کانال» را بزنید.")
            else:
                n = post_to_channels(sid, f"{st.get('text', '')}\n\n@{BOT_USERNAME}")
                admin_state.pop(sender, None)
                send(chat_id, f"✅ منتشر شد در {n} کانال." if n else "❌ ارسال به کانال انجام نشد. ربات باید ادمین کانال باشد.")
        elif bid == "adm:cancel":
            admin_state.pop(sender, None)
            send(chat_id, "لغو شد. برای پنل: /panel")
        elif bid == "adm:addch":
            send(chat_id, "📢 لینک یا آیدی کانال را بفرستید (مثل @mychannel).\n"
                          "بعد یک پست از همان کانال را برای من فوروارد کنید.\n"
                          "ربات باید ادمین کانال باشد.")
        elif bid == "adm:stats":
            stats(chat_id)
        elif bid == "adm:channels":
            send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "کانالی ثبت نشده.")
        return

    if bid.startswith("joined:"):
        payload = bid[7:]
        if is_member(sender):
            send_song(chat_id, payload[5:])
        else:
            send(chat_id, "هنوز عضو نیستید ❌ ابتدا در کانال عضو شوید و دوباره «تأیید عضویت» را بزنید.")


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN تنظیم نشده است.")
    offset = None
    print("AHNG MUSIC bot started...")
    while True:
        d = {"limit": 50}
        if offset:
            d["offset_id"] = offset
        data = call("getUpdates", **d).get("data") or {}
        offset = data.get("next_offset_id", offset)
        for u in data.get("updates", []):
            try:
                chat_id = u.get("chat_id")
                if u.get("type") == "NewMessage":
                    handle_message(u["new_message"], chat_id)
                elif u.get("inline_message"):
                    handle_button(u["inline_message"], chat_id)
            except Exception as e:
                print("handler error:", e)
        time.sleep(1)


if __name__ == "__main__":
    main()
