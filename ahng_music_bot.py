# -*- coding: utf-8 -*-
"""
AHNG MUSIC - Ø±Ø¨Ø§Øª Ù…ÙˆØ³ÛŒÙ‚ÛŒ Ø±ÙˆØ¨ÛŒÚ©Ø§
Ø§Ø¬Ø±Ø§: BOT_TOKEN=xxxx python ahng_music_bot.py
"""
import os
import re
import time
import sqlite3
import requests

# ============ ØªÙ†Ø¸ÛŒÙ…Ø§Øª ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMINS = {"u0HbMCz07b206d47b6e01988bf7610cf"}      # guid Ù…Ø¯ÛŒØ±Ù‡Ø§ (Ø¨Ø§ /myid Ù…ÛŒâ€ŒÚ¯ÛŒØ±ÛŒØ¯)
BOT_USERNAME = "ahng_music_bot"      # Ø¢ÛŒØ¯ÛŒ Ø±Ø¨Ø§Øª Ø¨Ø¯ÙˆÙ† @
DB_FILE = os.getenv("DB_FILE", "ahng.db")
API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"

# ============ Ø¯ÛŒØªØ§Ø¨ÛŒØ³ ============
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


# ============ Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§ Ùˆ Ø¹Ø¶ÙˆÛŒØª ============
def channels():
    return db.execute("SELECT guid, link FROM channels").fetchall()


def is_member(user_guid):
    """Ù‡Ø± Ø¨Ø§Ø± Ø§Ø² Ø±ÙˆØ¨ÛŒÚ©Ø§ Ù¾Ø±Ø³ÛŒØ¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯ (Ø°Ø®ÛŒØ±Ù‡ Ù†Ù…ÛŒâ€ŒØ´ÙˆØ¯)ØŒ Ù¾Ø³ Ø®Ø±ÙˆØ¬ Ø§Ø² Ú©Ø§Ù†Ø§Ù„ Ù‡Ù… Ø¯ÛŒØ¯Ù‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯."""
    for guid, _ in channels():
        res = call("getChatMember", chat_id=guid, user_id=user_guid)
        status = str((res.get("data") or {}).get("status", "")).lower()
        if status not in ("member", "creator", "admin", "owner"):
            return False
    return True


def join_prompt(chat_id, payload):
    rows = [[link_btn(f"ch{i}", f"ðŸ“¢ Ú©Ø§Ù†Ø§Ù„ {i + 1}", link)] for i, (_, link) in enumerate(channels())]
    rows.append([simple_btn(f"joined:{payload}", "âœ… ØªØ£ÛŒÛŒØ¯ Ø¹Ø¶ÙˆÛŒØª")])
    send(chat_id, "Ø¨Ø±Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù‡Ù†Ú¯ Ø§Ø¨ØªØ¯Ø§ Ø¯Ø± Ú©Ø§Ù†Ø§Ù„(Ù‡Ø§ÛŒ) Ø²ÛŒØ± Ø¹Ø¶Ùˆ Ø´ÙˆÛŒØ¯ØŒ Ø³Ù¾Ø³ Â«ØªØ£ÛŒÛŒØ¯ Ø¹Ø¶ÙˆÛŒØªÂ» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯.",
         keypad(rows))


# ============ Ø¢Ù‡Ù†Ú¯â€ŒÙ‡Ø§ ============
def song_link(sid):
    return f"https://rubika.ir/{BOT_USERNAME}?start=song_{sid}"


def send_song(chat_id, song_id):
    row = db.execute("SELECT title, artist, file_id FROM songs WHERE id=?", (song_id,)).fetchone()
    if not row:
        return send(chat_id, "Ø¢Ù‡Ù†Ú¯ Ù¾ÛŒØ¯Ø§ Ù†Ø´Ø¯.")
    title, artist, file_id = row
    call("sendFile", chat_id=chat_id, file_id=file_id,
         text=f"ðŸŽµ {title}\nðŸŽ¤ {artist}\n\n@{BOT_USERNAME}")
    db.execute("UPDATE songs SET downloads=downloads+1 WHERE id=?", (song_id,))
    db.commit()


