import asyncio
import aiohttp
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
from configs import HEADERS,PROXY

semaphore = asyncio.Semaphore(random.randint(5, 10))

async def crawl_links(session, func_get_links, i, url_template=""):
    url = url_template.format(i)
    async with semaphore:
        start_time = time.perf_counter()
        try:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            async with session.get(url, headers=HEADERS, proxy= PROXY, timeout=15) as resp:
                crawl_time = datetime.now().strftime("%H:%M:%S")
                if resp.status != 200:
                    print(f"❌ HTTP {resp.status} at page {i} | {crawl_time}")
                    return []

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                links = func_get_links(soup)

                if not links:
                    print(f"⚠️ No products found on page {i} | {crawl_time}")
                    return []

                elapsed = time.perf_counter() - start_time
                print(f"✅ Page {i} done. Found {len(links)} links | {elapsed:.2f}s | {crawl_time}")
                return links

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            crawl_time = datetime.now().strftime("%H:%M:%S")
            print(f"⚠️ Error at page {i}: {e} | {elapsed:.2f}s | {crawl_time}")
            return []
        
async def crawl_more_links(url_template, PAGE, getlink, path_store):
    link_set = set()

    async with aiohttp.ClientSession() as session:
        tasks = [crawl_links(session, getlink, i, url_template) for i in range(1, PAGE + 1)]
        results = await asyncio.gather(*tasks)

    with open(path_store, "a", encoding="utf-8") as f:
        for links in results:
            for link in links:
                if link not in link_set:
                    f.write(link + "\n")
                    f.flush()
                    link_set.add(link)

    print(f"\n📦 Tổng số link thu được: {len(link_set)}")
    print(f"📁 Đã lưu tại: {path_store}")