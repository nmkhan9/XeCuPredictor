import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from configs import GCS_BUCKET_NAME,GCS_PROJECT_ID
from src.utils.crawl_details_utils import crawl_details


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

if __name__ == "__main__":
    asyncio.run(crawl_details(path_file, parse_car_detail, table_id))