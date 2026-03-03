import asyncio
import random
import aiohttp
from src.utils.fetch_detail_utils import fetch_detail
from src.utils.io_utils import read_links_from_file, upload_to_bigquery, clean_column_names, upload_to_db
import pandas as pd

BATCH_SIZE = 200      
MIN_DELAY, MAX_DELAY = 5,7

async def crawl_details(path_file, parse_car_detail, table_id, table_name):
    link_set = read_links_from_file(path_file)
    print(f"✅ Found {len(link_set)} links in {path_file}\n")
    remaining_links = list(link_set)

    semaphore = asyncio.Semaphore(random.randint(3, 5))
    all_cars = []

    async with aiohttp.ClientSession() as session:
        for batch_start in range(0, len(remaining_links), BATCH_SIZE):
            batch = remaining_links[batch_start:batch_start + BATCH_SIZE]
            print(f"📦 Batch {batch_start//BATCH_SIZE + 1}: {len(batch)} links")

            tasks = [
                fetch_detail(session, parse_car_detail, link, i, len(remaining_links), semaphore)
                for i, link in enumerate(batch, batch_start + 1)
            ]
            results = await asyncio.gather(*tasks)
            batch_cars = [r for r in results if r]

            all_cars.extend(batch_cars)

            sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
            print(f"🕒 Cooling down {sleep_time:.1f}s...\n")
            await asyncio.sleep(sleep_time)
            if batch_cars:
                df_batch = pd.DataFrame(batch_cars)
                df_batch = clean_column_names(df_batch)
                upload_to_bigquery(df_batch, table_id, if_exists="append")
                upload_to_db(df_batch, table_name, if_exists="append")
                

    print(f"\n📦 Total product details collected: {len(all_cars)}/{len(link_set)}")

    return True

