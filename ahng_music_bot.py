# -*- coding: utf-8 -*-
"""
DeniUp (دنی‌آپ) - ربات مدیریت گروه روبیکا
کتابخانه: rubpy   ->   pip install rubpy
اجرا:     python deniup_bot.py
بار اول از شما شماره بات (+989306720427) و کد تایید را می‌خواهد.
"""
import re
import json
import time
import asyncio
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, deque

from rubpy import Client, filters
from rubpy.types import Update

# ============================ تنظیمات ============================
SESSION_NAME = "deniup"
BOT_NAME = "دنی‌آپ"
BOT_ACCOUNT_PHONE = "+989306720427"
ADMIN_PHONE = "09921122540"          # فقط برای اطلاع؛ شناسایی ادمین با GUID است
ADMIN_GUIDS = set()                  # GUID ادمین را اینجا بگذار (دستور /myguid در پیوی بات)

SPAM_LIMIT = 5        # بیش از این تعداد پیام ...
SPAM_WINDOW = 6       # ... در این تعداد ثانیه = اسپم
SPAM_MAX_WARNS = 3    # بعد از این تعداد اخطار، کاربر از گروه حذف می‌شود
STATS_FILE = "deniup_stats.json"
PROMO_FILE = "deniup_promo.json"
WARNS_FILE = "deniup_warns.json"     # اخطارهای مالک گروه (ماندگار)
OWNER_MAX_WARNS = 3                  # بعد از این تعداد اخطار مالک، عضو از گروه حذف می‌شود
BAN_WORDS = ("بن", "/ban", "ban")
WARN_WORDS = ("اخطار", "/warn", "warn")
UNWARN_WORDS = ("حذف اخطار", "/unwarn")
PROMOTE_WORDS = ("ارتقا", "ارتقاع", "ارتقاء", "ادمین", "/promote")
DEMOTE_WORDS = ("عزل", "عزل ادمین", "/demote")
MUTE_WORDS = ("سکوت", "/mute")
UNMUTE_WORDS = ("رفع سکوت", "/unmute")
MUTE_HOURS = 24                      # مدت سکوت
MUTE_FILE = "deniup_mutes.json"
# دسترسی‌هایی که ادمین جدید می‌گیرد (SetAdmin عمداً نیست تا ادمین‌ها نتوانند ادمین بسازند)
ADMIN_ACCESS = ["PinMessages", "DeleteGlobalAllMessages", "BanMember", "SetJoinLink", "ChangeInfo", "ViewMembers", "ViewAdmins"]
TZ = ZoneInfo("Asia/Tehran")     # ساعت شلوغی بر اساس وقت ایران
PROMO_CHANNEL = "@AhngOfficial"
PROMO_MIN_DATA = 30              # حداقل پیام ثبت‌شده تا ساعت شلوغی گروه محاسبه شود
PROMO_DEFAULT_HOUR = 21          # ساعت پیش‌فرض تا وقتی داده کافی نیست
PROMO_ACTIVE_MSGS = 3            # حداقل پیام در ۱۰ دقیقه اخیر تا گروه «شلوغ» حساب شود
ACCEPT_WORDS = ("قبول دارم", "قبول", "/accept")
CHECK_WORDS = ("عضو شدم", "عضو شدم ✅", "✅ عضو شدم", "/check", "بررسی")
MEMBER_CACHE_SEC = 600           # نتیجه عضویت تاییدشده تا این مدت کش می‌شود
FORCE_JOIN_TEXT = (
    "📢 عضویت اجباری\n\n"
    "برای استفاده از ربات، اول باید در کانال ما عضو بشی 👇\n"
    "👉 " + PROMO_CHANNEL + "\n\n"
    "بعد از عضویت، بنویس: «عضو شدم» ✅"
)

