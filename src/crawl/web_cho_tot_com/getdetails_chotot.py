import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from configs import GCS_BUCKET_NAME,GCS_PROJECT_ID
from src.utils.crawl_details_utils import crawl_details


BASE_DIR = Path(__file__).resolve().parents[3]
path_file = BASE_DIR / "data" / "links_chotot.txt"
table_id = f"{GCS_PROJECT_ID}.{GCS_BUCKET_NAME}.chotot_com"

def parse_car_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    specs = {}
    
    name_tag = soup.find("div", class_="r9vw5if")
    if not name_tag:
        return None
    
    name = name_tag.find_next("h1").get_text(strip=True)
    if not name:
        return None
    price_tag = soup.find("b", class_="p26z2wb")
    price = price_tag.get_text(strip=True) if price_tag else None

    specs["name"] = name
    specs["price"] = price


    details = soup.find_all("div", class_="p1ja3eq0")
    for detail in details:
        key_tag = detail.find("span", class_="bwq0cbs")
        if key_tag:
            key = key_tag.get_text(strip=True)
            value_tag = key_tag.find_next("span", class_="bwq0cbs")
            value = value_tag.get_text(strip=True) if value_tag else None
            specs[key] = value

if __name__ == "__main__":
    asyncio.run(crawl_details(path_file, parse_car_detail, table_id))