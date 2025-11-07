import asyncio
import random
import time
from datetime import datetime
from configs import HEADERS,PROXY

MAX_RETRIES = 3

async def fetch_detail(session, func_parse_html, link, idx, total, semaphore):
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            start_time = time.perf_counter()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                await asyncio.sleep(random.uniform(0.3, 1))
                async with session.get(link, headers=HEADERS, proxy=None, timeout=20) as resp:
                    if resp.status != 200:
                        print(f"{now} ❌ [{idx}/{total}] HTTP {resp.status} at {link}")
                        continue

                    html = await resp.text(encoding="utf-8", errors="ignore")
                    car_info = func_parse_html(html)

                    duration = time.perf_counter() - start_time
                    print(f"{now} ✅ Done car {idx}/{total} in {duration:.2f}s")
                    return car_info

            except Exception as e:
                duration = time.perf_counter() - start_time
                print(f"⚠️ [{idx}/{total}] Attempt {attempt}/{MAX_RETRIES} failed after {duration:.2f}s for {link}: {e}")

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 * attempt)
                else:
                    print(f"⛔ [{idx}/{total}] Giving up on {link} after {MAX_RETRIES} attempts.")
                    return None