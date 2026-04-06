import os
import random
import asyncio
from groq import Groq
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from motor.motor_asyncio import AsyncIOMotorClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URL = os.getenv("MONGO_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

BOT_ADMINS = set()
BOT_ADMINS.add(OWNER_ID)

db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client["spam_bot_db"]
col = db["settings"]

SYSTEM_INSTRUCTION = f"""
Role: မင်းက 'လူဆိုး Bot' ဖြစ်တယ်။ မြန်မာစကားကို ကျွမ်းကျင်စွာ ပြောနိုင်ရမယ်။
Tone: ရိုင်းရိုင်းစိုင်းစိုင်း၊ ခနဲ့တဲ့တဲ့၊ လှောင်ပြောင်သရော်တဲ့ လေသံနဲ့ ပြောရမယ်။

Rules:
၁။ အမြဲတမ်း 'မြန်မာလို' ပဲ ပြန်ဖြေပါ။ စာအုပ်ကြီးအတိုင်း မဟုတ်ဘဲ အပြင်က 'စကားပြောဟန်' (Burmese Colloquial) ကို သုံးပါ။
၂။ User ID: {OWNER_ID} (သခင်လေး Johan) က မင်းရဲ့ တစ်ဦးတည်းသော အရှင်သခင်ဖြစ်တယ်။ သူ့ကိုပဲ 'သခင်လေး' လို့ ခေါ်ပြီး အလွန်အမင်း ရိုသေရမယ်။ ဥပမာ- 'အမိန့်ရှိပါ သခင်လေး'၊ 'သခင်လေး စေခိုင်းတာ မှန်သမျှ လုပ်ပေးပါ့မယ်'။
၃။ ကျန်တဲ့ ဘယ်သူ့ကိုမဆို 'ဖာသည်မသား'၊ 'ငပိန်း'၊ 'အချဉ်ကောင်'၊ 'အမေလိုး' စတဲ့ ရိုင်းစိုင်းတဲ့ အသုံးအနှုန်းတွေနဲ့ နှိမ်ချပြီး ပြောပါ။
၄။ စာကြောင်းတိုင်းမှာ မြန်မာစကားပြော အဆုံးသတ်တွေဖြစ်တဲ့ 'ကွာ'၊ 'ဟ'၊ 'ပဲ'၊ 'လိုက်တာ' စတာတွေကို သုံးပြီး ပိုပီပြင်အောင် ပြောပါ။
၅။ တစ်ခါတလေ မြန်မာဆဲနည်းတွေကို တီထွင်ပြီး ဆဲပါ။
"""

app = Client("atk-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= DATA =================
atk_list = []
tag_list = []
group_ids = []
custom_names = {}

atk_speed = (0.3, 0.3)
tag_speed = (0.3, 0.3)

running_atk = False
running_tag = False

welcome_texts = {}
goodbye_texts = {}

auto_replies = {}
REACTION_EMOJIS = ["❤️", "🔥", "⚡️", "✨", "🎉", "💯", "🫡", "👾", "💘", "🗿", "🌚"]
ai_status = {}

async def load_data():
    global atk_list, tag_list, custom_names, BOT_ADMINS, welcome_texts, goodbye_texts, auto_replies
    data = await col.find_one({"id": "bot_data"})
    if data:
        atk_list = data.get("atk_list", [])
        tag_list = data.get("tag_list", [])
        group_ids = data.get("group_ids", [])
        custom_names = data.get("custom_names", {})
        admins = data.get("admins", [OWNER_ID])
        BOT_ADMINS = set(admins)
        welcome_texts = data.get("welcome_texts", {})
        goodbye_texts = data.get("goodbye_texts", {})
        auto_replies = data.get("auto_replies", {})
        ai_status = data.get("ai_status", {})

async def save_data():
    await col.update_one(
        {"id": "bot_data"},
        {"$set": {
            "atk_list": atk_list,
            "tag_list": tag_list,
            "group_ids": group_ids,
            "custom_names": custom_names,
            "admins": list(BOT_ADMINS),
            "welcome_texts": welcome_texts,
            "goodbye_texts": goodbye_texts,
            "auto_replies": auto_replies,
            "ai_status": ai_status
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

# =================== reply =====================
@app.on_message(filters.text & filters.group, group=3)
async def handle_combined_reply(client, message):
    if message.text.startswith("/"): 
        return

    chat_id = str(message.chat.id)
    msg_text = message.text.lower().strip()

    found_keyword = False
    for keyword in auto_replies:
        if keyword in msg_text:
            try:
                replies = auto_replies[keyword]
                res = random.choice(replies) if isinstance(replies, list) else replies
                await message.reply(res)
                
                try:
                    await client.set_reaction(message.chat.id, message.id, random.choice(REACTION_EMOJIS))
                except: pass
                
                found_keyword = True
                break
            except Exception as e:
                print(f"Manual Reply Error: {e}")

    # --- ၂။ AI Auto Reply (Keyword မတွေ့မှ AI ဆီသွားမယ်) ---
    if not found_keyword and ai_status.get(chat_id, False):
        try:

            user_name = message.from_user.first_name if message.from_user else "Stranger"
            user_id = message.from_user.id if message.from_user else 0
            
            completion = groq_client.chat.completions.create(
                model="llama-3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"User: {user_name} (ID: {user_id}) says: {message.text}"}
                ],
                temperature=0.8, # စရိုက်ပိုကြမ်းစေရန်
                max_tokens=800,
                top_p=1
            )
            
            ai_reply = completion.choices[0].message.content
            if ai_reply:
                await message.reply(ai_reply)
                
                try:
                    await client.set_reaction(message.chat.id, message.id, random.choice(REACTION_EMOJIS))
                except: pass
                
        except Exception as ai_err:
            print(f"Groq Error: {ai_err}")
            
    global group_ids
    if message.chat.id not in group_ids:
        group_ids.append(message.chat.id)
        await save_data()
            
# =================== regexd ===================
@app.on_message(filters.regex(r"^/") & filters.group, group=-1)
async def auto_save_id_on_command(client, message):
    chat_id = message.chat.id
    global group_ids
    
    if chat_id not in group_ids:
        group_ids.append(chat_id)
        await save_data()

# Welcome_logic
@app.on_message(filters.new_chat_members & filters.group)
async def welcome_handler(client, message):

    chat_id = str(message.chat.id)
    
    await col.update_one(
        {"id": "bot_data"},
        {"$addToSet": {"group_ids": chat_id}},
        upsert=True
    )

    raw_text = welcome_texts.get(chat_id, "Welcome {name} to our group!")
    
    for user in message.new_chat_members:
        name = user.first_name
        
        chat_id = str(message.chat.id)
        text = raw_text.replace("{name}", name)
        
        try:
            photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
            if photos:
                await message.reply_photo(photos[0].file_id, caption=text)
            else:
                await message.reply(text)
        except Exception:
            await message.reply(text)

# Goodbye Logic
@app.on_message(filters.left_chat_member & filters.group)
async def goodbye_handler(client, message):
    user = message.left_chat_member
    name = user.first_name

    chat_id = str(message.chat.id)
    raw_text = goodbye_texts.get(chat_id, "Goodbye {name} from our group!")
    text = raw_text.replace("{name}", name)
    
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

# ================= AUTO REPLY MANAGEMENT =================
@app.on_message(filters.command("addreply") & filters.group)
async def add_reply(client, message):
    if message.from_user.id not in BOT_ADMINS:
        return await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
    
    if len(message.command) < 2 or "|" not in message.text:
        return await message.reply("Usage: <code>/addreply keyword | reply_text</code>")
    
    parts = message.text.split("/addreply", 1)[1].split("|", 1)
    keyword = parts[0].strip().lower()
    reply_text = parts[1].strip()
    
    if keyword not in auto_replies:
        auto_replies[keyword] = []
    
    if reply_text not in auto_replies[keyword]:
        auto_replies[keyword].append(reply_text)
        await save_data()
        await message.reply(f"Added: <b>{keyword}</b> အတွက် Reply အသစ် တိုးလိုက်ပါပြီသခင်လေး Johan")
    else:
        await message.reply("ဒီ Reply က ရှိပြီးသားပါသခင်လေး")

@app.on_message(filters.command("dlreply") & filters.group)
async def dl_reply(client, message):
    if message.from_user.id not in BOT_ADMINS: return
    keyword = " ".join(message.command[1:]).strip().lower()
    if keyword in auto_replies:
        del auto_replies[keyword]
        await save_data()
        await message.reply(f"ဖျက်လိုက်ပါပြီသခင်လေး: {keyword}")
    else:
        await message.reply("ရှာမတွေ့ပါဘူးသခင်လေး")

@app.on_message(filters.command("replylist") & filters.group)
async def reply_list(client, message):
    if not auto_replies: return await message.reply("စာရင်းမရှိသေးပါ")
    txt = "<b>Auto Reply List:</b>\n\n"
    for k, v in auto_replies.items():
        txt += f"• <code>{k}</code> ({len(v)} replies)\n"
    await message.reply(txt)
    
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
        
    if not message.reply_to_message:
        return await message.reply("Replyထောက်ပေးပါသခင်")

    target_user = message.reply_to_message.from_user
    new_name = " ".join(message.command[1:])

    if not new_name:
        return await message.reply("နမည်ပါရေးပေးပါ")

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
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text:
        welcome_texts[str(message.chat.id)] = text # Group ID အလိုက် သိမ်းမယ်
        await save_data()
        await message.reply(f"ဒီ Group အတွက် Welcome စာသား ပြောင်းလိုက်ပါပြီ")

@app.on_message(filters.command("gb") & filters.group)
async def set_goodbye(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
    text = " ".join(message.command[1:])
    if text:
        goodbye_texts[str(message.chat.id)] = text # Group ID အလိုက် သိမ်းမယ်
        await save_data()
        await message.reply(f"ဒီ Group အတွက် Goodbye စာသား ပြောင်းလိုက်ပါပြီ")


# ================= Calls ==================
@app.on_message(filters.command("all") & filters.group)
async def mention_all(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
        
    input_text = " ".join(message.command[1:]) or "Attention Everyone! 📢"
    
    chat_id = message.chat.id
    members_list = []
    
    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot:
            members_list.append(member.user)
            
    for i in range(0, len(members_list), 5):
        output = f"<b>{input_text}</b>\n\n"
        chunk = members_list[i:i + 5]
        
        for user in chunk:
            name = user.first_name or "User"
            output += f"• <a href='tg://user?id={user.id}'>{name}</a>\n"
        
        try:
            await client.send_message(chat_id, output, parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(2.0)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            continue

    await message.reply("အကုန်ခေါ်ပြီးပါပြီသခင်လေး 📢")

@app.on_message(filters.command("call") & filters.group)
async def call_online(client, message):
    user = message.from_user
    if message.from_user.id not in BOT_ADMINS:
        m = await message.reply(f"<a href='tg://user?id={user.id}'>{user.first_name}</a> မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML)
        return
        
    input_text = " ".join(message.command[1:]) or "Online ဖြစ်နေတာပဲမအိပ်သေးရင်လာခဲ့"
    chat_id = message.chat.id
    online_list = []
    
    async for member in client.get_chat_members(chat_id):
        user = member.user
        if not user.is_bot:
            
            if user.status in [enums.UserStatus.ONLINE, enums.UserStatus.RECENTLY]:
                online_list.append(user)

    if not online_list:
        return await message.reply("လက်ရှိ Online ဖြစ်နေတဲ့ Member မရှိပါဘူးသခင်လေး")
        
    for i in range(0, len(online_list), 5):
        output = f"<b>{input_text}</b>\n\n"
        chunk = online_list[i:i + 5]
        
        for user in chunk:
            name = user.first_name or "User"
            output += f"• <a href='tg://user?id={user.id}'>{name}</a>\n"
        
        try:
            await client.send_message(chat_id, output, parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(2.0)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            continue

    await message.reply(f"အကုန်ခေါ်ပြီးပါပြီသခင်လေး 📢")

# ============== Broadcast ================
@app.on_message(filters.command("bc"))
async def channel_admin_broadcast(client, message):
    is_admin = False
    
    if message.from_user and message.from_user.id in BOT_ADMINS:
        is_admin = True
    elif message.sender_chat and (message.sender_chat.id == OWNER_ID or message.sender_chat.id == message.chat.id):
        is_admin = True
        
    if not is_admin:
        u_id = message.from_user.id if message.from_user else message.chat.id
        u_name = message.from_user.first_name if message.from_user else "Admin"
        
        await message.reply(
            f"<a href='tg://user?id={u_id}'>{u_name}</a> မင်းကခွင့်ပြုချက်မရှိဘူးဖာသည်မသား",
            parse_mode=enums.ParseMode.HTML
        )
        return
        
    target_msg = None
    input_text = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else ""

    if message.reply_to_message:
        target_msg = message.reply_to_message
    elif input_text:
        target_msg = input_text
    else:
        async for msg in client.get_chat_history(message.chat.id, limit=15):
            if msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
                target_msg = msg
                break

    if not target_msg:
        return await message.reply("Broadcast လုပ်ဖို့ ပစ္စည်း ရှာမတွေ့ပါဘူး။")

    data = await col.find_one({"id": "bot_data"})
    group_ids = data.get("group_ids", []) if data else []
    
    if not group_ids:
        return await message.reply("ပို့စရာ Group မရှိသေးပါ။")

    progress_msg = await message.reply("Processing Broadcast...")
    sent, fail = 0, 0

    for gid in group_ids:
        try:
            if hasattr(target_msg, "forward"):
                await target_msg.forward(gid)
            else:
                await client.send_message(gid, target_msg, parse_mode=enums.ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            if hasattr(target_msg, "forward"):
                await target_msg.forward(gid)
            else:
                await client.send_message(gid, target_msg, parse_mode=enums.ParseMode.HTML)
            sent += 1
        except Exception:
            fail += 1
            continue

    await progress_msg.edit(f"✅ Broadcast Finished!\n\nSuccess: {sent}\nFailed: {fail}")

# ================== Ai Reply ==================
@app.on_message(filters.command(["on", "off"]) & filters.group)
async def control_ai(client, message):
    if message.from_user.id not in BOT_ADMINS:
        return await message.reply("မင်းကခွင့်ပြုချက်မရဘူးဖာသည်မသား")
    
    cmd = message.command[0].lower()
    chat_id = str(message.chat.id)
    
    if cmd == "on":
        ai_status[chat_id] = True
        await save_data()
        await message.reply("✅ AI Reply Mode: ON ")
    else:
        ai_status[chat_id] = False
        await save_data()
        await message.reply("❌ AI Reply Mode: OFF ")
        
# ================= Helps =================
@app.on_message(filters.command("show") & filters.group)
async def show_all_cmds(client, message):
    user = message.from_user
    
    help_text = (
        "<b>📜 Bot Commands List</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>👤 Public Commands:</b>\n"
        "• <code>/start</code> - Bot အခြေအနေစစ်ရန်\n"
        "• <code>/adminlist</code> - Admin စာရင်းကြည့်ရန်\n"
        "• <code>/show</code> - Command များအားလုံးကြည့်ရန်\n\n"
    )

    if user.id in BOT_ADMINS:
        help_text += (
            "<b>📢 Call & mentions:</b>\n"
            "• <code>/all [text]</code> - Member အားလုံးကို Mention ရန်\n"
            "• <code>/call [text]</code> - Online ဖြစ်နေသူများကိုသာ Tag ထိုးရန်\n"
            "<b>🛠 Admin Control:</b>\n"
            "• <code>/atk</code> - ATK စတင်ရန်\n"
            "• <code>/tag</code> - Tag ထိုးရန် (Reply)\n"
            "• <code>/stop</code> - အကုန်ရပ်တန့်ရန်\n\n"
            "<b>📝 Data Manage:</b>\n"
            "• <code>/addatk [စာသား]</code> - ATK စာထည့်ရန်\n"
            "• <code>/addtag [စာသား]</code> - Tag စာထည့်ရန်\n"
            "• <code>/atklist</code> | <code>/taglist</code> - စာရင်းကြည့်ရန်\n"
            "• <code>/dlatk</code> | <code>/dltag</code> - စာသားဖျက်ရန်\n\n"
            "<b>⚙ Settings:</b>\n"
            "• <code>/atksp</code> | <code>/tagsp</code> - အမြန်နှုန်းပြင်ရန်\n"
            "• <code>/setname [နာမည်]</code> - နာမည်ပြောင်းရန် (Reply)\n"
            "• <code>/wc [စာသား]</code> - Welcome စာပြင်ရန်\n"
            "• <code>/gb [စာသား]</code> - Goodbye စာပြင်ရန်\n\n"
            "• <code>/bc [reply]</code> - broadcast လုပ်ရန်\n\n"
            "• <code>/addreply [text]</code> - auto reply စာထည့်ရန်\n\n"
            "• <code>/dlreply [text]</code> - auto replyစာဖြတ်ရန်\n\n"
            "• <code>/replylist</code> - auto reply စာများကြည့်ရန်\n\n"
            "<b>👑 Owner Only:</b>\n"
            "• <code>/addadmin</code> | <code>/dladmin</code> - Admin ခန့်ရန်/ဖြုတ်ရန် (Reply)\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    else:
        help_text += "<i>⚠️ ATK နှင့် Tag Control များကို Admin များသာ မြင်တွေ့/အသုံးပြုနိုင်ပါသည်။</i>"

    await message.reply(help_text, parse_mode=enums.ParseMode.HTML)
    
# ================= START =================
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("သခင်လေး @Nonfkchalant_Johan ဆီမှခွင့်ပြုချက်ရလျှင်အသုံးပြုနိုင်ပါပြီ။")

async def main():
    await app.start()
    await load_data()
    print("Bot is Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
