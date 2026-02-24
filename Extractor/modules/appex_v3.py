import requests
import json
import cloudscraper
from pyrogram import filters
import os
import asyncio
from config import *
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from bs4 import BeautifulSoup

# Fix: Using CHANNEL_ID from your config.py instead of LOGS_CHANNEL
channel_id = CHANNEL_ID 
PREMIUM_LOGS = CHANNEL_ID 

def decrypt(enc):
    enc = b64decode(enc.split(':')[0])
    key = '638udh3829162018'.encode('utf-8')
    iv = 'fedcba9876543210'.encode('utf-8')
    if len(enc) == 0:
        return ""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(enc), AES.block_size)
    return plaintext.decode('utf-8')

async def fetch(session, url, headers):
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return {}
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            return json.loads(str(soup))
    except Exception:
        return {}

async def handle_course(session, api_base, bi, si, ti, hdr1, f):
    url = f"{api_base}/get/livecourseclassbycoursesubtopconceptapiv3?courseid={bi}&subjectid={si}&topicid={ti}&conceptid=&start=-1"
    r3 = await fetch(session, url, hdr1)
    for i in r3.get("data", []):
        vi = i.get("id")
        r4 = await fetch(session, f"{api_base}/get/fetchVideoDetailsById?course_id={bi}&video_id={vi}&ytflag=0&folder_wise_course=0", hdr1)
        vt = r4.get("data", {}).get("Title", "")
        vl = r4.get("data", {}).get("download_link", "")
        
        if vl:
            dvl = decrypt(vl)
            f.write(f"{vt}:{dvl}\n")
        else:
            encrypted_links = r4.get("data", {}).get("encrypted_links", [])
            for link in encrypted_links:
                a = link.get("path")
                if a:
                    da = decrypt(a)
                    f.write(f"{vt}:{da}\n")
                    break
        
        if "material_type" in r4.get("data", {}):
            if r4["data"]["material_type"] == "VIDEO":
                p1 = r4["data"].get("pdf_link", "")
                p2 = r4["data"].get("pdf_link2", "")
                if p1:
                    dp1 = decrypt(p1)
                    f.write(f"{vt}:{dp1}\n")
                if p2:
                    dp2 = decrypt(p2)
                    f.write(f"{vt}:{dp2}\n")

async def appex_v3_txt(app, message):
    # Prompt 1: API Link
    editable = await app.send_message(message.chat.id, "🌐 **Please send your API URL or Website link:**")
    api = (await app.listen(editable.chat.id)).text
    api_base = f"https://{api}" if not api.startswith(("http://", "https://")) else api
    
    # Prompt 2: Credentials
    editable2 = await app.send_message(message.chat.id, "📧 **Send Id*password or Token:**")
    raw_text = (await app.listen(editable2.chat.id)).text
    await editable.delete()
    await editable2.delete()

    if '*' in raw_text:
        raw_url = f"{api_base}/post/userLogin"
        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.9.1"
        }
        info = {"email": raw_text.split("*")[0], "password": raw_text.split("*")[1]}
        try:
            response = requests.post(raw_url, data=info, headers=hdr).json()
            userid = response["data"]["userid"]
            token = response["data"]["token"]
        except Exception:
            return await message.reply_text("❌ Login Failed. Check Password.")
            
        hdr1 = {"Auth-Key": "appxapi", "Authorization": token, "User-ID": userid, "source": "website"}
        await message.reply_text("✅ **Login Successful**")
    else:
        token = raw_text
        hdr1 = {"Auth-Key": "appxapi", "Authorization": token, "User-ID": "userid", "source": "website"}
        await message.reply_text("✅ **Token Login Successful**")

    try:
        mc1 = requests.get(f"{api_base}/get/get_all_purchases?userid={hdr1['User-ID']}&item_type=10", headers=hdr1).json()
    except Exception:
        return await message.reply_text("❌ Error fetching courses.")

    FFF = "𝗕𝗔𝗧𝗖𝗛 𝗜𝗗 ➤ 𝗕𝗔𝗧𝗖𝗛 𝗡𝗔𝗠𝗘\n\n"
    if "data" in mc1 and mc1["data"]:
        for i in mc1["data"]:
            for ct in i["coursedt"]:
                ci, cn = ct.get("id"), ct.get("course_name")
                FFF += f"**`{ci}`   -   `{cn}`**\n\n"
    
    file_path = "batches.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(FFF)
    
    dl = f"✅ **Login Success** for {api_base}\n\n`{token}`"
    await message.reply_document(document=file_path, caption=dl)
    
    editable3 = await app.send_message(message.chat.id, "**Now send the Course ID to Download**")
    input_id = (await app.listen(editable3.chat.id)).text
    await message.reply_text("⌛ **EXTRACTING... PLEASE WAIT.**")

    try:
        r = requests.get(f"{api_base}/get/course_by_id?id={input_id}", headers=hdr1).json()
        txtn = r["data"][0].get("course_name")
        filename = f"{input_id}_{txtn}.txt"
        
        async with aiohttp.ClientSession() as session:
            with open(filename, 'w') as f:
                r1 = await fetch(session, f"{api_base}/get/allsubjectfrmlivecourseclass?courseid={input_id}&start=-1", hdr1)
                for i in r1.get("data", []):
                    si = i.get("subjectid")
                    r2 = await fetch(session, f"{api_base}/get/alltopicfrmlivecourseclass?courseid={input_id}&subjectid={si}&start=-1", hdr1)
                    for t in r2.get("data", []):
                        ti = t.get("topicid")
                        await handle_course(session, api_base, input_id, si, ti, hdr1, f)
        
        await app.send_document(message.chat.id, filename)
        os.remove(filename)
    except Exception:
        await message.reply_text("❌ Extraction Failed.")
    finally:
        if os.path.exists(file_path): os.remove(file_path)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             #>scAmMER%
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              #>!scaMMEr_*)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            #+Scammer<+
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  #@%SCamMEr?
       
