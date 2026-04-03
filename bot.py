import os
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from motor.motor_asyncio import AsyncIOMotorClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URL = os.getenv("MONGO_URL")

BOT_ADMINS = set()
BOT_ADMINS.add(OWNER_ID)  # Owner is auto admin

db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client["spam_bot_db"]
col = db["settings"]

app = Client("atk-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= DATA =================
atk_list = []
tag_list = []
custom_names = {}

atk_speed = (0.3, 0.3)
tag_speed = (0.3, 0.3)

running_atk = False
running_tag = False

# DATA အပိုင်းမှာ ထည့်ပါ
welcome_text = "Welcome to our group!"
goodbye_text = "Goodbye from our group!"

# load_data() ထဲမှာ ဖြည့်စွက်ပါ
global welcome_text, goodbye_text
welcome_text = data.get("welcome_text", "Welcome to our group!")
goodbye_text = data.get("goodbye_text", "Goodbye from our group!")

# save_data() ထဲမှာ ဖြည့်စွက်ပါ
"welcome_text": welcome_text,
"goodbye_text": goodbye_text,

async def load_data():
    global atk_list, tag_list, custom_names, BOT_ADMINS
    data = await col.find_one({"id": "bot_data"})
    if data:
        atk_list = data.get("atk_list", [])
        tag_list = data.get("tag_list", [])
        custom_names = data.get("custom_names", {})
        admins = data.get("admins", [OWNER_ID])
        BOT_ADMINS = set(admins)

async def save_data():
    await col.update_one(
        {"id": "bot_data"},
        {"$set": {
            "atk_list": atk_list,
            "tag_list": tag_list,
            "custom_names": custom_names,
            "admins": list(BOT_ADMINS)
        }},
        upsert=True
    )

# ================= BACKGROUND LOOP FUNCTIONS =================
async def run_atk_loop(client, chat_id):
    global running_atk
    while running_atk:
        for text in atk_list:
            if not running_atk: break
            try:
                await client.send_message(chat_id, text)
                await asyncio.sleep(random.uniform(atk_speed[0], atk_speed[1]))
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue

async def run_tag_loop(client, chat_id, target_user):
    global running_tag
    # ID ကို String အနေနဲ့ DB မှာသိမ်းထားတာဖြစ်လို့ ပြန်ရှာရင် str() သုံးရပါတယ်
    display_name = custom_names.get(str(target_user.id), target_user.first_name)
    clickable_tag = f"<a href='tg://user?id={target_user.id}'>{display_name}</a>"

    while running_tag:
        for text in tag_list:
            if not running_tag: break
            try:
                await client.send_message(chat_id, f"{clickable_tag} {text}", parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(random.uniform(tag_speed[0], tag_speed[1]))
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue

# Welcome Logic
@app.on_message(filters.new_chat_members & filters.group)
async def welcome_handler(client, message):
    for user in message.new_chat_members:
        name = user.first_name
        text = welcome_text.replace("{name}", name)
        
        try:
            # User ရဲ့ pfp ကို ယူမယ်
            photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
            if photos:
                await message.reply_photo(photos[0].file_id, caption=text)
            else:
                # pfp မရှိရင် စာပဲပို့မယ်
                await message.reply(text)
        except Exception:
            await message.reply(text)

# Goodbye Logic
@app.on_message(filters.left_chat_member & filters.group)
async def goodbye_handler(client, message):
    user = message.left_chat_member
    name = user.first_name
    text = goodbye_text.replace("{name}", name)
    
    try:
        photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
        if photos:
            await message.reply_photo(photos[0].file_id, caption=text)
        else:
            await message.reply(text)
    except Exception:
        await message.reply(text)
        
# ================= ADD =================
@app.on_message(filters.command("addatk") & filters.group)
async def add_atk(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text:
        atk_list.append(text)
        await save_data()
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")

@app.on_message(filters.command("addtag") & filters.group)
async def add_tag(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text:
        tag_list.append(text)
        await save_data()
        m = await message.reply("စာသိမ်းပြီးပါပြီသခင်လေးJohan")

# ================= LIST =================
@app.on_message(filters.command("atklist") & filters.group)
async def atklist(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    txt = "\n".join(atk_list) or "စာမရှိပါ"
    await save_data()
    m = await message.reply(f"<code>{txt}</code>")

@app.on_message(filters.command("taglist") & filters.group)
async def taglist(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    txt = "\n".join(tag_list) or "စာမရှိပါ"
    await save_data()
    m = await message.reply(f"<code>{txt}</code>")

# ================= DELETE =================
@app.on_message(filters.command("dlatk") & filters.group)
async def dlatk(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text in atk_list:
        atk_list.remove(text)
        await save_data()
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")

@app.on_message(filters.command("dltag") & filters.group)
async def dltag(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text in tag_list:
        tag_list.remove(text)
        await save_data()
    m = await message.reply("ဖျတ်လိုက်ပါပြီသခင်လေးJohan")

# ================= SPEED =================
@app.on_message(filters.command("atksp") & filters.group)
async def atksp(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား", parse_mode=enums.ParseMode.HTML)
        return
    global atk_speed
    try:
        val = message.command[1]

        if "-" in val:
            min_sp, max_sp = map(float, val.split("-"))
            atk_speed = (min_sp, max_sp)
        else:
            sp = float(val)
            atk_speed = (sp, sp)
        m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {atk_speed}")

        await save_data()
    except Exception:
        await message.reply("Usage: /atksp 0.1-0.8")

@app.on_message(filters.command("tagsp") & filters.group)
async def tagsp(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား", parse_mode=enums.ParseMode.HTML)
        return
    global tag_speed
    try:
        val = message.command[1]

        if "-" in val:
            min_sp, max_sp = map(float, val.split("-"))
            tag_speed = (min_sp, max_sp)
        else:
            sp = float(val)
            tag_speed = (sp, sp)
        m = await message.reply(f"အမြန်နှုန်းကိုပြုပြင်ပြီးပါပြီသခင် = {tag_speed}")

        await save_data()
    except Exception:
        await message.reply("Usage: /tagsp 0.1-0.8")

# ================ NAME =================
@app.on_message(filters.command("setname") & filters.group)
async def set_custom_name(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return

    # Reply ထောက်ပြီး နာမည်ပေးရမယ် (ဥပမာ - /setname ဖာသည်မသား)
    if not message.reply_to_message:
        return await message.reply("Replyထောက်ပေးပါသခင်")

    target_user = message.reply_to_message.from_user
    new_name = " ".join(message.command[1:])

    if not new_name:
        return await message.reply("နမည်ပါရေးပေးပါ")

    # Dictionary ထဲမှာ သိမ်းလိုက်ပြီ
    custom_names[str(target_user.id)] = new_name
    await save_data()
    await message.reply(f"User {target_user.id} ဖာသည်မသား '{new_name}' မင်းနမည်အသစ်အဖေပေးတာ")
    
# ================= ATK =================
@app.on_message(filters.command("atk") & filters.group)
async def atk(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return

    global running_atk

    if running_atk:
        return await message.reply("ATKတစ်ခုRunနေပြီးသားပါသခင်လေး")
    
    running_atk = True
    chat_id = message.chat.id

    asyncio.create_task(run_atk_loop(client, message.chat.id))
    await message.reply("ခွေးစရိုက်ပါပြီသခင်လေး")

# ================= TAG =================
@app.on_message(filters.command("tag") & filters.group)
async def tag(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    global running_tag

    if not message.reply_to_message:
        return await message.reply("ဖာသည်မသားကို reply ပေးပါ")

    if running_tag:
        return await message.reply("Tagတစ်ခုRunနေပြီးသားပါသခင်လေး")

    running_tag = True
    target_user = message.reply_to_message.from_user
    chat_id = message.chat.id

    asyncio.create_task(run_tag_loop(client, message.chat.id, message.reply_to_message.from_user))
    await message.reply("ခွေးစရိုက်ပါပြီသခင်လေး")

# ================= STOP =================
@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    global running_atk, running_tag
    running_atk = False
    running_tag = False

    m = await message.reply("ပျင်းလာလို့ဖာသည်မသားကိုခဏတာလွှတ်မြောက်ခွင့်ပေးလိုက်ပါပြီ")

# =============== AddAdmin ===============
@app.on_message(filters.command("addadmin") & filters.group & filters.user(OWNER_ID))
async def add_admin(client, message):
    if not message.reply_to_message:
        return await message.reply("သခင်လေးကိုreplyပေးပါ")
    user = message.reply_to_message.from_user
    BOT_ADMINS.add(user.id)
    m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> အသုံးပြုနိုင်ပါပြီသခင်",
        parse_mode=enums.ParseMode.HTML)

# =============== Dladmin ================
@app.on_message(filters.command("dladmin") & filters.group & filters.user(OWNER_ID))
async def dl_admin(client, message):
    if not message.reply_to_message:
        return await message.reply("replyအသုံပြုပါ")
    user = message.reply_to_message.from_user
    if user.id in BOT_ADMINS:
        BOT_ADMINS.remove(user.id)
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> အသုံးပြုဖို့ခွင့်မပြုတော့ဘူး",
            parse_mode=enums.ParseMode.HTML)
    else:
        m = await message.reply("User is not an admin")

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

# ========= Edit welcome/goodbye =========
@app.on_message(filters.command("wc") & filters.group)
async def set_welcome(client, message):
    if message.from_user.id not in BOT_ADMINS: return
    global welcome_text
    text = " ".join(message.command[1:])
    if text:
        welcome_text = text
        await save_data()
        await message.reply(f"Welcome message ပြောင်းလိုက်ပါပြီ- \n`{welcome_text}`")

@app.on_message(filters.command("gb") & filters.group)
async def set_goodbye(client, message):
    if message.from_user.id not in BOT_ADMINS: return
    global goodbye_text
    text = " ".join(message.command[1:])
    if text:
        goodbye_text = text
        await save_data()
        await message.reply(f"Goodbye message ပြောင်းလိုက်ပါပြီ- \n`{goodbye_text}`")
        
# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("သခင်လေး @Nonfkchalant_Johan ဆီမှခွင့်ပြုချက်ရလျှင်အသုံးပြုနိုင်ပါပြီ။")

async def main():
    await app.start()
    await load_data()  # <--- Bot တက်တာနဲ့ DB ကစာတွေ ပြန်ယူဖို့
    print("Bot is Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