def deliver(chat_id, user_guid, payload):
    """Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù‡Ù†Ú¯: Ø§Ú¯Ø± Ø¹Ø¶Ùˆ Ù†Ø¨Ø§Ø´Ø¯ Ø¹Ø¶ÙˆÛŒØª Ø§Ø¬Ø¨Ø§Ø±ÛŒØŒ ÙˆÚ¯Ø±Ù†Ù‡ Ø§Ø±Ø³Ø§Ù„."""
    if not payload.startswith("song_"):
        return
    if channels() and not is_member(user_guid):
        return join_prompt(chat_id, payload)
    send_song(chat_id, payload[5:])


def stats(chat_id):
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    songs, dl = db.execute("SELECT COUNT(*), COALESCE(SUM(downloads),0) FROM songs").fetchone()
    best = db.execute("SELECT id, title, downloads FROM songs ORDER BY downloads DESC LIMIT 10").fetchall()
    txt = f"ðŸ“Š Ø¢Ù…Ø§Ø± AHNG MUSIC\nðŸ‘¤ Ú©Ø§Ø±Ø¨Ø±Ø§Ù†: {users}\nðŸŽµ Ø¢Ù‡Ù†Ú¯â€ŒÙ‡Ø§: {songs}\nâ¬‡ï¸ Ø¯Ø§Ù†Ù„ÙˆØ¯Ù‡Ø§: {dl}\n\n"
    txt += "\n".join(f"{i}. {t} â† {d}" for i, t, d in best)
    send(chat_id, txt)


# ============ Ù¾Ù†Ù„ Ù…Ø¯ÛŒØ± ============
def is_admin(guid):
    return guid in ADMINS


def admin_panel(chat_id):
    rows = [
        [simple_btn("adm:add", "âž• Ø§ÙØ²ÙˆØ¯Ù† Ø¢Ù‡Ù†Ú¯"), simple_btn("adm:upload", "ðŸš€ Ø¢Ù¾Ù„ÙˆØ¯ Ùˆ Ø§Ù†ØªØ´Ø§Ø±")],
        [simple_btn("adm:addch", "ðŸ“¢ Ø«Ø¨Øª Ú©Ø§Ù†Ø§Ù„"), simple_btn("adm:stats", "ðŸ“Š Ø¢Ù…Ø§Ø±")],
        [simple_btn("adm:channels", "ðŸ“‹ Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§")],
    ]
    send(chat_id, "ðŸ›  Ù¾Ù†Ù„ Ù…Ø¯ÛŒØ±ÛŒØª AHNG MUSIC\nÛŒÚ©ÛŒ Ø§Ø² Ú¯Ø²ÛŒÙ†Ù‡â€ŒÙ‡Ø§ Ø±Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ù†ÛŒØ¯:", keypad(rows))


def post_to_channels(sid, caption):
    """Ø§Ù†ØªØ´Ø§Ø± Ø¢Ù‡Ù†Ú¯ Ø¯Ø± Ú©Ø§Ù†Ø§Ù„â€ŒÙ‡Ø§ÛŒ Ø«Ø¨Øªâ€ŒØ´Ø¯Ù‡ Ø¨Ø§ Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ Ø¯Ø±ÛŒØ§ÙØª."""
    row = db.execute("SELECT file_id FROM songs WHERE id=?", (sid,)).fetchone()
    if not row:
        return 0
    kp = keypad([[link_btn("dl", "ðŸŽ§ Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù‡Ù†Ú¯", song_link(sid))]])
    ok = 0
    for guid, _ in channels():
        res = call("sendFile", chat_id=guid, file_id=row[0], text=caption, inline_keypad=kp)
        if res and res.get("status", "OK") == "OK":
            ok += 1
    return ok


# ============ Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§ ============
admin_state = {}            # admin guid -> Ù…Ø±Ø­Ù„Ù‡â€ŒÛŒ ÙØ¹Ù„ÛŒ (Ø§ÙØ²ÙˆØ¯Ù†/Ø¢Ù¾Ù„ÙˆØ¯)
pending_channel_link = {}   # admin guid -> Ù„ÛŒÙ†Ú© Ú©Ø§Ù†Ø§Ù„ÛŒ Ú©Ù‡ Ù…Ù†ØªØ¸Ø± ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ù¾Ø³Øª Ø§Ø³Øª


