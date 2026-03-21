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

    print(f"✅ Found {total_links} links\n")

    semaphore = asyncio.Semaphore(random.randint(2, 4))

    connector = aiohttp.TCPConnector(
        limit=30,
        limit_per_host=10,
        ssl=False
    )

    async with aiohttp.ClientSession(
        timeout=TIMEOUT,
        connector=connector
    ) as session:

        await asyncio.sleep(random.uniform(1, 3))

        for batch_idx, batch_start in enumerate(range(0, total_links, BATCH_SIZE), start=1):
            batch = link_set[batch_start: batch_start + BATCH_SIZE]

            print(f"📦 Batch {batch_idx}: {len(batch)} links")

            tasks = [
                fetch_detail(session, parse_car_detail, link, idx, total_links, semaphore)
                for idx, link in enumerate(batch, batch_start + 1)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            batch_cars = [
                r for r in results
                if r and not isinstance(r, Exception)
            ]

            # 🔥 save ngay → không giữ RAM
            if batch_cars:
                try:
                    df = pd.DataFrame(batch_cars)
                    df = clean_column_names(df)

                    upload_to_bigquery(df, table_id, if_exists="append")
                    upload_to_db(df, table_name)

                    print(f"💾 Saved {len(df)} records")

                except Exception as e:
                    print(f"❌ Save error: {e}")

            print(f"📊 Success: {len(batch_cars)}/{len(batch)}")

            # cooldown
            sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"🕒 Sleep {sleep_time:.1f}s\n")
            await asyncio.sleep(sleep_time)

    print("\n🎉 DONE")
    return True