import os
import asyncio
from pyrogram import Client, filters

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID"))  # <-- မင်း Telegram ID
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
@app.on_message(filters.command("addatk") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def add_atk(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    text = " ".join(message.command[1:])
    if text:
        atk_list.append(text)
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")
        await auto_delete(m)
        await message.delete()

@app.on_message(filters.command("addtag") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def add_tag(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    text = " ".join(message.command[1:])
    if text:
        tag_list.append(text)
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")
        await auto_delete(m)
        await message.delete()

# ================= LIST =================
@app.on_message(filters.command("atklist") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def atklist(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    txt = "\n".join(atk_list) or "စာမရှိပါ"
    m = await message.reply(f"<code>{txt}</code>")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("taglist") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def taglist(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    txt = "\n".join(tag_list) or "စာမရှိပါ"
    m = await message.reply(f"<code>{txt}</code>")
    await auto_delete(m)
    await message.delete()

# ================= DELETE =================
@app.on_message(filters.command("dlatk") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def dlatk(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    text = " ".join(message.command[1:])
    if text in atk_list:
        atk_list.remove(text)
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("dltag") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def dltag(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    text = " ".join(message.command[1:])
    if text in tag_list:
        tag_list.remove(text)
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")
    await auto_delete(m)
    await message.delete()

# ================= SPEED =================
@app.on_message(filters.command("atksp") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def atksp(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    global atk_speed
    atk_speed = float(message.command[1])
    m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {atk_speed}")
    await auto_delete(m)
    await message.delete()

@app.on_message(filters.command("tagsp") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def tagsp(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    global tag_speed
    tag_speed = float(message.command[1])
    m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {tag_speed}")
    await auto_delete(m)
    await message.delete()

# ================= ATK =================
@app.on_message(filters.command("atk") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def atk(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
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
@app.on_message(filters.command("tag") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def tag(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
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
@app.on_message(filters.command("stop") & filters.group & filters.user(lambda uid: uid in BOT_ADMINS))
async def stop(client, message):
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
        return
    global running_atk, running_tag
    running_atk = False
    running_tag = False

    m = await message.reply("ပျင်းလာလို့ဖာသည်မသားကိုခဏတာလွှတ်မြောက်ခွင့်ပေးလိုက်ပါပြီ")
    await auto_delete(m)
    await message.delete()

# =============== AddAdmin ===============
@app.on_message(filters.command("addadmin") & filters.group & filters.user(OWNER_ID))
async def add_admin(client, message):
    if not message.reply_to_message:
        return await message.reply("သခင်လေးကိုreplyပေးပါ")
    user = message.reply_to_message.from_user
    BOT_ADMINS.add(user.id)
    m = await message.reply(f"{user.first_name} အသုံးပြုနိုင်ပါပြီသခင်")
    await message.delete()

# =============== Dladmin ================
@app.on_message(filters.command("dladmin") & filters.group & filters.user(OWNER_ID))
async def dl_admin(client, message):
    if not message.reply_to_message:
        return await message.reply("replyအသုံပြုပါ")
    user = message.reply_to_message.from_user
    if user.id in BOT_ADMINS:
        BOT_ADMINS.remove(user.id)
        m = await message.reply(f"{user.first_name} အသုံးပြုဖို့ခွင့်မပြုတော့ဘူး")
    else:
        m = await message.reply("User is not an admin")
    await message.delete()

# ============== Adminlist ===============
@app.on_message(filters.command("adminlist") & filters.group & filters.user(OWNER_ID))
async def admin_list(client, message):
    if not BOT_ADMINS:
        m = await message.reply("မရှိသေးပါ")
        return
    txt = ""
    for uid in BOT_ADMINS:
        txt += f"<a href='tg://user?id={uid}'>• {uid}</a>\n"
    m = await message.reply(txt, disable_web_page_preview=True)
    await message.delete()

# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("သခင်လေး @Nonfkchalant_Johan ဆီမှခွင့်ပြုချက်ရလျှင်အသုံးပြုနိုင်ပါပြီ။")

app.run()
