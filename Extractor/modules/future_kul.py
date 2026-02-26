import aiohttp
import json
import re
import io

class FutureKulExtractor:
    def __init__(self):
        self.base_url = "https://www.futurekul.com/admin/api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    async def _fetch_json(self, session, url):
        """Internal helper to parse JSON from response"""
        try:
            async with session.get(url, ssl=False, headers=self.headers) as response:
                if response.status != 200: return None
                text = await response.text()
                try:
                    return json.loads(text)
                except:
                    # Fallback for JSON inside script/HTML
                    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
                    return json.loads(match.group(1)) if match else None
        except:
            return None

    async def get_batches(self, is_live=True):
        """Returns list of batches"""
        batch_type = "1" if is_live else "0"
        url = f"{self.base_url}/course/135/{batch_type}/"
        async with aiohttp.ClientSession() as session:
            data = await self._fetch_json(session, url)
            return data.get("data", []) if data else []

    async def extract_links(self, batch_id, batch_title):
        """Extracts content and returns (BytesIO_File, Count)"""
        url = f"{self.base_url}/getCourseDataByTopic-v2/{batch_id}/"
        async with aiohttp.ClientSession() as session:
            content = await self._fetch_json(session, url)
            if not content or "data" not in content: return None, 0

            data = content["data"]
            links = []

            # Process Paid/Free Classes
            for key in ['paid_class', 'free_class']:
                items = data.get(key, [])
                for item in items:
                    topic = item.get('topic', 'General') if isinstance(item, dict) else 'Free'
                    classes = item.get('class', [item]) if isinstance(item, dict) else [item]
                    for cls in classes:
                        name = re.sub(r'<[^>]+>', '', cls.get('class_name', '')).strip()
                        link = cls.get('link')
                        if link: links.append(f"[{topic}] {name} : {link}")

            # Process PDFs
            for p_topic in data.get('pdf', []):
                t_name = p_topic.get('topic_name', 'Notes')
                for pdf in p_topic.get('pdf', []):
                    name = pdf.get('pdf_name', '').strip()
                    link = pdf.get('pdf_mobile')
                    if link: links.append(f"[PDF-{t_name}] {name} : {link}")

            if not links: return None, 0

            # Create file in memory
            file_data = f"Batch: {batch_title}\nTotal: {len(links)}\n" + "="*40 + "\n\n" + "\n".join(links)
            file_io = io.BytesIO(file_data.encode('utf-8'))
            file_io.name = f"{batch_title.replace(' ', '_')}.txt"
            return file_io, len(links)
