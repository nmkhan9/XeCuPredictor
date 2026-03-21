import asyncio
import random
import aiohttp
import pandas as pd

from src.utils.fetch_detail_utils import fetch_detail
from src.utils.io_utils import (
    read_links_from_file,
    upload_to_bigquery,
    clean_column_names,
    upload_to_db
)

BATCH_SIZE = 100
MIN_DELAY, MAX_DELAY = 3, 5
TIMEOUT = aiohttp.ClientTimeout(total=25)


async def crawl_details(path_file, parse_car_detail, table_id, table_name):
    link_set = read_links_from_file(path_file)
    total_links = len(link_set)

    print(f"✅ Found {total_links} links in {path_file}\n")

    remaining_links = list(link_set)
    semaphore = asyncio.Semaphore(random.randint(2, 4))

    all_cars = []

    connector = aiohttp.TCPConnector(limit=50, ssl=False)

    async with aiohttp.ClientSession(
        timeout=TIMEOUT,
        connector=connector
    ) as session:

        # delay đầu (tránh burst request ngay lập tức)
        await asyncio.sleep(random.uniform(1, 3))

        for batch_idx, batch_start in enumerate(range(0, total_links, BATCH_SIZE), start=1):
            batch = remaining_links[batch_start: batch_start + BATCH_SIZE]

            print(f"📦 Batch {batch_idx}: {len(batch)} links")

            tasks = [
                fetch_detail(
                    session,
                    parse_car_detail,
                    link,
                    idx,
                    total_links,
                    semaphore
                )
                for idx, link in enumerate(batch, batch_start + 1)
            ]

            # return_exceptions=True để không crash cả batch
            results = await asyncio.gather(*tasks, return_exceptions=True)

            batch_cars = []
            for r in results:
                if isinstance(r, Exception):
                    print(f"⚠️ Task error: {r}")
                elif r:
                    batch_cars.append(r)

            all_cars.extend(batch_cars)

            # save từng batch (tránh mất dữ liệu nếu crash giữa chừng)
            if batch_cars:
                try:
                    df_batch = pd.DataFrame(batch_cars)
                    df_batch = clean_column_names(df_batch)

                    upload_to_bigquery(df_batch, table_id, if_exists="append")
                    upload_to_db(df_batch, table_name)

                    print(f"💾 Saved {len(df_batch)} records")
                except Exception as e:
                    print(f"❌ Save error: {e}")

            # cooldown giữa các batch
            sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"🕒 Cooling down {sleep_time:.1f}s...\n")
            await asyncio.sleep(sleep_time)

    print(f"\n📦 Total collected: {len(all_cars)}/{total_links}")

    return True