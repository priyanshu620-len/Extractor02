import aiohttp, json, re, io, time
from datetime import datetime

class FutureKulExtractor:
    def __init__(self):
        self.base_url = "https://www.futurekul.com/admin/api"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    async def _fetch_json(self, session, url):
        try:
            async with session.get(url, ssl=False, headers=self.headers) as res:
                if res.status != 200: return None
                text = await res.text()
                try: return json.loads(text)
                except:
                    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
                    return json.loads(match.group(1)) if match else None
        except: return None

    async def get_batches(self, is_live=True):
        status = "1" if is_live else "0"
        url = f"{self.base_url}/course/135/{status}/"
        async with aiohttp.ClientSession() as session:
            data = await self._fetch_json(session, url)
            return data.get("data", []) if data else []

    async def extract_links(self, batch_id, batch_title, user_info, start_time, batch_type):
        url = f"{self.base_url}/getCourseDataByTopic-v2/{batch_id}/"
        async with aiohttp.ClientSession() as session:
            content = await self._fetch_json(session, url)
            if not content or "data" not in content: return None, None

            data, links = content["data"], []
            v_count, p_count = 0, 0

            # --- Extraction Logic ---
            sections = [('paid_class', 'topic', 'class'), ('free_class', None, None), ('pdf', 'topic_name', 'pdf')]
            for key, t_key, c_key in sections:
                for item in data.get(key, []):
                    inner_items = item.get(c_key, [item]) if c_key else [item]
                    for itm in inner_items:
                        name = re.sub(r'<[^>]+>', '', itm.get('class_name') or itm.get('pdf_name') or '').strip()
                        link = itm.get('link') or itm.get('pdf_mobile')
                        if link:
                            links.append(f"{name} : {link}")
                            if '.pdf' in link.lower() or 'pdf' in name.lower(): p_count += 1
                            else: v_count += 1

            if not links: return None, None

            file_data = f"✨ FUTUREKUL BATCH: {batch_title}\n" + "="*30 + "\n\n" + "\n".join(links)
            file_io = io.BytesIO(file_data.encode('utf-8'))
            file_io.name = f"{batch_title.replace(' ', '_')}.txt"

            # --- Blockquote Report Format ---
            time_taken = int(time.time() - start_time)
            report = f"""
⚡ **FutureKul Extraction Report** ⚡

📚 **Batch Name:** `{batch_title}`
> • 📱 **App Name:** FutureKul
> • 🆔 **Batch ID:** `{batch_id}`
> • 🎯 **Batch Type:** {batch_type}
> • 🔗 **Total Content:** {len(links)}
> • 🎥 **Videos:** {v_count} | 📄 **PDFs:** {p_count}
> • ⏱️ **Total Time Taken:** {time_taken}s
> • 📅 **Date-Time:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
> • 🧾 **User ID:** `{user_info['id']}`
> • 💬 **Username:** {user_info['username']}
> • 👤 **Extracted by:** {user_info['mention']} 🐦‍🔥
╾─────────────────────────╼
"""
            return file_io, report
