import asyncio, aiohttp, time, random
from configs import HEADERS, PROXY
from src.utils.io_utils import log, preview_data

MAX_RETRIES = 3

async def fetch_detail(session, func_parse_html, link, idx, total, semaphore):
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            start_time = time.perf_counter()

            try:
                await asyncio.sleep(random.uniform(0.3, 1))
                log("🌐", idx, total, f"Fetching (try {attempt})")

                async with session.get(
                    link,
                    headers=HEADERS,
                    proxy=PROXY,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as resp:

                    if resp.status != 200:
                        log("❌", idx, total, f"HTTP {resp.status}")
                        continue

                    html = await resp.text(encoding="utf-8", errors="ignore")
                    car_info = func_parse_html(html)

                    duration = time.perf_counter() - start_time

                    # chỉ log 1 phần data
                    if random.random() < 0.2:  # chỉ 20% request log data
                        log("📄", idx, total, preview_data(car_info))

                    log("✅", idx, total, f"{duration:.2f}s")

                    return car_info

            except asyncio.TimeoutError:
                log("⏱️", idx, total, f"Timeout (try {attempt})")

            except Exception as e:
                log("⚠️", idx, total, f"{type(e).__name__}")

            # exponential backoff chuẩn hơn
            if attempt < MAX_RETRIES:
                sleep_time = min(2 ** attempt + random.uniform(0, 1), 5)
                log("🔁", idx, total, f"Retry in {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
            else:
                log("⛔", idx, total, "Failed")
                return None