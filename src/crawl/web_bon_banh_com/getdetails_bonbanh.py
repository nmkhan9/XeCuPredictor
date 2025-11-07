import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
from src.utils.crawl_utils import fetch_detail
from src.utils.io_utils import read_links_from_file, upload_to_bigquery, clean_column_names
import pandas as pd
from configs import GCS_BUCKET_NAME,GCS_PROJECT_ID

BATCH_SIZE = 100      
MIN_DELAY, MAX_DELAY = 5, 10

BASE_DIR = Path(__file__).resolve().parents[3]
path_file = BASE_DIR / "data" / "links_bonbanh.txt"
table_id = f"{GCS_PROJECT_ID}.{GCS_BUCKET_NAME}.bonbanh_com"

def parse_car_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    specs = {}
    name_tag = soup.find("div", class_="title")
    name = name_tag.find_next("h1").get_text(strip=True) if name_tag else None
    specs["Name"] = name

    spec_section = soup.find("div", class_="box_car_detail")
    if spec_section:
        rows = spec_section.find_all("div", class_="row")
        for row in rows:
            label_div = row.find("div", class_="label")
            value_div = row.find("div", class_="txt_input")
            if label_div and value_div:
                label = label_div.get_text(strip=True).replace(":", "")
                value = value_div.get_text(strip=True)
                specs[label] = value
    return specs

async def crawl_details(path_file):
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

    print(f"\n📦 Total product details collected: {len(all_cars)}/{len(link_set)}")

    df = pd.DataFrame(all_cars)
    df = pd.DataFrame(all_cars)
    df = clean_column_names(df)
    print(df.head())
    upload_to_bigquery(df, table_id, if_exists="replace")

    return df


if __name__ == "__main__":
    asyncio.run(crawl_details(path_file))