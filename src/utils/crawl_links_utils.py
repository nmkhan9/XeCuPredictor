import asyncio, aiohttp, random, time
from bs4 import BeautifulSoup
from configs import HEADERS, PROXY
from src.utils.io_utils import log, preview_data

PAGE = 500
CONCURRENT = random.randint(5, 8)
BATCH_SIZE = 20
MAX_RETRIES = 3

semaphore = asyncio.Semaphore(CONCURRENT)

# load link đã có (tránh trùng khi chạy lại)
def load_existing_links(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


async def crawl_links(session, func_get_links, i, total, url_template=""):
    url = url_template.format(i)

    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            start_time = time.perf_counter()

            try:
                await asyncio.sleep(random.uniform(0.5, 1.5))

                async with session.get(
                    url,
                    headers=HEADERS,
                    proxy=PROXY,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:

                    if resp.status != 200:
                        log("❌ HTTP", i, total, f"{resp.status} | Try {attempt}")
                        continue

                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    links = func_get_links(soup)

                    elapsed = time.perf_counter() - start_time

                    if links:
                        log("✅ DONE", i, total, f"{len(links)} links | {elapsed:.2f}s")

                        # 🔥 log gọn
                        if random.random() < 0.3:
                            log("📄 DATA", i, total, preview_data(links[:3]))

                        return links

                    else:
                        log("⚠️ EMPTY", i, total, "No data")

            except Exception as e:
                log("⚠️ ERROR", i, total, f"Try {attempt} | {type(e).__name__}")

            # exponential backoff + jitter
            await asyncio.sleep(min(2 ** attempt + random.uniform(0, 1), 5))

    return []


async def crawl_more_links(url_template, getlink, path_store):
    # load link cũ
    existing_links = load_existing_links(path_store)

    connector = aiohttp.TCPConnector(
        limit=CONCURRENT,
        limit_per_host=CONCURRENT
    )

    async with aiohttp.ClientSession(connector=connector) as session:

        for start in range(1, PAGE + 1, BATCH_SIZE):
            end = min(start + BATCH_SIZE, PAGE + 1)

            tasks = [
                crawl_links(session, getlink, i, PAGE, url_template)
                for i in range(start, end)
            ]

            results = await asyncio.gather(*tasks)

            # gom link mới
            batch_links = set()
            for links in results:
                if links:
                    batch_links.update(links)

            new_links = batch_links - existing_links

            # ghi file 1 lần / batch
            if new_links:
                with open(path_store, "a", encoding="utf-8") as f:
                    f.write("\n".join(new_links) + "\n")

                existing_links.update(new_links)

            log("📦 BATCH", start, PAGE, f"{start}-{end-1} | New: {len(new_links)} | Total: {len(existing_links)}")

            # nghỉ giữa batch
            await asyncio.sleep(random.uniform(2, 5))

    print(f"\n📦 Tổng số link: {len(existing_links)}")
    print(f"📁 File: {path_store}")