def handle_admin(m, chat_id, sender, text):
    f = m.get("file")
    fwd = m.get("forwarded_from") or {}

    # Û±) ÙØ±Ø³ØªØ§Ø¯Ù† Ø¢Ù‡Ù†Ú¯ -> Ø°Ø®ÛŒØ±Ù‡ + Ø³Ø§Ø®Øª Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ
    if f:
        name = (f.get("file_name") or "Ø¢Ù‡Ù†Ú¯").rsplit(".", 1)[0]
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
            return send(chat_id, f"âœ… Ø°Ø®ÛŒØ±Ù‡ Ø´Ø¯: {title} - {artist}\nØ¨Ø±Ø§ÛŒ Ø§Ø¯Ø§Ù…Ù‡ Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø²ÛŒØ± Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯:",
                        keypad([[simple_btn(f"adm:text:{sid}", "âœï¸ Ù†ÙˆØ´ØªÙ† Ù…ØªÙ† Ù¾Ø³Øª")]]))
        admin_state.pop(sender, None)
        send(chat_id, f"âœ… Ø°Ø®ÛŒØ±Ù‡ Ø´Ø¯: {title} - {artist}\nÙ„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ (Ú©Ù¾ÛŒ Ú©Ù†ÛŒØ¯ Ùˆ Ø¯Ø± Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ Ù¾Ø³Øª Ú©Ø§Ù†Ø§Ù„ Ø¨Ú¯Ø°Ø§Ø±ÛŒØ¯):")
        return send(chat_id, song_link(sid))

    # Ù…Ø±Ø§Ø­Ù„ Ø¢Ù¾Ù„ÙˆØ¯: Ù…ØªÙ† Ù¾Ø³Øª -> Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ -> ØªØ£ÛŒÛŒØ¯ Ù†Ù‡Ø§ÛŒÛŒ
    st = admin_state.get(sender) or {}
    mode = st.get("mode")
    if mode in ("await_text", "await_link") and text and not text.startswith("/"):
        sid = st["sid"]
        if mode == "await_text":
            st["text"] = text
            st["mode"] = "await_link"
            return send(chat_id, "âœ… Ù…ØªÙ† Ø«Ø¨Øª Ø´Ø¯.\nØ­Ø§Ù„Ø§ Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø¨ÙØ±Ø³ØªÛŒØ¯:\n" + song_link(sid))
        mm = re.search(r"song_(\d+)", text)
        if not mm or mm.group(1) != str(sid):
            return send(chat_id, "Ù„ÛŒÙ†Ú© Ø¯Ø±Ø³Øª Ù†ÛŒØ³Øª. Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ Ù‡Ù…ÛŒÙ† Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø¨ÙØ±Ø³ØªÛŒØ¯:\n" + song_link(sid))
        st["mode"] = "await_confirm"
        return send(chat_id, f"Ù¾ÛŒØ´â€ŒÙ†Ù…Ø§ÛŒØ´ Ù¾Ø³Øª:\n\n{st['text']}\n\n@{BOT_USERNAME}\n\nØªØ£ÛŒÛŒØ¯ Ù…ÛŒâ€ŒÚ©Ù†ÛŒØ¯ Ø¯Ø± Ú©Ø§Ù†Ø§Ù„ Ù…Ù†ØªØ´Ø± Ø´ÙˆØ¯ØŸ",
                    keypad([[simple_btn(f"adm:post:{sid}", "âœ… ØªØ£ÛŒÛŒØ¯ Ù†Ù‡Ø§ÛŒÛŒ"), simple_btn("adm:cancel", "âŒ Ù„ØºÙˆ")]]))

    # Û²) ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ù¾Ø³Øª Ú©Ø§Ù†Ø§Ù„ -> Ø«Ø¨Øª guid Ú©Ø§Ù†Ø§Ù„
    if fwd and pending_channel_link.get(sender):
        guid = fwd.get("from_chat_id")
        if guid:
            db.execute("INSERT OR REPLACE INTO channels VALUES(?,?)", (guid, pending_channel_link.pop(sender)))
            db.commit()
            return send(chat_id, "âœ… Ú©Ø§Ù†Ø§Ù„ Ø«Ø¨Øª Ø´Ø¯. ÛŒØ§Ø¯ØªØ§Ù† Ø¨Ø§Ø´Ø¯ Ø±Ø¨Ø§Øª Ø¯Ø± Ú©Ø§Ù†Ø§Ù„ Ø§Ø¯Ù…ÛŒÙ† Ø¨Ø§Ø´Ø¯.")

    # Û³) Ù„ÛŒÙ†Ú© Ú©Ø§Ù†Ø§Ù„ -> ØªÙ„Ø§Ø´ Ø¨Ø±Ø§ÛŒ Ø¹Ø¶Ùˆ Ø´Ø¯Ù† + Ø¯Ø±Ø®ÙˆØ§Ø³Øª ÙÙˆØ±ÙˆØ§Ø±Ø¯
    first = text.split()[0] if text else ""
    is_username = first.startswith("@") and len(first) > 2 and first[1:].lower() != BOT_USERNAME.lower()
    is_link = ("rubika.ir/" in first or "rubika.me/" in first) and BOT_USERNAME.lower() not in first.lower()
    if is_username or is_link:
        if True:
            link = "https://rubika.ir/" + first[1:] if is_username else first
            pending_channel_link[sender] = link
            call("joinChannelByLink", link=link)   # Ù…Ù…Ú©Ù† Ø§Ø³Øª Ø¯Ø± Bot API Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒ Ù†Ø´ÙˆØ¯
            return send(chat_id, "Ù„ÛŒÙ†Ú© Ø«Ø¨Øª Ø´Ø¯. Ø­Ø§Ù„Ø§ ÛŒÚ© Ù¾Ø³Øª Ø§Ø² Ù‡Ù…Ø§Ù† Ú©Ø§Ù†Ø§Ù„ Ø±Ø§ Ø¨Ø±Ø§ÛŒ Ù…Ù† ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯ ØªØ§ Ø´Ù†Ø§Ø³Ù‡â€ŒÛŒ Ú©Ø§Ù†Ø§Ù„ Ø±Ø§ Ø¨Ú¯ÛŒØ±Ù….\n"
                                 "(Ø§Ú¯Ø± Ø±Ø¨Ø§Øª Ø®ÙˆØ¯Ø´ Ø¹Ø¶Ùˆ Ù†Ø´Ø¯ØŒ Ø¢Ù† Ø±Ø§ Ø§Ø¯Ù…ÛŒÙ† Ú©Ø§Ù†Ø§Ù„ Ú©Ù†ÛŒØ¯.)")

    if text == "/stats":
        return stats(chat_id)
    if text == "/channels":
        return send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "Ú©Ø§Ù†Ø§Ù„ÛŒ Ø«Ø¨Øª Ù†Ø´Ø¯Ù‡.")
    if text.startswith("/delchannel "):
        db.execute("DELETE FROM channels WHERE guid=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "Ø­Ø°Ù Ø´Ø¯.")
    if text.startswith("/del "):
        db.execute("DELETE FROM songs WHERE id=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "Ø¢Ù‡Ù†Ú¯ Ø­Ø°Ù Ø´Ø¯.")
    return None


def handle_message(m, chat_id):
    sender = m.get("sender_id", chat_id)
    text = (m.get("text") or "").strip()
    db.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (sender, int(time.time())))
    db.commit()

    # ÙØ´Ø±Ø¯Ù† Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø´ÛŒØ´Ù‡â€ŒØ§ÛŒ Ù…Ù…Ú©Ù† Ø§Ø³Øª Ø¨Ù‡ Ø´Ú©Ù„ Ù¾ÛŒØ§Ù… Ø¹Ø§Ø¯ÛŒ Ø¨Ø§ aux_data.button_id Ø¨Ø±Ø³Ø¯
    aux = m.get("aux_data") or {}
    if aux.get("button_id"):
        print("BUTTON (message):", aux.get("button_id"), "from", sender)
        return handle_button({"aux_data": aux, "sender_id": sender}, chat_id)

    if text == "/myid":
        return send(chat_id, f"guid Ø´Ù…Ø§:\n{sender}")

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
        return send(chat_id, "Ø³Ù„Ø§Ù… ðŸ‘‹ Ø¨Ù‡ AHNG MUSIC Ø®ÙˆØ´ Ø¢Ù…Ø¯ÛŒØ¯.\nØ¨Ø±Ø§ÛŒ Ø¯Ø±ÛŒØ§ÙØª Ø¢Ù‡Ù†Ú¯ Ø§Ø² Ø¯Ú©Ù…Ù‡â€ŒÛŒ Ø¯Ø§Ù†Ù„ÙˆØ¯ Ø²ÛŒØ± Ù¾Ø³Øªâ€ŒÙ‡Ø§ÛŒ Ú©Ø§Ù†Ø§Ù„ Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.")


def handle_button(inline, chat_id):
    bid = (inline.get("aux_data") or {}).get("button_id") or inline.get("button_id") or ""
    sender = inline.get("sender_id", chat_id)

    # Ø¯Ú©Ù…Ù‡â€ŒÙ‡Ø§ÛŒ Ù¾Ù†Ù„ Ù…Ø¯ÛŒØ±: ÙÙ‚Ø· Ø¨Ø±Ø§ÛŒ Ø§Ø¯Ù…ÛŒÙ†â€ŒÙ‡Ø§
    if bid.startswith("adm:"):
        if not is_admin(sender):
            return
        if bid == "adm:add":
            admin_state[sender] = {"mode": "await_song_add"}
            send(chat_id, "âž• Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø¨ÙØ±Ø³ØªÛŒØ¯ ÛŒØ§ ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.\n"
                          "(Ø¯Ø± Ú©Ù¾Ø´Ù† Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯: Ø§Ø³Ù… Ø¢Ù‡Ù†Ú¯ | Ø®ÙˆØ§Ù†Ù†Ø¯Ù‡)\n"
                          "Ø¨Ø¹Ø¯ Ø§Ø² Ø°Ø®ÛŒØ±Ù‡ØŒ Ù„ÛŒÙ†Ú© Ø§Ø®ØªØµØ§ØµÛŒ Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ù…ÛŒâ€ŒÚ¯ÛŒØ±ÛŒØ¯.")
        elif bid == "adm:upload":
            admin_state[sender] = {"mode": "await_song_upload"}
            send(chat_id, "ðŸš€ Ø¢Ù‡Ù†Ú¯ Ø±Ø§ Ø¨ÙØ±Ø³ØªÛŒØ¯ ÛŒØ§ ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.\n"
                          "(Ø¯Ø± Ú©Ù¾Ø´Ù† Ù…ÛŒâ€ŒØªÙˆØ§Ù†ÛŒØ¯ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯: Ø§Ø³Ù… Ø¢Ù‡Ù†Ú¯ | Ø®ÙˆØ§Ù†Ù†Ø¯Ù‡)")
        elif bid.startswith("adm:text:"):
            admin_state[sender] = {"mode": "await_text", "sid": bid[9:]}
            send(chat_id, "âœï¸ Ù…ØªÙ† Ù¾Ø³Øª Ø±Ø§ Ø¨Ù†ÙˆÛŒØ³ÛŒØ¯ Ùˆ Ø¨ÙØ±Ø³ØªÛŒØ¯:")
        elif bid.startswith("adm:post:"):
            st = admin_state.get(sender) or {}
            sid = bid[9:]
            if st.get("mode") != "await_confirm" or str(st.get("sid")) != sid:
                send(chat_id, "Ø§ÛŒÙ† Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ù…Ù†Ù‚Ø¶ÛŒ Ø´Ø¯Ù‡. Ø¯ÙˆØ¨Ø§Ø±Ù‡ Ø§Ø² Ù¾Ù†Ù„ Ø´Ø±ÙˆØ¹ Ú©Ù†ÛŒØ¯: /panel")
            elif not channels():
                send(chat_id, "Ú©Ø§Ù†Ø§Ù„ÛŒ Ø«Ø¨Øª Ù†Ø´Ø¯Ù‡. Ø§ÙˆÙ„ Â«ðŸ“¢ Ø«Ø¨Øª Ú©Ø§Ù†Ø§Ù„Â» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯.")
            else:
                n = post_to_channels(sid, f"{st.get('text', '')}\n\n@{BOT_USERNAME}")
                admin_state.pop(sender, None)
                send(chat_id, f"âœ… Ù…Ù†ØªØ´Ø± Ø´Ø¯ Ø¯Ø± {n} Ú©Ø§Ù†Ø§Ù„." if n else "âŒ Ø§Ø±Ø³Ø§Ù„ Ø¨Ù‡ Ú©Ø§Ù†Ø§Ù„ Ø§Ù†Ø¬Ø§Ù… Ù†Ø´Ø¯. Ø±Ø¨Ø§Øª Ø¨Ø§ÛŒØ¯ Ø§Ø¯Ù…ÛŒÙ† Ú©Ø§Ù†Ø§Ù„ Ø¨Ø§Ø´Ø¯.")
        elif bid == "adm:cancel":
            admin_state.pop(sender, None)
            send(chat_id, "Ù„ØºÙˆ Ø´Ø¯. Ø¨Ø±Ø§ÛŒ Ù¾Ù†Ù„: /panel")
        elif bid == "adm:addch":
            send(chat_id, "ðŸ“¢ Ù„ÛŒÙ†Ú© ÛŒØ§ Ø¢ÛŒØ¯ÛŒ Ú©Ø§Ù†Ø§Ù„ Ø±Ø§ Ø¨ÙØ±Ø³ØªÛŒØ¯ (Ù…Ø«Ù„ @mychannel).\n"
                          "Ø¨Ø¹Ø¯ ÛŒÚ© Ù¾Ø³Øª Ø§Ø² Ù‡Ù…Ø§Ù† Ú©Ø§Ù†Ø§Ù„ Ø±Ø§ Ø¨Ø±Ø§ÛŒ Ù…Ù† ÙÙˆØ±ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.\n"
                          "Ø±Ø¨Ø§Øª Ø¨Ø§ÛŒØ¯ Ø§Ø¯Ù…ÛŒÙ† Ú©Ø§Ù†Ø§Ù„ Ø¨Ø§Ø´Ø¯.")
        elif bid == "adm:stats":
            stats(chat_id)
        elif bid == "adm:channels":
            send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "Ú©Ø§Ù†Ø§Ù„ÛŒ Ø«Ø¨Øª Ù†Ø´Ø¯Ù‡.")
        return

    if bid.startswith("joined:"):
        payload = bid[7:]
        if is_member(sender):
            send_song(chat_id, payload[5:])
        else:
            send(chat_id, "Ù‡Ù†ÙˆØ² Ø¹Ø¶Ùˆ Ù†ÛŒØ³ØªÛŒØ¯ âŒ Ø§Ø¨ØªØ¯Ø§ Ø¯Ø± Ú©Ø§Ù†Ø§Ù„ Ø¹Ø¶Ùˆ Ø´ÙˆÛŒØ¯ Ùˆ Ø¯ÙˆØ¨Ø§Ø±Ù‡ Â«ØªØ£ÛŒÛŒØ¯ Ø¹Ø¶ÙˆÛŒØªÂ» Ø±Ø§ Ø¨Ø²Ù†ÛŒØ¯.")


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN ØªÙ†Ø¸ÛŒÙ… Ù†Ø´Ø¯Ù‡ Ø§Ø³Øª.")
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
                    print("BUTTON (inline):", u["inline_message"])
                    handle_button(u["inline_message"], chat_id)
                else:
                    print("UPDATE:", str(u)[:300])
            except Exception as e:
                print("handler error:", e)
        time.sleep(1)


if __name__ == "__main__":
    main()
