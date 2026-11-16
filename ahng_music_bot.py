# -*- coding: utf-8 -*-
"""
AHNG MUSIC - \u0631\u0628\u0627\u062a \u0645\u0648\u0633\u06cc\u0642\u06cc \u0631\u0648\u0628\u06cc\u06a9\u0627
\u0627\u062c\u0631\u0627: BOT_TOKEN=xxxx python ahng_music_bot.py
"""
import os
import re
import json
from collections import deque
import time
import sqlite3
import requests

# ============ \u062a\u0646\u0638\u06cc\u0645\u0627\u062a ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMINS = {"u0HbMCz07b206d47b6e01988bf7610cf"}      # guid \u0645\u062f\u06cc\u0631\u0647\u0627 (\u0628\u0627 /myid \u0645\u06cc\u200c\u06af\u06cc\u0631\u06cc\u062f)
BOT_USERNAME = "ahng_music_bot"      # \u0622\u06cc\u062f\u06cc \u0631\u0628\u0627\u062a \u0628\u062f\u0648\u0646 @
DB_FILE = os.getenv("DB_FILE", "ahng.db")
API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"

# ============ \u062f\u06cc\u062a\u0627\u0628\u06cc\u0633 ============
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


# ============ \u06a9\u0627\u0646\u0627\u0644\u200c\u0647\u0627 \u0648 \u0639\u0636\u0648\u06cc\u062a ============
def channels():
    return db.execute("SELECT guid, link FROM channels").fetchall()


def is_member(user_guid):
    """\u0647\u0631 \u0628\u0627\u0631 \u0627\u0632 \u0631\u0648\u0628\u06cc\u06a9\u0627 \u067e\u0631\u0633\u06cc\u062f\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f (\u0630\u062e\u06cc\u0631\u0647 \u0646\u0645\u06cc\u200c\u0634\u0648\u062f)\u060c \u067e\u0633 \u062e\u0631\u0648\u062c \u0627\u0632 \u06a9\u0627\u0646\u0627\u0644 \u0647\u0645 \u062f\u06cc\u062f\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f."""
    for guid, _ in channels():
        res = call("getChatMember", chat_id=guid, user_id=user_guid)
        status = str((res.get("data") or {}).get("status", "")).lower()
        if status not in ("member", "creator", "admin", "owner"):
            return False
    return True


def join_prompt(chat_id, payload):
    rows = [[link_btn(f"ch{i}", f"\U0001f4e2 \u06a9\u0627\u0646\u0627\u0644 {i + 1}", link)] for i, (_, link) in enumerate(channels())]
    rows.append([simple_btn(f"joined:{payload}", "\u2705 \u062a\u0623\u06cc\u06cc\u062f \u0639\u0636\u0648\u06cc\u062a")])
    send(chat_id, "\u0628\u0631\u0627\u06cc \u062f\u0631\u06cc\u0627\u0641\u062a \u0622\u0647\u0646\u06af \u0627\u0628\u062a\u062f\u0627 \u062f\u0631 \u06a9\u0627\u0646\u0627\u0644(\u0647\u0627\u06cc) \u0632\u06cc\u0631 \u0639\u0636\u0648 \u0634\u0648\u06cc\u062f\u060c \u0633\u067e\u0633 \xab\u062a\u0623\u06cc\u06cc\u062f \u0639\u0636\u0648\u06cc\u062a\xbb \u0631\u0627 \u0628\u0632\u0646\u06cc\u062f.",
         keypad(rows))


# ============ \u0622\u0647\u0646\u06af\u200c\u0647\u0627 ============
def song_link(sid):
    return f"https://rubika.ir/{BOT_USERNAME}?start=song_{sid}"


def send_song(chat_id, song_id):
    row = db.execute("SELECT title, artist, file_id FROM songs WHERE id=?", (song_id,)).fetchone()
    if not row:
        return send(chat_id, "\u0622\u0647\u0646\u06af \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f.")
    title, artist, file_id = row
    call("sendFile", chat_id=chat_id, file_id=file_id,
         text=f"\U0001f3b5 {title}\n\U0001f3a4 {artist}\n\n@{BOT_USERNAME}")
    db.execute("UPDATE songs SET downloads=downloads+1 WHERE id=?", (song_id,))
    db.commit()


