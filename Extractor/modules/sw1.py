import requests
import json

BASE_URL = "https://backend.multistreaming.site/api"

# ========== FETCH COURSE NAME BY ID ==========
def get_course_name(course_id, user_id="3708939"):
    """Fetches original batch title using ID to avoid button data errors"""
    try:
        url = f"{BASE_URL}/courses/active?userId={user_id}"
        res = requests.get(url)
        res.raise_for_status()
        batches = res.json().get("data", [])
        for b in batches:
            if str(b.get("id")) == str(course_id):
                return b.get("title", "Unknown_Batch")
    except Exception:
        pass
    return "Batch"

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
def get_final_data(course_id, mode="1"):
    classes_list = fetch_classes(course_id)
    pdfs_list = fetch_pdfs(course_id)
    
    combined_data = classes_list + pdfs_list
    final_text = "\n".join(combined_data)
    
    video_count = 0
    pdf_count = 0
    for item in combined_data:
        if "(PDF) :" in item:
            pdf_count += 1
        else:
            video_count += 1
            
    # Asli Batch Title nikalna
    real_title = get_course_name(course_id)
            
    return {
        "text": final_text,
        "total": len(combined_data),
        "videos": video_count,
        "pdfs": pdf_count,
        "title": real_title
    }