PROMO_MESSAGES = [
    "🎵✨ عاشق آهنگ‌های خاص و دلنشینی؟\nبهترین‌ها رو تو کانال ما پیدا کن 👇\n📢 {ch}",
    "🌹 یه استراحت کوتاه، یه آهنگ قشنگ! 🎧\nهر روز تازه‌ترین آهنگ‌ها فقط تو 👈 {ch}",
    "💎 اگه آهنگ خوب دوست داری، جات اینجاست!\nعضو شو و هر روز لذت ببر 🎶\n📲 {ch}",
    "🔥 داغ‌ترین و جدیدترین آهنگ‌ها منتظرته!\nهمین الان بپیوند 👇\n📢 {ch}",
    "🎶 حال و هوات رو عوض کن با آهنگ‌های ناب 💫\nکانال رسمی ما: {ch}",
]

RULES_TEXT = (
    "📜 قوانین مهم — لطفاً حتماً بخوانید ⚠️\n\n"
    "1️⃣ ربات برای مدیریت گروه شما (حذف لینک، آیدی و اسپم) فعالیت می‌کند.\n"
    "2️⃣ ربات روزانه در ساعات شلوغ گروه، یک پیام تبلیغ کانال " + PROMO_CHANNEL + " ارسال می‌کند.\n"
    "3️⃣ اگر نمی‌خواهید تبلیغ در گروه شما ارسال شود، باید ماهانه "
    "۵۰ هزار تومان پرداخت کنید.\n"
    "4️⃣ برای پرداخت و فعال‌سازی، به ادمین ربات پیام بدهید: " + ADMIN_PHONE + "\n\n"
    "✅ اگر با قوانین موافقید بنویسید: «قبول دارم» تا ربات عضو گروه شما شود."
)
# ================================================================

LINK_RE = re.compile(
    r"(https?://|www\.|t\.me/|rubika\.ir/|rubika\.me/|telegram\.me/|"
    r"instagram\.com/|wa\.me/|chat\.whatsapp\.com|\b[\w-]+\.(com|ir|me|org|net|info|xyz|link)\b)",
    re.IGNORECASE,
)
ID_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_]{3,}")
JOIN_LINK_RE = re.compile(r"rubika\.ir/(join[gc])/([A-Za-z0-9]+)", re.IGNORECASE)

GREETINGS = {
    "سلام": ["سلام عزیزم 🌹", "سلام، خوش اومدی 👋", "سلام! در خدمتم ✨"],
    "خوبی": ["مرسی عزیزم، تو خوبی؟ 😊", "عالیم! شما چطوری؟ 🌟"],
    "چطوری": ["عالیم، ممنون که پرسیدی 🌹", "خوبم خوبم، تو چطوری؟ 😍"],
}

bot = Client(name=SESSION_NAME)

# ---------- داده‌ها ----------
try:
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        STATS = json.load(f)
except Exception:
    STATS = {}

_last_save = 0.0


def save_stats(force=False):
    global _last_save
    if force or time.time() - _last_save > 20:
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(STATS, f, ensure_ascii=False)
            _last_save = time.time()
        except Exception:
            pass


msg_times = defaultdict(lambda: deque(maxlen=SPAM_LIMIT + 2))
warns = defaultdict(int)
owner_cache = {}   # group_guid -> (set(admin_guids), owner_guid, time)
BOT_GUID = None
PENDING = {}                       # author_guid -> لینکی که منتظر قبول قوانین است
recent_msgs = defaultdict(lambda: deque(maxlen=50))
_promo_task = None

try:
    with open(PROMO_FILE, "r", encoding="utf-8") as f:
        PROMO = json.load(f)
except Exception:
    PROMO = {}
PROMO.setdefault("exempt", [])     # گروه‌هایی که ماهانه پرداخت کرده‌اند
PROMO.setdefault("last_sent", {})  # gid -> تاریخ آخرین تبلیغ


def save_promo():
    try:
        with open(PROMO_FILE, "w", encoding="utf-8") as f:
            json.dump(PROMO, f, ensure_ascii=False)
    except Exception:
        pass