def deliver(chat_id, user_guid, payload):
    """\u062f\u0631\u06cc\u0627\u0641\u062a \u0622\u0647\u0646\u06af: \u0627\u06af\u0631 \u0639\u0636\u0648 \u0646\u0628\u0627\u0634\u062f \u0639\u0636\u0648\u06cc\u062a \u0627\u062c\u0628\u0627\u0631\u06cc\u060c \u0648\u06af\u0631\u0646\u0647 \u0627\u0631\u0633\u0627\u0644."""
    if not payload.startswith("song_"):
        return
    if channels() and not is_member(user_guid):
        return join_prompt(chat_id, payload)
    send_song(chat_id, payload[5:])


def stats(chat_id):
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    songs, dl = db.execute("SELECT COUNT(*), COALESCE(SUM(downloads),0) FROM songs").fetchone()
    best = db.execute("SELECT id, title, downloads FROM songs ORDER BY downloads DESC LIMIT 10").fetchall()
    txt = f"\U0001f4ca \u0622\u0645\u0627\u0631 AHNG MUSIC\n\U0001f464 \u06a9\u0627\u0631\u0628\u0631\u0627\u0646: {users}\n\U0001f3b5 \u0622\u0647\u0646\u06af\u200c\u0647\u0627: {songs}\n\u2b07\ufe0f \u062f\u0627\u0646\u0644\u0648\u062f\u0647\u0627: {dl}\n\n"
    txt += "\n".join(f"{i}. {t} \u2190 {d}" for i, t, d in best)
    send(chat_id, txt)


# ============ \u067e\u0646\u0644 \u0645\u062f\u06cc\u0631 ============
def is_admin(guid):
    return guid in ADMINS


def admin_panel(chat_id):
    rows = [
        [simple_btn("adm:add", "\u2795 \u0627\u0641\u0632\u0648\u062f\u0646 \u0622\u0647\u0646\u06af"), simple_btn("adm:upload", "\U0001f680 \u0622\u067e\u0644\u0648\u062f \u0648 \u0627\u0646\u062a\u0634\u0627\u0631")],
        [simple_btn("adm:addch", "\U0001f4e2 \u062b\u0628\u062a \u06a9\u0627\u0646\u0627\u0644"), simple_btn("adm:stats", "\U0001f4ca \u0622\u0645\u0627\u0631")],
        [simple_btn("adm:channels", "\U0001f4cb \u06a9\u0627\u0646\u0627\u0644\u200c\u0647\u0627")],
    ]
    send(chat_id, "\U0001f6e0 \u067e\u0646\u0644 \u0645\u062f\u06cc\u0631\u06cc\u062a AHNG MUSIC\n\u06cc\u06a9\u06cc \u0627\u0632 \u06af\u0632\u06cc\u0646\u0647\u200c\u0647\u0627 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:", keypad(rows))


def post_to_channels(sid, caption):
    """\u0627\u0646\u062a\u0634\u0627\u0631 \u0622\u0647\u0646\u06af \u062f\u0631 \u06a9\u0627\u0646\u0627\u0644\u200c\u0647\u0627\u06cc \u062b\u0628\u062a\u200c\u0634\u062f\u0647 \u0628\u0627 \u062f\u06a9\u0645\u0647\u200c\u06cc \u0634\u06cc\u0634\u0647\u200c\u0627\u06cc \u062f\u0631\u06cc\u0627\u0641\u062a."""
    row = db.execute("SELECT file_id FROM songs WHERE id=?", (sid,)).fetchone()
    if not row:
        return 0
    kp = keypad([[link_btn("dl", "\U0001f3a7 \u062f\u0631\u06cc\u0627\u0641\u062a \u0622\u0647\u0646\u06af", song_link(sid))]])
    ok = 0
    for guid, _ in channels():
        res = call("sendFile", chat_id=guid, file_id=row[0], text=caption, inline_keypad=kp)
        if res and res.get("status", "OK") == "OK":
            ok += 1
    return ok


# ============ \u067e\u06cc\u0627\u0645\u200c\u0647\u0627 ============
admin_state = {}            # admin guid -> \u0645\u0631\u062d\u0644\u0647\u200c\u06cc \u0641\u0639\u0644\u06cc (\u0627\u0641\u0632\u0648\u062f\u0646/\u0622\u067e\u0644\u0648\u062f)
pending_channel_link = {}   # admin guid -> \u0644\u06cc\u0646\u06a9 \u06a9\u0627\u0646\u0627\u0644\u06cc \u06a9\u0647 \u0645\u0646\u062a\u0638\u0631 \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u067e\u0633\u062a \u0627\u0633\u062a


