import asyncio
import aiohttp
import json
import re
from datetime import datetime

async def fetch_data(session, url):
    """Fetch data from URL and parse JSON from HTML response"""
    try:
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                text = await response.text()
                # Try to find JSON in the HTML response
                # Look for JSON patterns in the text
                json_patterns = re.findall(r'\{.*\}', text, re.DOTALL)
                for pattern in json_patterns:
                    try:
                        data = json.loads(pattern)
                        return data
                    except json.JSONDecodeError:
                        continue
                
                # Try to extract JSON from script tags or other common patterns
                script_patterns = [
                    r'data\s*:\s*(\{.*\})',
                    r'var\s+data\s*=\s*(\{.*\});',
                    r'window\.data\s*=\s*(\{.*\});'
                ]
                
                for pattern in script_patterns:
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            return data
                        except json.JSONDecodeError:
                            continue
                
                # If no JSON found, try to parse the whole text as JSON
                try:
                    data = json.loads(text)
                    return data
                except json.JSONDecodeError:
                    print(f"No valid JSON found in response from {url}")
                    return None
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def main():
    print("="*50)
    print("BATCH EXTRACTOR")
    print("="*50)
    
    # User input
    print("Choose batch type:")
    print("1. Live Batch")
    print("2. Recorded Batch")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice not in ['1', '2']:
        print("Invalid choice!")
        return
    
    is_live = '1' if choice == '1' else '0'
    base_url = "https://www.futurekul.com/admin/api"
    user_id = ""
    
    print(f"\nFetching {'Live' if choice == '1' else 'Recorded'} Batches...")
    
    # Start timer
    start_time = datetime.now()
    
    # Disable SSL verification
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Get batches
        batches_url = f"{base_url}/course/135/{is_live}/{user_id}"
        print(f"Fetching from: {batches_url}")
        batches_data = await fetch_data(session, batches_url)
        
        if not batches_data:
            print("Failed to fetch batches - No data returned!")
            return
            
        if isinstance(batches_data, dict) and batches_data.get("state") != 200:
            print(f"API Error: {batches_data.get('msg', 'Unknown error')}")
            return
            
        if isinstance(batches_data, dict):
            batches = batches_data.get("data", [])
        elif isinstance(batches_data, list):
            batches = batches_data
        else:
            batches = []
        
        if not batches:
            print("No batches found!")
            return
        
        # Display batches
        print(f"\n{'='*50}")
        print("Available Batches:")
        print("="*50)
        
        for i, batch in enumerate(batches, 1):
            if isinstance(batch, dict):
                title = batch.get('title', 'No Title')
                price = batch.get('price', 'N/A')
                batch_id = batch.get('id', 'N/A')
            else:
                title = str(batch)
                price = 'N/A'
                batch_id = 'N/A'
            print(f"{i}. {title} - ₹{price} (ID: {batch_id})")
        
        # Select batch
        try:
            batch_choice = int(input(f"\nSelect a batch (1-{len(batches)}): ").strip())
            if 1 <= batch_choice <= len(batches):
                selected_batch = batches[batch_choice - 1]
            else:
                print("Invalid selection!")
                return
        except ValueError:
            print("Please enter a valid number!")
            return
        
        if not isinstance(selected_batch, dict):
            print("Invalid batch data!")
            return
            
        # Get batch content
        print(f"\nExtracting content for: {selected_batch['title']}")
        
        batch_content_url = f"{base_url}/getCourseDataByTopic-v2/{selected_batch['id']}/{user_id}"
        print(f"Fetching content from: {batch_content_url}")
        batch_content = await fetch_data(session, batch_content_url)
        
        if not batch_content:
            print("Failed to fetch batch content - No data!")
            return
            
        if isinstance(batch_content, dict) and batch_content.get("state") != 200:
            print(f"Content API Error: {batch_content.get('msg', 'Unknown error')}")
            return
            
        if isinstance(batch_content, dict):
            content_data = batch_content.get("data", {})
        else:
            content_data = batch_content
        
        # Prepare filename
        filename = f"{selected_batch['title'].replace(' ', '_').replace('/', '_')}.txt"
        
        # Extract all links
        all_links = []
        
        # Free classes
        free_classes = content_data.get('free_class', []) if isinstance(content_data, dict) else []
        for cls in free_classes:
            if isinstance(cls, dict) and cls.get('link'):
                title = re.sub(r'<[^>]+>', '', cls.get('class_name', '')).strip()
                if title:
                    all_links.append(('Free Classes', '', f'{title} : {cls["link"]}'))
        
        # Paid classes
        paid_classes = content_data.get('paid_class', []) if isinstance(content_data, dict) else []
        for topic in paid_classes:
            if isinstance(topic, dict):
                topic_name = topic.get('topic', 'All Classes')
                if 'class' in topic:
                    classes = topic['class']
                    for cls in classes:
                        if isinstance(cls, dict) and cls.get('link'):
                            title = re.sub(r'<[^>]+>', '', cls.get('class_name', '')).strip()
                            if title:
                                link = cls['link']
                                if link:
                                    all_links.append((topic_name, '', f'{title} : {link}'))
        
        # PDFs
        pdf_data = content_data.get('pdf', []) if isinstance(content_data, dict) else []
        for pdf_topic in pdf_data:
            if isinstance(pdf_topic, dict):
                topic_name = pdf_topic.get('topic_name', 'All Notes')
                if 'pdf' in pdf_topic:
                    pdfs = pdf_topic['pdf']
                    for pdf in pdfs:
                        if isinstance(pdf, dict) and pdf.get('pdf_mobile'):
                            title = pdf.get('pdf_name', '').strip()
                            if title:
                                all_links.append((topic_name, '', f'{title} : {pdf["pdf_mobile"]}'))
        
        # Write to file
        print(f"\nWriting {len(all_links)} links to {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            for folder, subfolder, content in all_links:
                f.write(f"{folder} {subfolder} {content}\n")
        
        # Calculate time
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Count links
        video_count = len([l for l in all_links if ('m3u8' in l[2] or 'youtube' in l[2] or 'playlist' in l[2])])
        pdf_count = len([l for l in all_links if 'pdf' in l[2]])
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Total Links: {len(all_links)}")
        print(f"Video Links: {video_count}")
        print(f"PDF Links: {pdf_count}")
        print(f"Time taken: {total_time:.2f} seconds")
        print(f"Saved to: {filename}")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(main())