def peak_hours(g):
    """۳ ساعت شلوغ گروه (اگر داده کافی نباشد، ساعت پیش‌فرض)"""
    hours = g.get("hours", {})
    if g.get("total", 0) < PROMO_MIN_DATA or not hours:
        return {PROMO_DEFAULT_HOUR}
    top = sorted(hours, key=lambda h: -hours[h])[:3]
    return {int(h) for h in top}


async def promo_loop():
    """هر ۵ دقیقه چک می‌کند؛ روزی حداکثر یک تبلیغ، در ساعت شلوغ هر گروه"""
    while True:
        try:
            now = datetime.now(TZ)
            today = now.strftime("%Y-%m-%d")
            for gid, g in list(STATS.items()):
                if gid in PROMO["exempt"] or PROMO["last_sent"].get(gid) == today:
                    continue
                if now.hour not in peak_hours(g):
                    continue
                active = [t for t in recent_msgs[gid] if time.time() - t < 600]
                if len(active) < PROMO_ACTIVE_MSGS:
                    continue   # گروه الان ساکته؛ دور بعد دوباره چک می‌شود
                try:
                    await bot.send_message(gid, random.choice(PROMO_MESSAGES).format(ch=PROMO_CHANNEL))
                    PROMO["last_sent"][gid] = today
                    save_promo()
                    await asyncio.sleep(2)
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(300)


def ensure_promo_task():
    global _promo_task
    if _promo_task is None or _promo_task.done():
        _promo_task = asyncio.get_event_loop().create_task(promo_loop())


# ---------- اخطارهای مالک ----------
try:
    with open(WARNS_FILE, "r", encoding="utf-8") as f:
        OWNER_WARNS = json.load(f)       # "gid:uid" -> تعداد اخطار
except Exception:
    OWNER_WARNS = {}


try:
    with open(MUTE_FILE, "r", encoding="utf-8") as f:
        MUTED = json.load(f)             # "gid:uid" -> زمان پایان سکوت (timestamp)
except Exception:
    MUTED = {}


def save_mutes():
    try:
        with open(MUTE_FILE, "w", encoding="utf-8") as f:
            json.dump(MUTED, f)
    except Exception:
        pass


def is_muted(gid, uid):
    """سریع و بدون await؛ سکوت‌های منقضی‌شده پاک می‌شوند"""
    k = f"{gid}:{uid}"
    end = MUTED.get(k)
    if not end:
        return False
    if time.time() >= end:
        MUTED.pop(k, None)
        save_mutes()
        return False
    return True


def save_warns():
    try:
        with open(WARNS_FILE, "w", encoding="utf-8") as f:
            json.dump(OWNER_WARNS, f, ensure_ascii=False)
    except Exception:
        pass


# ---------- کمکی‌ها ----------
async def get_roles(group_guid):
    """برگرداندن (مالک گروه, مجموعه ادمین‌ها) با کش ۵ دقیقه‌ای"""
    cached = owner_cache.get(group_guid)
    if cached and time.time() - cached[2] < 300:
        return cached[1], cached[0]
    owner, admins = None, set()
    try:
        res = await bot.get_group_admin_members(group_guid)
        members = res.in_chat_members if hasattr(res, "in_chat_members") else res.get("in_chat_members", [])
        for m in members:
            g = getattr(m, "member_guid", None) or (m.get("member_guid") if isinstance(m, dict) else None)
            jt = getattr(m, "join_type", None) or (m.get("join_type") if isinstance(m, dict) else "")
            if g:
                admins.add(g)
                if str(jt).lower() == "creator":
                    owner = g
    except Exception:
        pass
    owner_cache[group_guid] = (admins, owner, time.time())
    return owner, admins


async def is_privileged(group_guid, user_guid):
    """ادمین کل بات، مالک گروه یا ادمین گروه"""
    if user_guid in ADMIN_GUIDS:
        return True
    owner, admins = await get_roles(group_guid)
    return user_guid == owner or user_guid in admins