def handle_admin(m, chat_id, sender, text):
    f = m.get("file")
    fwd = m.get("forwarded_from") or {}

    # \u06f1) \u0641\u0631\u0633\u062a\u0627\u062f\u0646 \u0622\u0647\u0646\u06af -> \u0630\u062e\u06cc\u0631\u0647 + \u0633\u0627\u062e\u062a \u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc
    if f:
        name = (f.get("file_name") or "\u0622\u0647\u0646\u06af").rsplit(".", 1)[0]
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
            return send(chat_id, f"\u2705 \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f: {title} - {artist}\n\u0628\u0631\u0627\u06cc \u0627\u062f\u0627\u0645\u0647 \u062f\u06a9\u0645\u0647\u200c\u06cc \u0632\u06cc\u0631 \u0631\u0627 \u0628\u0632\u0646\u06cc\u062f:",
                        keypad([[simple_btn(f"adm:text:{sid}", "\u270d\ufe0f \u0646\u0648\u0634\u062a\u0646 \u0645\u062a\u0646 \u067e\u0633\u062a")]]))
        admin_state.pop(sender, None)
        send(chat_id, f"\u2705 \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f: {title} - {artist}\n\u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc (\u06a9\u067e\u06cc \u06a9\u0646\u06cc\u062f \u0648 \u062f\u0631 \u062f\u06a9\u0645\u0647\u200c\u06cc \u0634\u06cc\u0634\u0647\u200c\u0627\u06cc \u067e\u0633\u062a \u06a9\u0627\u0646\u0627\u0644 \u0628\u06af\u0630\u0627\u0631\u06cc\u062f):")
        return send(chat_id, song_link(sid))

    # \u0645\u0631\u0627\u062d\u0644 \u0622\u067e\u0644\u0648\u062f: \u0645\u062a\u0646 \u067e\u0633\u062a -> \u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc -> \u062a\u0623\u06cc\u06cc\u062f \u0646\u0647\u0627\u06cc\u06cc
    st = admin_state.get(sender) or {}
    mode = st.get("mode")
    if mode in ("await_text", "await_link") and text and not text.startswith("/"):
        sid = st["sid"]
        if mode == "await_text":
            st["text"] = text
            st["mode"] = "await_link"
            return send(chat_id, "\u2705 \u0645\u062a\u0646 \u062b\u0628\u062a \u0634\u062f.\n\u062d\u0627\u0644\u0627 \u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc \u0622\u0647\u0646\u06af \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f:\n" + song_link(sid))
        mm = re.search(r"song_(\d+)", text)
        if not mm or mm.group(1) != str(sid):
            return send(chat_id, "\u0644\u06cc\u0646\u06a9 \u062f\u0631\u0633\u062a \u0646\u06cc\u0633\u062a. \u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc \u0647\u0645\u06cc\u0646 \u0622\u0647\u0646\u06af \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f:\n" + song_link(sid))
        st["mode"] = "await_confirm"
        return send(chat_id, f"\u067e\u06cc\u0634\u200c\u0646\u0645\u0627\u06cc\u0634 \u067e\u0633\u062a:\n\n{st['text']}\n\n@{BOT_USERNAME}\n\n\u062a\u0623\u06cc\u06cc\u062f \u0645\u06cc\u200c\u06a9\u0646\u06cc\u062f \u062f\u0631 \u06a9\u0627\u0646\u0627\u0644 \u0645\u0646\u062a\u0634\u0631 \u0634\u0648\u062f\u061f",
                    keypad([[simple_btn(f"adm:post:{sid}", "\u2705 \u062a\u0623\u06cc\u06cc\u062f \u0646\u0647\u0627\u06cc\u06cc"), simple_btn("adm:cancel", "\u274c \u0644\u063a\u0648")]]))

    # \u06f2) \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u067e\u0633\u062a \u06a9\u0627\u0646\u0627\u0644 -> \u062b\u0628\u062a guid \u06a9\u0627\u0646\u0627\u0644
    if fwd and pending_channel_link.get(sender):
        guid = fwd.get("from_chat_id")
        if guid:
            db.execute("INSERT OR REPLACE INTO channels VALUES(?,?)", (guid, pending_channel_link.pop(sender)))
            db.commit()
            return send(chat_id, "\u2705 \u06a9\u0627\u0646\u0627\u0644 \u062b\u0628\u062a \u0634\u062f. \u06cc\u0627\u062f\u062a\u0627\u0646 \u0628\u0627\u0634\u062f \u0631\u0628\u0627\u062a \u062f\u0631 \u06a9\u0627\u0646\u0627\u0644 \u0627\u062f\u0645\u06cc\u0646 \u0628\u0627\u0634\u062f.")

    # \u06f3) \u0644\u06cc\u0646\u06a9 \u06a9\u0627\u0646\u0627\u0644 -> \u062a\u0644\u0627\u0634 \u0628\u0631\u0627\u06cc \u0639\u0636\u0648 \u0634\u062f\u0646 + \u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0641\u0648\u0631\u0648\u0627\u0631\u062f
    first = text.split()[0] if text else ""
    is_username = first.startswith("@") and len(first) > 2 and first[1:].lower() != BOT_USERNAME.lower()
    is_link = ("rubika.ir/" in first or "rubika.me/" in first) and BOT_USERNAME.lower() not in first.lower()
    if is_username or is_link:
        if True:
            link = "https://rubika.ir/" + first[1:] if is_username else first
            pending_channel_link[sender] = link
            call("joinChannelByLink", link=link)   # \u0645\u0645\u06a9\u0646 \u0627\u0633\u062a \u062f\u0631 Bot API \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc \u0646\u0634\u0648\u062f
            return send(chat_id, "\u0644\u06cc\u0646\u06a9 \u062b\u0628\u062a \u0634\u062f. \u062d\u0627\u0644\u0627 \u06cc\u06a9 \u067e\u0633\u062a \u0627\u0632 \u0647\u0645\u0627\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0628\u0631\u0627\u06cc \u0645\u0646 \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f \u062a\u0627 \u0634\u0646\u0627\u0633\u0647\u200c\u06cc \u06a9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0628\u06af\u06cc\u0631\u0645.\n"
                                 "(\u0627\u06af\u0631 \u0631\u0628\u0627\u062a \u062e\u0648\u062f\u0634 \u0639\u0636\u0648 \u0646\u0634\u062f\u060c \u0622\u0646 \u0631\u0627 \u0627\u062f\u0645\u06cc\u0646 \u06a9\u0627\u0646\u0627\u0644 \u06a9\u0646\u06cc\u062f.)")

    if text == "/stats":
        return stats(chat_id)
    if text == "/channels":
        return send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "\u06a9\u0627\u0646\u0627\u0644\u06cc \u062b\u0628\u062a \u0646\u0634\u062f\u0647.")
    if text.startswith("/delchannel "):
        db.execute("DELETE FROM channels WHERE guid=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "\u062d\u0630\u0641 \u0634\u062f.")
    if text.startswith("/del "):
        db.execute("DELETE FROM songs WHERE id=?", (text.split()[1],))
        db.commit()
        return send(chat_id, "\u0622\u0647\u0646\u06af \u062d\u0630\u0641 \u0634\u062f.")
    return None


def handle_message(m, chat_id):
    sender = m.get("sender_id", chat_id)
    text = (m.get("text") or "").strip()
    db.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (sender, int(time.time())))
    db.commit()

    # \u0641\u0634\u0631\u062f\u0646 \u062f\u06a9\u0645\u0647\u200c\u06cc \u0634\u06cc\u0634\u0647\u200c\u0627\u06cc \u0645\u0645\u06a9\u0646 \u0627\u0633\u062a \u0628\u0647 \u0634\u06a9\u0644 \u067e\u06cc\u0627\u0645 \u0639\u0627\u062f\u06cc \u0628\u0627 aux_data.button_id \u0628\u0631\u0633\u062f
    aux = m.get("aux_data") or {}
    if aux.get("button_id"):
        print("BUTTON (message):", aux.get("button_id"), "from", sender)
        return handle_button({"aux_data": aux, "sender_id": sender}, chat_id)

    if text == "/myid":
        return send(chat_id, f"guid \u0634\u0645\u0627:\n{sender}")

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
        return send(chat_id, "\u0633\u0644\u0627\u0645 \U0001f44b \u0628\u0647 AHNG MUSIC \u062e\u0648\u0634 \u0622\u0645\u062f\u06cc\u062f.\n\u0628\u0631\u0627\u06cc \u062f\u0631\u06cc\u0627\u0641\u062a \u0622\u0647\u0646\u06af \u0627\u0632 \u062f\u06a9\u0645\u0647\u200c\u06cc \u062f\u0627\u0646\u0644\u0648\u062f \u0632\u06cc\u0631 \u067e\u0633\u062a\u200c\u0647\u0627\u06cc \u06a9\u0627\u0646\u0627\u0644 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u06a9\u0646\u06cc\u062f.")


