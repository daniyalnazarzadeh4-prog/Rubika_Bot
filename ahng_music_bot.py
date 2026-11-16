# -*- coding: utf-8 -*-
"""
AHNG MUSIC - Rubika Music Bot
Rubika Bot API v3
Python + requests + SQLite

Run:
BOT_TOKEN=xxxx python ahng_music_bot.py
"""

import os
import re
import time
import sqlite3
import logging
import requests

from urllib.parse import quote


# =====================================================
# CONFIG
# =====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

BOT_USERNAME = "ahng_music_bot"

ADMINS = {
    x.strip()
    for x in os.getenv(
        "ADMINS",
        "u0HbMCz07b206d47b6e01988bf7610cf"
    ).split(",")
    if x.strip()
}

DB_FILE = os.getenv("DB_FILE", "ahng.db")

API = f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/"

POLL_INTERVAL = 0.4

REQUEST_TIMEOUT = (5, 20)


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("AHNG_MUSIC")


# =====================================================
# HTTP SESSION
# =====================================================

session = requests.Session()

session.headers.update({
    "Content-Type": "application/json",
    "User-Agent": "AHNG-MUSIC-BOT/1.0"
})


def call(method, **data):

    try:

        response = session.post(
            API + method,
            json=data,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        result = response.json()

        if result.get("status") not in (None, "OK"):

            log.error(
                "API ERROR | %s | %s",
                method,
                result
            )

        return result

    except Exception:

        log.exception("REQUEST ERROR | %s", method)

        return {}


# =====================================================
# DATABASE
# =====================================================

db = sqlite3.connect(
    DB_FILE,
    check_same_thread=False,
    timeout=30
)

db.execute("PRAGMA journal_mode=WAL")

db.execute("PRAGMA busy_timeout=30000")

db.executescript("""

CREATE TABLE IF NOT EXISTS songs(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    artist TEXT,

    file_id TEXT,

    downloads INTEGER DEFAULT 0,

    added_at INTEGER

);

CREATE TABLE IF NOT EXISTS users(

    guid TEXT PRIMARY KEY,

    joined_at INTEGER

);

CREATE TABLE IF NOT EXISTS channels(

    guid TEXT PRIMARY KEY,

    link TEXT

);

""")

db.commit()


def db_commit():
    db.commit()


# =====================================================
# STATES
# =====================================================

admin_state = {}

pending_channel_link = {}


# =====================================================
# BUTTON SYSTEM
# ALL BUTTONS ARE LINK BUTTONS
# =====================================================

def bot_link(payload):

    return (
        f"https://rubika.ir/{BOT_USERNAME}"
        f"?start={quote(str(payload), safe='_')}"
    )


def link_button(button_id, text, url):

    return {

        "id": str(button_id),

        "type": "Link",

        "button_text": text,

        "button_link": {

            "type": "url",

            "link_url": url

        }

    }


def action_button(action, text):

    return link_button(
        action,
        text,
        bot_link(action)
    )


def channel_button(index, text, url):

    return link_button(
        f"channel_{index}",
        text,
        url
    )


def keypad(rows):

    return {

        "rows": [

            {"buttons": row}

            for row in rows

        ]

    }


def send(chat_id, text, buttons=None):

    if not chat_id:

        log.warning("SEND CANCELLED: chat_id is empty")

        return {}

    data = {

        "chat_id": chat_id,

        "text": str(text)

    }

    if buttons:

        data["inline_keypad"] = buttons

    result = call("sendMessage", **data)

    log.info(
        "SEND MESSAGE | chat=%s | status=%s",
        chat_id,
        result.get("status")
    )

    return result


# =====================================================
# CHANNELS
# =====================================================

def channels():

    return db.execute(
        "SELECT guid, link FROM channels"
    ).fetchall()


def is_member(user_guid):

    if not user_guid:

        return False

    for guid, link in channels():

        result = call(
            "getChatMember",
            chat_id=guid,
            user_id=user_guid
        )

        status = str(
            (result.get("data") or {}).get("status", "")
        ).lower()

        log.info(
            "MEMBERSHIP | user=%s | channel=%s | status=%s",
            user_guid,
            guid,
            status
        )

        if status not in (
            "member",
            "creator",
            "admin",
            "owner"
        ):

            return False

    return True


# =====================================================
# SONG LINKS
# =====================================================

def song_link(song_id):

    return bot_link(f"song_{song_id}")


def get_song(song_id):

    return db.execute(
        """
        SELECT title, artist, file_id
        FROM songs
        WHERE id=?
        """,
        (song_id,)
    ).fetchone()


# =====================================================
# SEND SONG
# =====================================================

def send_song(chat_id, song_id):

    song = get_song(song_id)

    if not song:

        return send(
            chat_id,
            "❌ آهنگ موردنظر پیدا نشد."
        )

    title, artist, file_id = song

    result = call(
        "sendFile",
        chat_id=chat_id,
        file_id=file_id,
        text=(
            f"🎵 {title}\n"
            f"🎤 {artist}\n\n"
            f"@{BOT_USERNAME}"
        )
    )

    if result.get("status") == "OK":

        db.execute(
            """
            UPDATE songs
            SET downloads = downloads + 1
            WHERE id=?
            """,
            (song_id,)
        )

        db_commit()

        log.info(
            "SONG SENT | song=%s | chat=%s",
            song_id,
            chat_id
        )

    return result


# =====================================================
# MEMBERSHIP PROMPT
# =====================================================

def join_prompt(chat_id, payload):

    rows = []

    for index, (guid, link) in enumerate(channels()):

        rows.append([

            channel_button(
                index,
                f"📢 کانال {index + 1}",
                link
            )

        ])

    rows.append([

        action_button(
            f"joined_{payload}",
            "✅ تأیید عضویت"
        )

    ])

    send(
        chat_id,
        "🔒 برای دریافت آهنگ ابتدا در کانال‌های زیر عضو شوید:",
        keypad(rows)
    )


def deliver(chat_id, user_guid, payload):

    if not payload.startswith("song_"):

        return

    song_id = payload[5:]

    if not song_id.isdigit():

        return send(chat_id, "❌ لینک آهنگ معتبر نیست.")

    if not get_song(song_id):

        return send(chat_id, "❌ آهنگ پیدا نشد.")

    if channels():

        if not is_member(user_guid):

            return join_prompt(
                chat_id,
                payload
            )

    return send_song(chat_id, song_id)


# =====================================================
# STATISTICS
# =====================================================

def stats(chat_id):

    users = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    songs, downloads = db.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(downloads), 0)
        FROM songs
        """
    ).fetchone()

    best = db.execute(
        """
        SELECT id, title, downloads
        FROM songs
        ORDER BY downloads DESC
        LIMIT 10
        """
    ).fetchall()

    text = (
        "📊 آمار AHNG MUSIC\n\n"
        f"👤 کاربران: {users}\n"
        f"🎵 آهنگ‌ها: {songs}\n"
        f"⬇️ دانلودها: {downloads}\n\n"
        "🏆 ۱۰ آهنگ پردانلود:\n\n"
    )

    if best:

        text += "\n".join(

            f"{i}. {title} | {count} دانلود"

            for i, (song_id, title, count)
            in enumerate(best, 1)

        )

    else:

        text += "هنوز آهنگی ثبت نشده است."

    return send(chat_id, text)


# =====================================================
# CHANNEL LIST
# =====================================================

def channel_list(chat_id):

    items = channels()

    if not items:

        return send(
            chat_id,
            "📭 هنوز کانالی ثبت نشده است."
        )

    text = "📋 کانال‌های ثبت‌شده:\n\n"

    text += "\n".join(

        f"{i}. {guid}\n{link}"

        for i, (guid, link) in enumerate(items, 1)

    )

    return send(chat_id, text)


# =====================================================
# ADMIN
# =====================================================

def is_admin(guid):

    return guid in ADMINS


def admin_panel(chat_id):

    rows = [

        [
            action_button(
                "adm_add",
                "➕ افزودن آهنگ"
            ),

            action_button(
                "adm_upload",
                "🚀 آپلود و انتشار"
            )
        ],

        [
            action_button(
                "adm_addch",
                "📢 ثبت کانال"
            ),

            action_button(
                "adm_stats",
                "📊 آمار"
            )
        ],

        [
            action_button(
                "adm_channels",
                "📋 کانال‌ها"
            )
        ]

    ]

    return send(
        chat_id,
        "🛠 پنل مدیریت AHNG MUSIC\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        keypad(rows)
    )


# =====================================================
# SAVE SONG
# =====================================================

def save_song(message, sender):

    file = message.get("file") or {}

    file_id = file.get("file_id")

    if not file_id:

        return None

    filename = (
        file.get("file_name")
        or "آهنگ"
    )

    filename = filename.rsplit(".", 1)[0]

    title = filename

    artist = "-"

    caption = (message.get("text") or "").strip()

    if "|" in caption:

        title, artist = [
            x.strip()
            for x in caption.split("|", 1)
        ]

    db.execute(
        """
        INSERT INTO songs
        (title, artist, file_id, downloads, added_at)
        VALUES (?, ?, ?, 0, ?)
        """,
        (
            title,
            artist,
            file_id,
            int(time.time())
        )
    )

    db_commit()

    song_id = db.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    log.info(
        "SONG SAVED | id=%s | title=%s | sender=%s",
        song_id,
        title,
        sender
    )

    return song_id, title, artist


# =====================================================
# PUBLISH SONG
# =====================================================

def post_to_channels(song_id, caption):

    song = get_song(song_id)

    if not song:

        return 0

    title, artist, file_id = song

    buttons = keypad([

        [

            link_button(
                f"song_{song_id}",
                "🎧 دریافت آهنگ",
                song_link(song_id)
            )

        ]

    ])

    success = 0

    for guid, link in channels():

        result = call(
            "sendFile",
            chat_id=guid,
            file_id=file_id,
            text=caption,
            inline_keypad=buttons
        )

        if result.get("status") == "OK":

            success += 1

        log.info(
            "PUBLISH | channel=%s | result=%s",
            guid,
            result
        )

    return success


# =====================================================
# ADMIN TEXT HANDLER
# =====================================================

def handle_admin(message, chat_id, sender, text):

    file = message.get("file")

    forwarded = message.get("forwarded_from") or {}

    state = admin_state.get(sender) or {}

    mode = state.get("mode")

    # -------------------------------------------------
    # RECEIVE SONG
    # -------------------------------------------------

    if file:

        saved = save_song(message, sender)

        if not saved:

            return send(
                chat_id,
                "❌ فایل آهنگ شناسایی نشد."
            )

        song_id, title, artist = saved

        if mode == "await_upload":

            admin_state[sender] = {

                "mode": "await_post_text",

                "sid": song_id

            }

            return send(
                chat_id,
                f"✅ آهنگ ذخیره شد:\n"
                f"{title} - {artist}\n\n"
                "✍️ حالا متن پست را ارسال کنید:"
            )

        admin_state.pop(sender, None)

        return send(
            chat_id,
            f"✅ آهنگ ذخیره شد:\n"
            f"{title} - {artist}\n\n"
            f"🔗 لینک اختصاصی:\n{song_link(song_id)}"
        )

    # -------------------------------------------------
    # ADD CHANNEL FORWARD
    # -------------------------------------------------

    if forwarded and sender in pending_channel_link:

        guid = forwarded.get("from_chat_id")

        if not guid:

            return send(
                chat_id,
                "❌ شناسه کانال از پیام فورواردشده دریافت نشد."
            )

        link = pending_channel_link.pop(sender)

        db.execute(
            """
            INSERT OR REPLACE INTO channels
            (guid, link)
            VALUES (?, ?)
            """,
            (guid, link)
        )

        db_commit()

        log.info(
            "CHANNEL SAVED | guid=%s | link=%s",
            guid,
            link
        )

        return send(
            chat_id,
            "✅ کانال ثبت شد.\n\n"
            "مطمئن شوید ربات در کانال دسترسی ادمین دارد."
        )

    # -------------------------------------------------
    # POST TEXT
    # -------------------------------------------------

    if mode == "await_post_text" and text:

        if text.startswith("/"):

            return

        admin_state[sender] = {

            "mode": "await_song_link",

            "sid": state["sid"],

            "text": text

        }

        return send(
            chat_id,
            "✅ متن پست ذخیره شد.\n\n"
            "🔗 حالا لینک اختصاصی همین آهنگ را ارسال کنید:\n\n"
            + song_link(state["sid"])
        )

    # -------------------------------------------------
    # VERIFY SONG LINK
    # -------------------------------------------------

    if mode == "await_song_link" and text:

        match = re.search(
            r"song_(\d+)",
            text
        )

        if not match or match.group(1) != str(state["sid"]):

            return send(
                chat_id,
                "❌ لینک اشتباه است.\n"
                "لینک همین آهنگ را ارسال کنید."
            )

        state["mode"] = "await_confirm"

        admin_state[sender] = state

        buttons = keypad([

            [

                action_button(
                    f"adm_post_{state['sid']}",
                    "✅ تأیید نهایی"
                ),

                action_button(
                    "adm_cancel",
                    "❌ لغو"
                )

            ]

        ])

        return send(
            chat_id,
            "📋 پیش‌نمایش پست:\n\n"
            f"{state['text']}\n\n"
            f"@{BOT_USERNAME}\n\n"
            "آیا انتشار را تأیید می‌کنید؟",
            buttons
        )

    # -------------------------------------------------
    # ADD CHANNEL
    # -------------------------------------------------

    if mode == "await_channel" and text:

        first = text.split()[0]

        if first.startswith("@"):

            link = "https://rubika.ir/" + first[1:]

        elif (
            "rubika.ir/" in first
            or "rubika.me/" in first
        ):

            link = first

        else:

            return send(
                chat_id,
                "❌ لینک یا آیدی کانال معتبر نیست."
            )

        pending_channel_link[sender] = link

        admin_state.pop(sender, None)

        return send(
            chat_id,
            "✅ لینک دریافت شد.\n\n"
            "حالا یک پست از همان کانال برای ربات فوروارد کنید.\n\n"
            "ربات باید در کانال ادمین باشد."
        )

    # -------------------------------------------------
    # COMMANDS
    # -------------------------------------------------

    if text == "/stats":

        return stats(chat_id)

    if text == "/channels":

        return channel_list(chat_id)

    if text.startswith("/delchannel "):

        guid = text.split(maxsplit=1)[1].strip()

        db.execute(
            "DELETE FROM channels WHERE guid=?",
            (guid,)
        )

        db_commit()

        return send(chat_id, "✅ کانال حذف شد.")

    if text.startswith("/del "):

        song_id = text.split(maxsplit=1)[1].strip()

        if not song_id.isdigit():

            return send(chat_id, "❌ شناسه آهنگ معتبر نیست.")

        db.execute(
            "DELETE FROM songs WHERE id=?",
            (song_id,)
        )

        db_commit()

        return send(chat_id, "✅ آهنگ حذف شد.")

    return None


# =====================================================
# BUTTON ACTIONS
# =====================================================

def handle_action(action, chat_id, sender):

    log.info(
        "BUTTON RECEIVED | action=%s | sender=%s",
        action,
        sender
    )

    # -------------------------------------------------
    # ADMIN ACTIONS
    # -------------------------------------------------

    if action.startswith("adm_"):

        if not is_admin(sender):

            log.warning(
                "UNAUTHORIZED BUTTON | sender=%s | action=%s",
                sender,
                action
            )

            return

        if action == "adm_add":

            admin_state[sender] = {
                "mode": "await_add"
            }

            return send(
                chat_id,
                "➕ آهنگ را ارسال یا فوروارد کنید.\n\n"
                "برای تعیین نام و خواننده در کپشن بنویسید:\n"
                "اسم آهنگ | خواننده"
            )

        if action == "adm_upload":

            admin_state[sender] = {
                "mode": "await_upload"
            }

            return send(
                chat_id,
                "🚀 آهنگ موردنظر را ارسال یا فوروارد کنید."
            )

        if action == "adm_stats":

            return stats(chat_id)

        if action == "adm_channels":

            return channel_list(chat_id)

        if action == "adm_addch":

            admin_state[sender] = {
                "mode": "await_channel"
            }

            return send(
                chat_id,
                "📢 لینک یا آیدی کانال را ارسال کنید.\n\n"
                "مثال:\n"
                "@mychannel"
            )

        if action == "adm_cancel":

            admin_state.pop(sender, None)

            return send(
                chat_id,
                "❌ عملیات لغو شد."
            )

        if action.startswith("adm_post_"):

            song_id = action[len("adm_post_"):]

            state = admin_state.get(sender) or {}

            if (
                state.get("mode") != "await_confirm"
                or str(state.get("sid")) != song_id
            ):

                return send(
                    chat_id,
                    "❌ درخواست منقضی شده است.\n"
                    "دوباره از پنل شروع کنید."
                )

            if not channels():

                return send(
                    chat_id,
                    "❌ هیچ کانالی ثبت نشده است."
                )

            count = post_to_channels(
                song_id,
                state.get("text", "") + f"\n\n@{BOT_USERNAME}"
            )

            admin_state.pop(sender, None)

            return send(
                chat_id,
                f"📢 نتیجه انتشار:\n\n"
                f"✅ انتشار موفق در {count} کانال."
                if count
                else
                "❌ انتشار در هیچ کانالی موفق نبود."
            )

        return

    # -------------------------------------------------
    # JOIN CONFIRMATION
    # -------------------------------------------------

    if action.startswith("joined_song_"):

        payload = action[len("joined_"):]

        song_id = payload[5:]

        if not song_id.isdigit():

            return

        if is_member(sender):

            return send_song(
                chat_id,
                song_id
            )

        return send(
            chat_id,
            "❌ هنوز عضو تمام کانال‌ها نشده‌اید.\n\n"
            "ابتدا عضو شوید و دوباره تأیید کنید."
        )


# =====================================================
# START PAYLOAD
# =====================================================

def process_start(chat_id, sender, payload):

    log.info(
        "START | sender=%s | payload=%s",
        sender,
        payload
    )

    if payload.startswith("song_"):

        return deliver(
            chat_id,
            sender,
            payload
        )

    if payload.startswith("adm_"):

        return handle_action(
            payload,
            chat_id,
            sender
        )

    if payload.startswith("joined_song_"):

        return handle_action(
            payload,
            chat_id,
            sender
        )

    if payload == "":

        if is_admin(sender):

            return admin_panel(chat_id)

        return send(
            chat_id,
            "سلام 👋 به AHNG MUSIC خوش آمدید.\n\n"
            "🎵 برای دریافت آهنگ از لینک اختصاصی آهنگ‌ها استفاده کنید."
        )


# =====================================================
# MESSAGE HANDLER
# =====================================================

def handle_message(message, chat_id):

    if not isinstance(message, dict):

        return

    sender = message.get("sender_id", chat_id)

    text = (
        message.get("text") or ""
    ).strip()

    if not sender:

        return

    # SAVE USER

    db.execute(
        """
        INSERT OR IGNORE INTO users
        (guid, joined_at)
        VALUES (?, ?)
        """,
        (sender, int(time.time()))
    )

    db_commit()

    log.info(
        "MESSAGE | sender=%s | text=%s",
        sender,
        text[:200]
    )

    # MY ID - AVAILABLE TO EVERYONE

    if text == "/myid":

        return send(
            chat_id,
            f"🆔 شناسه شما:\n{sender}"
        )

    # ADMIN MESSAGES

    if is_admin(sender):

        result = handle_admin(
            message,
            chat_id,
            sender,
            text
        )

        if result is not None:

            return result

    # START

    if text.startswith("/start"):

        parts = text.split(maxsplit=1)

        payload = (
            parts[1].strip()
            if len(parts) > 1
            else ""
        )

        return process_start(
            chat_id,
            sender,
            payload
        )

    # ADMIN PANEL

    if text == "/panel":

        if is_admin(sender):

            return admin_panel(chat_id)

        return

    # ADMIN COMMANDS

    if is_admin(sender):

        if text.startswith(("/stats", "/channels", "/del ", "/delchannel ")):

            return handle_admin(
                message,
                chat_id,
                sender,
                text
            )


# =====================================================
# UPDATE PROCESSOR
# =====================================================

def process_update(update):

    if not isinstance(update, dict):

        return

    update_type = update.get("type")

    chat_id = update.get("chat_id")

    if update_type == "RemovedMessage":

        return

    if update_type == "NewMessage":

        message = update.get("new_message") or {}

        try:

            handle_message(
                message,
                chat_id
            )

        except Exception:

            log.exception(
                "MESSAGE HANDLER ERROR"
            )

        return

    # Other update types

    if update.get("inline_message"):

        log.info(
            "INLINE UPDATE RECEIVED: %s",
            update["inline_message"]
        )

        inline = update["inline_message"]

        sender = inline.get("sender_id")

        if sender and inline.get("aux_data"):

            action = (
                inline["aux_data"].get("button_id")
            )

            if action:

                handle_action(
                    action,
                    inline.get("chat_id") or chat_id,
                    sender
                )

        return

    log.info(
        "OTHER UPDATE: %s",
        update
    )


# =====================================================
# MAIN POLLING
# =====================================================

def main():

    if not BOT_TOKEN:

        raise SystemExit(
            "BOT_TOKEN تنظیم نشده است."
        )

    offset = None

    log.info(
        "AHNG MUSIC STARTED | BOT=%s",
        BOT_USERNAME
    )

    log.info(
        "ADMINS=%s",
        len(ADMINS)
    )

    while True:

        try:

            params = {
                "limit": 100
            }

            if offset:

                params["offset_id"] = offset

            result = call(
                "getUpdates",
                **params
            )

            if not result:

                time.sleep(2)

                continue

            if result.get("status") not in (None, "OK"):

                log.error(
                    "POLLING ERROR: %s",
                    result
                )

                time.sleep(3)

                continue

            data = result.get("data") or {}

            updates = data.get("updates") or []

            log.info(
                "UPDATES RECEIVED: %s",
                len(updates)
            )

            for update in updates:

                try:

                    process_update(update)

                except Exception:

                    log.exception(
                        "UPDATE PROCESSING ERROR"
                    )

            next_offset = data.get("next_offset_id")

            if next_offset:

                offset = next_offset

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:

            log.info("BOT STOPPED")

            break

        except Exception:

            log.exception(
                "MAIN LOOP ERROR"
            )

            time.sleep(3)


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    main()
