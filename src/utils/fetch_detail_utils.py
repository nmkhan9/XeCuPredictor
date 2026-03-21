import asyncio
import random
import time
from datetime import datetime
from configs import HEADERS, PROXY

MAX_RETRIES = 3

def log(status, idx, total, msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{idx}/{total}] {status} {msg}")

def preview_data(data, max_len=120):
    """In gọn dữ liệu"""
    text = str(data)
    return text[:max_len] + "..." if len(text) > max_len else text


async def fetch_detail(session, func_parse_html, link, idx, total, semaphore):
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            start_time = time.perf_counter()

            try:
                await asyncio.sleep(random.uniform(0.3, 1.2))
                log("🌐", idx, total, f"Fetching (attempt {attempt})")

                async with session.get(
                    link,
                    headers=HEADERS,
                    proxy=PROXY,
                    timeout=20
                ) as resp:

                    if resp.status != 200:
                        log("❌", idx, total, f"HTTP {resp.status}")
                        continue

                    html = await resp.text(encoding="utf-8", errors="ignore")
                    car_info = func_parse_html(html)

                    duration = time.perf_counter() - start_time

                    # in dữ liệu vừa crawl (rút gọn)
                    log("📄", idx, total, f"Data: {preview_data(car_info)}")

                    log("✅", idx, total, f"Done in {duration:.2f}s")

                    return car_info

            except asyncio.TimeoutError:
                duration = time.perf_counter() - start_time
                log("⏱️", idx, total, f"Timeout {duration:.2f}s (attempt {attempt})")

            except Exception as e:
                duration = time.perf_counter() - start_time
                log("⚠️", idx, total, f"{type(e).__name__}: {e}")

            if attempt < MAX_RETRIES:
                sleep_time = random.uniform(1, 2) * attempt
                log("🔁", idx, total, f"Retry in {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
            else:
                log("⛔", idx, total, f"Failed after {MAX_RETRIES} attempts")
                return None