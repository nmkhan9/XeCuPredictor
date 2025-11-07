import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from src.utils.crawl_details_utils import crawl_details
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

if __name__ == "__main__":
    asyncio.run(crawl_details(path_file, parse_car_detail, table_id))