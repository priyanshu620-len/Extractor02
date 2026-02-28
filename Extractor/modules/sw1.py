import requests
import json
import datetime
import time
from urllib.parse import urlparse

# ========== CONFIGURATION ==========
BASE_URL = "https://backend.multistreaming.site/api"
# Aapka Brand Logo (ONeX Extractor)
MY_BRAND_THUMB = "https://i.postimg.cc/Y0x5RtMH/Whats-App-Image-2026-02-28-at-6-57-52-PM.jpg"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://multistreaming.site",
    "Referer": "https://multistreaming.site/"
})

# ========== 1. FETCH ACTIVE BATCHES & DETAILS ==========
def fetch_active_batches(user_id="3708939"):
    """Sare active courses fetch karta hai (Fixes AttributeError)"""
    try:
        url = f"{BASE_URL}/courses/active?userId={user_id}"
        res = session.get(url, timeout=15)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        print(f"Error fetching batches: {e}")
        return []

def get_batch_details(course_id, user_id="3708939"):
    """Batch ka Title aur Thumbnail URL nikaalta hai"""
    batches = fetch_active_batches(user_id)
    for b in batches:
        if str(b.get("id")) == str(course_id):
            title = b.get("title", "Batch")
            thumb = b.get("thumbnail") or b.get("previewImage") or "https://via.placeholder.com/150"
            return title, thumb
    return "Batch", "https://via.placeholder.com/150"

# ========== 2. FETCH CLASSES (VIDEOS & NOTES) ==========
def fetch_classes(course_id):
    try:
        url = f"{BASE_URL}/courses/{course_id}/classes?populate=full"
        res = session.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()

        all_classes = []
        classes_data = data.get("data", {}).get("classes", [])

        for topic in classes_data:
            t_name = topic.get("topicName", "Unknown Topic")
            for cls in topic.get("classes", []):
                title = cls.get("title", "Untitled")
                teacher = cls.get("teacherName", "Unknown")
                
                # Video Logic
                video_link = None
                mp4s = cls.get("mp4Recordings", [])
                for mp4 in mp4s:
                    if mp4.get("quality") == "720p":
                        video_link = mp4.get("url")
                        break
                if not video_link and mp4s:
                    video_link = mp4s[0].get("url")

                if video_link:
                    all_classes.append(f"🎥 {t_name} | {title} ({teacher}) : {video_link}")

                # Inline PDF Extraction
                for pdf in cls.get("classPdf", []):
                    p_name = pdf.get("name", "Class Note")
                    p_link = pdf.get("url", "")
                    if p_link:
                        all_classes.append(f"📄 {t_name} | {p_name} (PDF) : {p_link}")

        return all_classes
    except Exception as e:
        print(f"Error fetching classes: {e}")
        return []

# ========== 3. FETCH PDFs (DPPs & FOLDERS) ==========
def fetch_pdfs(course_id):
    try:
        url = f"{BASE_URL}/courses/{course_id}/pdfs?groupBy=topic"
        res = session.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()

        pdf_links = []
        topics = data.get("data", {}).get("topics", [])
        for topic in topics:
            t_name = topic.get("topicName", "Unknown Topic")
            for pdf in topic.get("pdfs", []):
                p_title = pdf.get("title", "Untitled")
                p_teacher = pdf.get("teacherName", "Unknown")
                p_link = pdf.get("uploadPdf")
                if p_link:
                    icon = "📘" if "DPP" in p_title.upper() or "DPP" in t_name.upper() else "📁"
                    pdf_links.append(f"{icon} {t_name} | {p_title} ({p_teacher}) : {p_link}")

        return pdf_links
    except Exception as e:
        print(f"Error fetching PDFs: {e}")
        return []

# ========== 4. FINAL DATA & STYLISH REPORT ==========
def get_final_data(course_id, tg_user_id="N/A", tg_username="N/A", extractor_name="ONeX"):
    start_time = time.time()
    
    # Extraction Start
    classes_list = fetch_classes(course_id)
    pdfs_list = fetch_pdfs(course_id)
    real_title, batch_thumb = get_batch_details(course_id)
    
    combined_data = classes_list + pdfs_list
    video_count = sum(1 for item in combined_data if "🎥" in item)
    note_count = sum(1 for item in combined_data if "📄" in item or "📁" in item)
    dpp_count = sum(1 for item in combined_data if "📘" in item)
    
    time_taken = round(time.time() - start_time, 2)
    current_dt = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Stylish Report (As per your Screenshot)
    report = (
        f"⚡ **Selection Way Extraction Report** ⚡\n\n"
        f"📚 **Batch Name:** *{real_title}*\n"
        f"> • 📱 **App:** Selection Way\n"
        f"> • 🆔 **Batch ID:** `{course_id}`\n"
        f"> • 🔗 **Total Content:** {len(combined_data)}\n"
        f"> • 🎥 **Videos:** {video_count} | 📄 **PDFs:** {note_count + dpp_count}\n"
        f"> • 🖼️ **Thumbnail:** [Click Here To View]({batch_thumb})\n"
        f"> • ⏱️ **Total Time Taken:** {time_taken}s\n"
        f"> • 📅 **Date-Time:** {current_dt}\n"
        f"> • 🧾 **User ID:** `{tg_user_id}`\n"
        f"> • 💬 **Username:** @{tg_username}\n"
        f"• 👤 **Extracted by:** ꧁{extractor_name}꧂\n"
        f"╾─────────────────────────╼"
    )

    return {
        "text": "\n".join(combined_data),
        "report": report,
        "title": real_title,
        "brand_thumb": MY_BRAND_THUMB, # Ye aapka ONeX logo hai
        "batch_thumb": batch_thumb      # Ye batch ki image hai
    }
