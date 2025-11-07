import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
from src.utils.crawl_utils import fetch_detail
from src.utils.io_utils import read_links_from_file, upload_to_bigquery, clean_column_names
import pandas as pd
from configs import GCS_BUCKET_NAME,GCS_PROJECT_ID

BASE_DIR = Path(__file__).resolve().parents[3]
path_file = BASE_DIR / "data" / "links_oto.txt"
table_id = f"{GCS_PROJECT_ID}.{GCS_BUCKET_NAME}.oto_com"

def parse_car_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    car_info = {}

    name_tag = soup.find("div", class_="group-title-detail")
    name = name_tag.find_next("h1", class_="title-detail").get_text(strip=True) if name_tag else None
    car_info["Name"] = name

    price_tag = soup.find("span", class_="price")
    price = price_tag.get_text(strip=True) if price_tag else None
    car_info["Price"] = price

    labels = soup.find_all("label", class_="label")
    for label in labels:
        key = label.get_text(strip=True)
        value_node = label.find_next_sibling(string=True)
        if not value_node or value_node.strip() == "":
            div = label.find_next("div")
            value = div.get_text(strip=True) if div else "N/A"
        else:
            value = value_node.strip()
        car_info[key] = value

    return car_info

async def crawl_details(path_file):
    link_set = read_links_from_file(path_file)
    print(f"✅ Found {len(link_set)} links in {path_file}\n")

    semaphore = asyncio.Semaphore(random.randint(3, 5))
    all_cars = []

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_detail(session, parse_car_detail, link, i, len(link_set), semaphore)
            for i, link in enumerate(link_set, 1)
        ]
        results = await asyncio.gather(*tasks)
        all_cars = [r for r in results if r is not None]

    print(f"\n📦 Total product details collected: {len(all_cars)}/{len(link_set)}")

    df = pd.DataFrame(all_cars)
    df = pd.DataFrame(all_cars)
    df = clean_column_names(df)
    print(df.head())
    upload_to_bigquery(df, table_id, if_exists="replace")

    return df


if __name__ == "__main__":
    asyncio.run(crawl_details(path_file))