async def is_owner_or_botadmin(group_guid, user_guid):
    """مالک همین گروه (فقط داخل همان گروه) یا ادمین کل بات"""
    if user_guid in ADMIN_GUIDS:
        return True
    owner, _ = await get_roles(group_guid)
    return user_guid == owner


async def safe_delete(guid, msg_id):
    try:
        await bot.delete_messages(guid, [msg_id])
        return True
    except Exception:
        return False


def get_attr(obj, name, default=None):
    v = getattr(obj, name, None)
    if v is None and isinstance(obj, dict):
        v = obj.get(name)
    return v if v is not None else default


async def get_replied_author(gid, msg):
    """GUID نویسنده‌ی پیامی که روی آن ریپلای شده (یا None)"""
    reply_id = get_attr(msg, "reply_to_message_id")
    if not reply_id:
        return None, None
    try:
        res = await bot.get_messages_by_id(gid, [reply_id])
        msgs = get_attr(res, "messages", [])
        if msgs:
            return get_attr(msgs[0], "author_object_guid"), reply_id
    except Exception:
        pass
    return None, reply_id


async def say(gid, text, reply_id=None):
    try:
        if reply_id:
            return await bot.send_message(gid, text, reply_to_message_id=reply_id)
    except Exception:
        pass
    return await bot.send_message(gid, text)


# ---------- عضویت اجباری ----------
CHANNEL_GUID = None
MEMBER_OK = {}       # user_guid -> زمان آخرین تایید عضویت
WAIT_LINK = {}       # user_guid -> لینک گروهی که قبل از عضویت فرستاده


async def get_channel_guid():
    global CHANNEL_GUID
    if CHANNEL_GUID:
        return CHANNEL_GUID
    res = await bot.get_object_by_username(PROMO_CHANNEL.lstrip("@"))
    ch = get_attr(res, "channel") or {}
    CHANNEL_GUID = get_attr(ch, "channel_guid")
    return CHANNEL_GUID


async def is_channel_member(uid):
    """بررسی عضویت در کانال. بات باید در کانال ادمین باشد تا لیست اعضا را ببیند."""
    if time.time() - MEMBER_OK.get(uid, 0) < MEMBER_CACHE_SEC:
        return True
    try:
        guid = await get_channel_guid()
        start = None
        for _ in range(300):
            res = await bot.get_channel_all_members(guid, start_id=start)
            members = get_attr(res, "in_chat_members", []) or []
            if any(get_attr(m, "member_guid") == uid for m in members):
                MEMBER_OK[uid] = time.time()
                return True
            if not get_attr(res, "has_continue", False):
                return False
            start = get_attr(res, "next_start_id")
            if not start:
                return False
        return False
    except Exception as e:
        # اگر بات ادمین کانال نباشد بررسی ممکن نیست؛ برای اینکه کاربران گیر نکنند عبور می‌دهیم
        print("[عضویت اجباری] خطا در بررسی عضویت - بات را ادمین کانال کنید:", e)
        return True