def handle_button(inline, chat_id):
    bid = (inline.get("aux_data") or {}).get("button_id") or inline.get("button_id") or ""
    sender = inline.get("sender_id", chat_id)

    # \u062f\u06a9\u0645\u0647\u200c\u0647\u0627\u06cc \u067e\u0646\u0644 \u0645\u062f\u06cc\u0631: \u0641\u0642\u0637 \u0628\u0631\u0627\u06cc \u0627\u062f\u0645\u06cc\u0646\u200c\u0647\u0627
    if bid.startswith("adm:"):
        if not is_admin(sender):
            return
        if bid == "adm:add":
            admin_state[sender] = {"mode": "await_song_add"}
            send(chat_id, "\u2795 \u0622\u0647\u0646\u06af \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f \u06cc\u0627 \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f.\n"
                          "(\u062f\u0631 \u06a9\u067e\u0634\u0646 \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f: \u0627\u0633\u0645 \u0622\u0647\u0646\u06af | \u062e\u0648\u0627\u0646\u0646\u062f\u0647)\n"
                          "\u0628\u0639\u062f \u0627\u0632 \u0630\u062e\u06cc\u0631\u0647\u060c \u0644\u06cc\u0646\u06a9 \u0627\u062e\u062a\u0635\u0627\u0635\u06cc \u0622\u0647\u0646\u06af \u0631\u0627 \u0645\u06cc\u200c\u06af\u06cc\u0631\u06cc\u062f.")
        elif bid == "adm:upload":
            admin_state[sender] = {"mode": "await_song_upload"}
            send(chat_id, "\U0001f680 \u0622\u0647\u0646\u06af \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f \u06cc\u0627 \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f.\n"
                          "(\u062f\u0631 \u06a9\u067e\u0634\u0646 \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f: \u0627\u0633\u0645 \u0622\u0647\u0646\u06af | \u062e\u0648\u0627\u0646\u0646\u062f\u0647)")
        elif bid.startswith("adm:text:"):
            admin_state[sender] = {"mode": "await_text", "sid": bid[9:]}
            send(chat_id, "\u270d\ufe0f \u0645\u062a\u0646 \u067e\u0633\u062a \u0631\u0627 \u0628\u0646\u0648\u06cc\u0633\u06cc\u062f \u0648 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f:")
        elif bid.startswith("adm:post:"):
            st = admin_state.get(sender) or {}
            sid = bid[9:]
            if st.get("mode") != "await_confirm" or str(st.get("sid")) != sid:
                send(chat_id, "\u0627\u06cc\u0646 \u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0645\u0646\u0642\u0636\u06cc \u0634\u062f\u0647. \u062f\u0648\u0628\u0627\u0631\u0647 \u0627\u0632 \u067e\u0646\u0644 \u0634\u0631\u0648\u0639 \u06a9\u0646\u06cc\u062f: /panel")
            elif not channels():
                send(chat_id, "\u06a9\u0627\u0646\u0627\u0644\u06cc \u062b\u0628\u062a \u0646\u0634\u062f\u0647. \u0627\u0648\u0644 \xab\U0001f4e2 \u062b\u0628\u062a \u06a9\u0627\u0646\u0627\u0644\xbb \u0631\u0627 \u0628\u0632\u0646\u06cc\u062f.")
            else:
                n = post_to_channels(sid, f"{st.get('text', '')}\n\n@{BOT_USERNAME}")
                admin_state.pop(sender, None)
                send(chat_id, f"\u2705 \u0645\u0646\u062a\u0634\u0631 \u0634\u062f \u062f\u0631 {n} \u06a9\u0627\u0646\u0627\u0644." if n else "\u274c \u0627\u0631\u0633\u0627\u0644 \u0628\u0647 \u06a9\u0627\u0646\u0627\u0644 \u0627\u0646\u062c\u0627\u0645 \u0646\u0634\u062f. \u0631\u0628\u0627\u062a \u0628\u0627\u06cc\u062f \u0627\u062f\u0645\u06cc\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0628\u0627\u0634\u062f.")
        elif bid == "adm:cancel":
            admin_state.pop(sender, None)
            send(chat_id, "\u0644\u063a\u0648 \u0634\u062f. \u0628\u0631\u0627\u06cc \u067e\u0646\u0644: /panel")
        elif bid == "adm:addch":
            send(chat_id, "\U0001f4e2 \u0644\u06cc\u0646\u06a9 \u06cc\u0627 \u0622\u06cc\u062f\u06cc \u06a9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0628\u0641\u0631\u0633\u062a\u06cc\u062f (\u0645\u062b\u0644 @mychannel).\n"
                          "\u0628\u0639\u062f \u06cc\u06a9 \u067e\u0633\u062a \u0627\u0632 \u0647\u0645\u0627\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0631\u0627 \u0628\u0631\u0627\u06cc \u0645\u0646 \u0641\u0648\u0631\u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f.\n"
                          "\u0631\u0628\u0627\u062a \u0628\u0627\u06cc\u062f \u0627\u062f\u0645\u06cc\u0646 \u06a9\u0627\u0646\u0627\u0644 \u0628\u0627\u0634\u062f.")
        elif bid == "adm:stats":
            stats(chat_id)
        elif bid == "adm:channels":
            send(chat_id, "\n".join(f"{g} | {l}" for g, l in channels()) or "\u06a9\u0627\u0646\u0627\u0644\u06cc \u062b\u0628\u062a \u0646\u0634\u062f\u0647.")
        return

    if bid.startswith("joined:"):
        payload = bid[7:]
        if is_member(sender):
            send_song(chat_id, payload[5:])
        else:
            send(chat_id, "\u0647\u0646\u0648\u0632 \u0639\u0636\u0648 \u0646\u06cc\u0633\u062a\u06cc\u062f \u274c \u0627\u0628\u062a\u062f\u0627 \u062f\u0631 \u06a9\u0627\u0646\u0627\u0644 \u0639\u0636\u0648 \u0634\u0648\u06cc\u062f \u0648 \u062f\u0648\u0628\u0627\u0631\u0647 \xab\u062a\u0623\u06cc\u06cc\u062f \u0639\u0636\u0648\u06cc\u062a\xbb \u0631\u0627 \u0628\u0632\u0646\u06cc\u062f.")



