import requests
import json
import datetime
import time
from urllib.parse import urlparse

BASE_URL = "https://backend.multistreaming.site/api"
session = requests.Session()

# ========== FETCH COURSE NAME BY ID ==========
def get_course_name(course_id, user_id="3708939"):
    """Fetches original batch title using ID"""
    try:
        url = f"{BASE_URL}/courses/active?userId={user_id}"
        res = session.get(url, timeout=10)
        res.raise_for_status()
        batches = res.json().get("data", [])
        for b in batches:
            if str(b.get("id")) == str(course_id):
                return b.get("title", "Unknown_Batch")
    except Exception:
        pass
    return "Batch"

# ========== FETCH CLASSES (FULL BATCH) ==========
def fetch_classes(course_id):
    try:
        url = f"{BASE_URL}/courses/{course_id}/classes?populate=full"
        res = session.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        all_classes = []
        classes_data = data.get("data", {}).get("classes", [])

        for topic in classes_data:
            topic_name = topic.get("topicName", "Unknown Topic")
            for cls in topic.get("classes", []):
                title = cls.get("title", "Untitled")
                teacher = cls.get("teacherName", "")
                
                # Video Extraction
                video_link = None
                mp4s = cls.get("mp4Recordings", [])
                for mp4 in mp4s:
                    if mp4.get("quality") == "720p":
                        video_link = mp4.get("url")
                        break
                if not video_link and mp4s:
                    video_link = mp4s[0].get("url")

                if video_link:
                    all_classes.append(f"🎥 {topic_name} | {title} ({teacher}) : {video_link}")

                # Inline PDF Extraction
                for pdf in cls.get("classPdf", []):
                    name = pdf.get("name", "Class Note")
                    link = pdf.get("url", "")
                    if link:
                        all_classes.append(f"📄 {topic_name} | {name} (PDF) : {link}")

        return all_classes
    except Exception:
        return []

# ========== FETCH PDFs ==========
def fetch_pdfs(course_id):
    try:
        url = f"{BASE_URL}/courses/{course_id}/pdfs?groupBy=topic"
        res = session.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        pdf_links = []
        topics = data.get("data", {}).get("topics", [])
        for topic in topics:
            topic_name = topic.get("topicName", "Unknown Topic")
            for pdf in topic.get("pdfs", []):
                title = pdf.get("title", "Untitled")
                teacher = pdf.get("teacherName", "")
                link = pdf.get("uploadPdf")
                if link:
                    # Logic to identify DPPs vs regular Notes
                    icon = "📘" if "DPP" in title.upper() or "DPP" in topic_name.upper() else "📁"
                    pdf_links.append(f"{icon} {topic_name} | {title} ({teacher}) : {link}")

        return pdf_links
    except Exception:
        return []

# ========== FINAL DATA & REPORT GENERATION ==========
def get_final_data(course_id, tg_user_id="N/A", tg_username="N/A", extractor_name="User"):
    start_time = time.time()
    
    # Fetch Data
    classes_list = fetch_classes(course_id)
    pdfs_list = fetch_pdfs(course_id)
    real_title = get_course_name(course_id)
    
    # Calculate Counts
    combined_data = classes_list + pdfs_list
    video_count = sum(1 for item in combined_data if "🎥" in item)
    note_count = sum(1 for item in combined_data if "📄" in item or "📁" in item)
    dpp_count = sum(1 for item in combined_data if "📘" in item)
    
    # Dynamic App Name from URL
    domain = urlparse(BASE_URL).netloc
    app_display_name = domain.replace("backend.", "").split('.')[0].capitalize()
    
    # Time and Date
    time_taken = round(time.time() - start_time, 2)
    current_dt = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Generate Report with Blockquotes
    report = (
        f"⚡ **Batch Extraction Report** ⚡\n\n"
        f"📚 **Batch Name:** {real_title}\n"
        f"> • 🔢 **Batch ID:** `{course_id}`\n"
        f"> • 📱 **App Name:** {app_display_name}\n"
        f"> • 🛒 **Purchased:** ❌ NO\n"
        f"> • 🔗 **Total Content:** {len(combined_data)}\n"
        f"> • 🎥 **Videos:** {video_count} | 📄 **Notes:** {note_count}\n"
        f"> • 📹 **DPP Videos:** 0 | 📘 **DPP Notes:** {dpp_count}\n"
        f"> • 📅 **Date-Time:** {current_dt}\n"
        f"> • ⏱️ **Total Time Taken:** {time_taken}s\n"
        f"> • 🧾 **User ID:** `{tg_user_id}`\n"
        f"> • 💬 **Username:** @{tg_username}\n"
        f"> • 👤 **Extracted by:** {extractor_name}\n"
        f"╾─────────────────────────╼"
    )

    return {
        "text": "\n".join(combined_data),
        "report": report,
        "title": real_title
    }
