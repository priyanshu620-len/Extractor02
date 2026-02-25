import requests
import json

BASE_URL = "https://backend.multistreaming.site/api"

# ========== FETCH ACTIVE COURSES ==========
def fetch_active_batches(user_id="3708939"):
    url = f"{BASE_URL}/courses/active?userId={user_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    return data.get("data", [])

# ========== FETCH CLASSES (FULL BATCH) ==========
def fetch_classes(course_id):
    url = f"{BASE_URL}/courses/{course_id}/classes?populate=full"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    all_classes = []
    classes_data = data.get("data", {}).get("classes", [])

    for topic in classes_data:
        topic_name = topic.get("topicName", "Unknown Topic")
        for cls in topic.get("classes", []):
            title = cls.get("title", "Untitled")
            teacher = cls.get("teacherName", "")
            
            video_link = None
            mp4s = cls.get("mp4Recordings", [])
            for mp4 in mp4s:
                if mp4.get("quality") == "720p":
                    video_link = mp4.get("url")
                    break
            if not video_link and mp4s:
                video_link = mp4s[0].get("url")

            if video_link:
                all_classes.append(f"{topic_name} | {title} ({teacher}) : {video_link}")

            for pdf in cls.get("classPdf", []):
                name = pdf.get("name", "")
                link = pdf.get("url", "")
                if link:
                    all_classes.append(f"{topic_name} | {name} (PDF) : {link}")

    return all_classes

# ========== FETCH TODAY'S CLASSES ==========
def fetch_todays_classes(course_id):
    url = f"{BASE_URL}/courses/{course_id}/todays-classes"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    todays = []

    for cls in data.get("data", []):
        title = cls.get("title", "Untitled")
        teacher = cls.get("teacherName", "")
        mp4s = cls.get("mp4Recordings", [])
        link = mp4s[0].get("url") if mp4s else cls.get("class_link", "")
        if link:
            todays.append(f"{title} ({teacher}) : {link}")

    return todays

# ========== FETCH PDFs ==========
def fetch_pdfs(course_id):
    url = f"{BASE_URL}/courses/{course_id}/pdfs?groupBy=topic"
    res = requests.get(url)
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
                pdf_links.append(f"{topic_name} | {title} ({teacher}) : {link}")

    return pdf_links

# ========== BOT INTEGRATION FUNCTION ==========
# Ye function aapka bot call karega
def get_final_data(course_id, mode="1"):
    combined_data = []
    if mode == "1":
        combined_data.extend(fetch_classes(course_id))
        combined_data.extend(fetch_pdfs(course_id))
    else:
        combined_data.extend(fetch_todays_classes(course_id))
    
    return "\n".join(combined_data)