def process_update(u):
    chat_id = u.get("chat_id")
    if u.get("type") == "NewMessage":
        handle_message(u["new_message"], chat_id)
    elif u.get("inline_message"):
        im = u["inline_message"]
        print("BUTTON (inline):", im)
        handle_button(im, im.get("chat_id") or chat_id)
    else:
        print("UPDATE:", str(u)[:300])


def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN تنظیم نشده است.")
    offset = None
    seen, order = set(), deque()
    first = True
    print("AHNG MUSIC bot started...")
    while True:
        batch = []
        # ۱) با offset (برای پیام‌های عادی)
        d = {"limit": 50}
        if offset:
            d["offset_id"] = offset
        data = call("getUpdates", **d).get("data") or {}
        if data.get("next_offset_id"):
            offset = data["next_offset_id"]
        batch += data.get("updates", [])
        # ۲) بدون offset (روبیکا کلیک دکمه‌ی شیشه‌ای را با offset نمی‌دهد)
        data2 = call("getUpdates", limit=50).get("data") or {}
        batch += data2.get("updates", [])

        for u in batch:
            key = json.dumps(u, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            order.append(key)
            if len(order) > 3000:
                seen.discard(order.popleft())
            if first:
                continue      # آپدیت‌های قدیمیِ قبل از روشن شدن را رد کن
            try:
                process_update(u)
            except Exception as e:
                print("handler error:", e)
        first = False
        time.sleep(1)


if __name__ == "__main__":
    main()
