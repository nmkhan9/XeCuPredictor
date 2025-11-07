import asyncio
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
from configs import HEADERS,PROXY

semaphore = asyncio.Semaphore(random.randint(5, 10))

async def crawl_page(
    session,
    func_get_links,
    i,
    link_set,
    headers= HEADERS,
    proxy=None,
    url_template="",
    no_new_count=0,
    MAX_NO_NEW=3,
):
    url = url_template.format(i)

    async with semaphore:
        start_time = time.perf_counter()
        try:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            async with session.get(url, headers=HEADERS, proxy=None, timeout=15) as resp:
                crawl_time = datetime.now().strftime("%H:%M:%S")
                if resp.status != 200:
                    print(f"❌ HTTP {resp.status} at page {i} | {crawl_time}")
                    return link_set, no_new_count, False

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                links = func_get_links(soup)

                if not links:
                    print(f"⚠️ No products found on page {i} | {crawl_time}")
                    return link_set, no_new_count, False

                before = len(link_set)
                link_set.update(links)
                after = len(link_set)

                elapsed = time.perf_counter() - start_time
                added = after - before

                if added == 0:
                    no_new_count += 1
                    print(f"⚠️ Page {i}: no new links ({no_new_count}/{MAX_NO_NEW}) | {elapsed:.2f}s | {crawl_time}")
                else:
                    no_new_count = 0
                    print(f"✅ Page {i} done. Added {added} new links | {elapsed:.2f}s | {crawl_time}")

                if no_new_count >= MAX_NO_NEW:
                    print(f"\n⛔ Stopping crawl: {MAX_NO_NEW} consecutive pages with no new links. | {crawl_time}")
                    return link_set, no_new_count, "STOP"

                return link_set, no_new_count, True

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            crawl_time = datetime.now().strftime("%H:%M:%S")
            print(f"⚠️ Error at page {i}: {e} | {elapsed:.2f}s | {crawl_time}")
            return link_set, no_new_count, False