# ---------- پیوی: دریافت لینک و عضویت ----------
@bot.on_message_updates(filters.is_private)
async def private_handler(update: Update):
    text = (update.text or "").strip()
    author = update.author_guid

    # --- عضویت اجباری (ادمین بات و /myguid معاف) ---
    if author not in ADMIN_GUIDS and text != "/myguid":
        if not await is_channel_member(author):
            m0 = JOIN_LINK_RE.search(text)
            if m0:
                WAIT_LINK[author] = m0.group(0)
            return await update.reply(FORCE_JOIN_TEXT)
        if text in CHECK_WORDS:
            link0 = WAIT_LINK.pop(author, None)
            if link0:
                PENDING[author] = link0
                return await update.reply("✅ عضویتت تأیید شد 🌹\n\n" + RULES_TEXT)
            return await update.reply("✅ عضویتت تأیید شد 🌹 حالا لینک گروهت رو بفرست.")

    if text in ("/start", "start", "شروع"):
        return await update.reply(
            f"سلام 👋 من {BOT_NAME} هستم، ربات مدیریت گروه.\n"
            "لینک گروه یا کانالت رو بفرست تا عضو بشم، بعدش منو ادمین کن 🌹"
        )
    if text == "/myguid":
        return await update.reply(f"GUID شما:\n{author}")

    ensure_promo_task()
    if text not in ACCEPT_WORDS:
        m = JOIN_LINK_RE.search(text)
        if m:
            PENDING[author] = m.group(0)
            return await update.reply(RULES_TEXT)
    elif author in PENDING:
        link = PENDING.pop(author)
        kind = JOIN_LINK_RE.search(link).group(1).lower()
        try:
            if kind == "joinc":
                await bot.join_channel_by_link(link)
            else:
                await bot.join_group(link)
            await update.reply("✅ عضو شدم! لطفاً منو ادمین کن تا بتونم مدیریت کنم.")
        except Exception:
            try:  # تلاش با روش دیگر
                await bot.join_group(link)
                await update.reply("✅ عضو شدم! منو ادمین کن تا کامل کار کنم.")
            except Exception:
                await update.reply("❌ نتونستم عضو بشم. لینک معتبره؟ (ممکنه محدودیت یا لینک منقضی باشه)")
        return

    if author in ADMIN_GUIDS and text == "/stats":
        total = sum(g.get("total", 0) for g in STATS.values())
        await update.reply(f"📊 گروه‌های ثبت‌شده: {len(STATS)}\nمجموع پیام‌ها: {total}")


