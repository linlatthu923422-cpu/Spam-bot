import os
import asyncio
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 123456789  # <-- မင်း Telegram ID
BOT_ADMINS = set()
BOT_ADMINS.add(OWNER_ID)  # Owner is auto admin

app = Client("atk-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= DATA =================
atk_list = []
tag_list = []

atk_speed = 0.3
tag_speed = 0.3

running_atk = False
running_tag = False

# ================= HELPER =================
async def auto_delete(msg, delay=3):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ================= ADD =================
@app.on_message(filters.command("Addatk") & filters.group)
async def add_atk(client, message):
    text = " ".join(message.command[1:])
    if text:
        atk_list.append(text)
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")
        await auto_delete(m)
        await message.delete()

@app.on_message(filters.command("Addtag") & filters.group)
async def add_tag(client, message):
    text = " ".join(message.command[1:])
    if text:
        tag_list.append(text)
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")
        await auto_delete(m)
        await message.delete()

# ================= LIST =================
@app.on_message(filters.command("Atklist") & filters.group)
async def atklist(client, message):
    txt = "\n".join(atk_list) or "စာမရှိပါ"
    m = await message.reply(f"<code>{txt}</code>")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("Taglist") & filters.group)
async def taglist(client, message):
    txt = "\n".join(tag_list) or "စာမရှိပါ"
    m = await message.reply(f"<code>{txt}</code>")
    await auto_delete(m)
    await message.delete()

# ================= DELETE =================
@app.on_message(filters.command("Dlatk") & filters.group)
async def dlatk(client, message):
    text = " ".join(message.command[1:])
    if text in atk_list:
        atk_list.remove(text)
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("Dltag") & filters.group)
async def dltag(client, message):
    text = " ".join(message.command[1:])
    if text in tag_list:
        tag_list.remove(text)
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")
    await auto_delete(m)
    await message.delete()

# ================= SPEED =================
@app.on_message(filters.command("Atksp") & filters.group)
async def atksp(client, message):
    global atk_speed
    atk_speed = float(message.command[1])
    m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {atk_speed}")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("Tagsp") & filters.group)
async def tagsp(client, message):
    global tag_speed
    tag_speed = float(message.command[1])
    m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {tag_speed}")
    await auto_delete(m)
    await message.delete()

# ================= ATK =================
@app.on_message(filters.command("Atk") & filters.group)
async def atk(client, message):
    global running_atk
    running_atk = True

    await message.delete()

    while running_atk:
        for text in atk_list:
            if not running_atk:
                break
            try:
                await message.reply(text)
                await asyncio.sleep(atk_speed)
            except:
                break

# ================= TAG =================
@app.on_message(filters.command("Tag") & filters.group)
async def tag(client, message):
    global running_tag
    running_tag = True

    if not message.reply_to_message:
        return await message.reply("ဖာသည်မသားကိုreplyပေးပါ")

    user = message.reply_to_message.from_user

    await message.delete()

    while running_tag:
        for text in tag_list:
            if not running_tag:
                break
            try:
                await message.reply(f"{user.mention} {text}")
                await asyncio.sleep(tag_speed)
            except:
                break

# ================= STOP =================
@app.on_message(filters.command("Stop") & filters.group)
async def stop(client, message):
    global running_atk, running_tag
    running_atk = False
    running_tag = False

    m = await message.reply("ပျင်းလာလို့ဖာသည်မသားကိုခဏတာလွှတ်မြောက်ခွင့်ပေးလိုက်ပါပြီ")
    await auto_delete(m)
    await message.delete()

# ================= START =================
@app.on_message(filters.command("Start"))
async def start(client, message):
    await message.reply("စတင်နေပါပြီ")

app.run()
