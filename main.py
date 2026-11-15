import os
from rubka import Robot, Message

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

bot = Robot(token=TOKEN)


@bot.on_message(commands=["start"])
async def start(bot: Robot, message: Message):
    await message.reply(
        "🎵 به ربات AHNG MUSIC خوش آمدید.\n\n"
        "برای شروع، شناسه کاربری خود را دریافت کنید:\n"
        "/id"
    )


@bot.on_message(commands=["id"])
async def get_id(bot: Robot, message: Message):
    await message.reply(
        f"شناسه کاربری شما:\n{message.sender_id}"
    )


print("AHNG MUSIC BOT is running...")
bot.run()