# ---------- گروه‌ها ----------
@bot.on_message_updates(filters.is_group)
async def group_handler(update: Update):
    global BOT_GUID
    gid = update.object_guid
    uid = update.author_guid
    mid = update.message_id
    text = (update.text or "").strip()

    # --- کاربر در سکوت: فوراً حذف (قبل از هر کار دیگری) ---
    if uid and is_muted(gid, uid):
        await safe_delete(gid, mid)
        return

    # --- پیام‌های سرویس: خوش‌آمدگویی ---
    msg = get_attr(update, "message") or {}
    mtype = str(get_attr(msg, "type", "")).lower()
    if mtype == "event" or not text and get_attr(msg, "event_data"):
        ev = get_attr(msg, "event_data") or {}
        etype = str(get_attr(ev, "type", ""))
        if etype in ("JoinedGroupByLink", "AddedGroupMembers"):
            who = get_attr(get_attr(ev, "performer_object") or {}, "title", "") or \
                  get_attr(get_attr(ev, "peer_objects", [{}])[0] if get_attr(ev, "peer_objects") else {}, "title", "") or "عزیز"
            welcome = (
                f"🌹✨ سلام {who} عزیز، به گروه خوش آمدی! ✨🌹\n\n"
                "💎 خوشحالیم که کنارمونی\n"
                "📌 لطفاً قوانین رو رعایت کن:\n"
                "   ⛔ ارسال لینک و آیدی ممنوع\n"
                "   ⛔ اسپم و تبلیغات ممنوع\n"
                "   ✅ احترام به همه اعضا\n\n"
                f"🤖 مدیریت با {BOT_NAME}"
            )
            await bot.send_message(gid, welcome)
        return

    if not text or not uid:
        return

    # --- آمار ---
    g = STATS.setdefault(gid, {"total": 0, "users": {}})
    g["total"] += 1
    g["users"][uid] = g["users"].get(uid, 0) + 1
    hr = str(datetime.now(TZ).hour)
    g.setdefault("hours", {})[hr] = g["hours"].get(hr, 0) + 1
    recent_msgs[gid].append(time.time())
    save_stats()
    ensure_promo_task()

    # --- ادمین کل بات: فعال/غیرفعال کردن حذف تبلیغ برای این گروه (پرداخت ماهانه) ---
    if uid in ADMIN_GUIDS and text in ("/vip", "/unvip"):
        if text == "/vip" and gid not in PROMO["exempt"]:
            PROMO["exempt"].append(gid)
        elif text == "/unvip" and gid in PROMO["exempt"]:
            PROMO["exempt"].remove(gid)
        save_promo()
        return await update.reply("✅ تبلیغات این گروه غیرفعال شد." if text == "/vip" else "✅ تبلیغات این گروه فعال شد.")

    privileged = await is_privileged(gid, uid)
    owner_or_admin = await is_owner_or_botadmin(gid, uid)

    # --- بن / اخطار: مالک روی پیام عضو ریپلای می‌زند ---
    if owner_or_admin and text in (BAN_WORDS + WARN_WORDS + UNWARN_WORDS + PROMOTE_WORDS + DEMOTE_WORDS + MUTE_WORDS + UNMUTE_WORDS):
        target, rid = await get_replied_author(gid, msg)
        if not target:
            return await update.reply("↩️ برای استفاده، روی پیام عضو ریپلای بزن و بنویس: بن / اخطار / سکوت / ارتقا")
        if BOT_GUID is None:
            try:
                me = await bot.get_me()
                BOT_GUID = get_attr(get_attr(me, "user", me), "user_guid")
            except Exception:
                pass
        # --- ارتقا به ادمین / عزل ---
        if text in PROMOTE_WORDS + DEMOTE_WORDS:
            owner_g, admins_g = await get_roles(gid)
            if target == BOT_GUID or target == owner_g:
                return await update.reply("⛔ این کار روی مالک گروه یا خود ربات ممکن نیست.")
            promoting = text in PROMOTE_WORDS
            if promoting and target in admins_g:
                return await say(gid, "ℹ️ این کاربر از قبل ادمین است.", rid)
            if not promoting and target not in admins_g:
                return await say(gid, "ℹ️ این کاربر ادمین نیست.", rid)
            try:
                if promoting:
                    await bot.set_group_admin(gid, target, access_list=ADMIN_ACCESS, action="SetAdmin")
                else:
                    await bot.set_group_admin(gid, target, access_list=[], action="UnsetAdmin")
                owner_cache.pop(gid, None)   # کش نقش‌ها تازه شود
                return await say(gid, "👑 کاربر به دستور مالک گروه ادمین شد." if promoting
                                 else "✅ ادمینی این کاربر برداشته شد.", rid)
            except Exception:
                return await say(gid, "❌ نشد. منو ادمین گروه کن و دسترسی «افزودن ادمین» بهم بده.", rid)

        if target == BOT_GUID or await is_privileged(gid, target):
            return await update.reply("⛔ روی مالک، ادمین‌ها و خود ربات نمی‌شه بن یا اخطار داد.")
        key = f"{gid}:{target}"

        if text in MUTE_WORDS:
            MUTED[key] = time.time() + MUTE_HOURS * 3600
            save_mutes()
            return await say(gid, f"🔇 کاربر به دستور مالک گروه به مدت {MUTE_HOURS} ساعت در سکوت قرار گرفت.\nپیام‌هاش حذف می‌شه.", rid)
        if text in UNMUTE_WORDS:
            MUTED.pop(key, None)
            save_mutes()
            return await say(gid, "🔊 سکوت این کاربر برداشته شد.", rid)

        if text in UNWARN_WORDS:
            OWNER_WARNS.pop(key, None)
            save_warns()
            return await say(gid, "✅ اخطارهای این کاربر پاک شد.", rid)

        if text in BAN_WORDS:
            try:
                await bot.ban_group_member(gid, target)
                OWNER_WARNS.pop(key, None)
                save_warns()
                return await say(gid, "🚫 کاربر به دستور مالک گروه حذف شد.", rid)
            except Exception:
                return await say(gid, "❌ نتونستم حذفش کنم. منو ادمین گروه کن (با دسترسی حذف عضو).", rid)

        # اخطار
        OWNER_WARNS[key] = OWNER_WARNS.get(key, 0) + 1
        n = OWNER_WARNS[key]
        if n >= OWNER_MAX_WARNS:
            try:
                await bot.ban_group_member(gid, target)
                OWNER_WARNS.pop(key, None)
                save_warns()
                return await say(gid, f"🚫 اخطار {n}/{OWNER_MAX_WARNS} — کاربر به دلیل رسیدن به سقف اخطار از گروه حذف شد.", rid)
            except Exception:
                save_warns()
                return await say(gid, f"⚠️ اخطار {n}/{OWNER_MAX_WARNS} — به سقف رسید ولی نتونستم حذفش کنم. منو ادمین گروه کن.", rid)
        save_warns()
        return await say(gid, f"⚠️ اخطار {n}/{OWNER_MAX_WARNS} از طرف مالک گروه.\nبا رسیدن به {OWNER_MAX_WARNS} اخطار از گروه حذف می‌شی.", rid)

    # --- فرمان‌های مالک گروه ---
    if owner_or_admin and text in ("/panel", "پنل"):
        return await update.reply(
            f"⚙️ پنل {BOT_NAME}\n"
            "• آمار گپ — آمار پیام‌ها\n"
            "• لینک و آیدی و اسپم: فعال ✅\n"
            "فقط مالک گروه می‌تونه به این دستورات دسترسی داشته باشه."
        )

    # --- حذف لینک و آیدی (مالک و ادمین‌ها معاف) ---
    if not privileged:
        if LINK_RE.search(text) or ID_RE.search(text):
            await safe_delete(gid, mid)
            await bot.send_message(gid, "⛔ ارسال لینک و آیدی در این گروه ممنوعه!")
            return

        # --- ضد اسپم ---
        key = (gid, uid)
        now = time.time()
        dq = msg_times[key]
        dq.append(now)
        recent = [t for t in dq if now - t <= SPAM_WINDOW]
        if len(recent) >= SPAM_LIMIT:
            await safe_delete(gid, mid)
            warns[key] += 1
            if warns[key] >= SPAM_MAX_WARNS:
                try:
                    await bot.ban_group_member(gid, uid)
                    await bot.send_message(gid, "🚫 کاربر به دلیل اسپم از گروه حذف شد.")
                except Exception:
                    await bot.send_message(gid, "🚫 اسپم ممنوع! (برای حذف کاربر منو ادمین کنید)")
                warns[key] = 0
            else:
                await bot.send_message(gid, f"⚠️ اسپم ممنوعه! اخطار {warns[key]}/{SPAM_MAX_WARNS}")
            dq.clear()
            return

    # --- پاسخ به ریپلای روی بات / صدا زدن اسم بات ---
    called = BOT_NAME in text or "دنی اپ" in text
    replied_to_bot = False
    reply_id = get_attr(msg, "reply_to_message_id")
    if reply_id:
        try:
            if BOT_GUID is None:
                me = await bot.get_me()
                BOT_GUID = get_attr(get_attr(me, "user", me), "user_guid")
            res = await bot.get_messages_by_id(gid, [reply_id])
            msgs = get_attr(res, "messages", [])
            if msgs and get_attr(msgs[0], "author_object_guid") == BOT_GUID:
                replied_to_bot = True
        except Exception:
            pass

    if called or replied_to_bot:
        clean = text.replace(BOT_NAME, "").strip()
        if "آمار" in clean:
            top = sorted(g["users"].items(), key=lambda x: -x[1])[:5]
            lines = [f"{i+1}. {n} پیام" for i, (_, n) in enumerate(top)]
            return await update.reply(
                f"📊 آمار گپ\n💬 مجموع پیام‌ها: {g['total']}\n"
                f"👥 کاربران فعال: {len(g['users'])}\n🏆 برترین‌ها:\n" + "\n".join(lines)
            )
        for k, answers in GREETINGS.items():
            if k in clean:
                return await update.reply(answers[g["total"] % len(answers)])


if __name__ == "__main__":
    print(f"{BOT_NAME} در حال اجراست ...")
    try:
        bot.run()
    finally:
        save_stats(force=True)
