import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from configs import GCS_BUCKET_NAME,GCS_PROJECT_ID
from src.utils.crawl_details_utils import crawl_details


BASE_DIR = Path(__file__).resolve().parents[3]
path_file = BASE_DIR / "data" / "links_carmudi.txt"
table_id = f"{GCS_PROJECT_ID}.{GCS_BUCKET_NAME}.carmudi_vn"

def parse_car_detail(html):
    soup = BeautifulSoup(html, "html.parser")
    car_info = {}
    
    info_tag = soup.find("div", class_="flex flex-col gap-4 md:gap-6")
    if  info_tag:
        name_tag = info_tag.find("h1", class_="text-lg")
        if name_tag:
            car_info["Name"] = name_tag.get_text(strip=True)

        price_tag = info_tag.find("h3", class_="text-lg")
        if price_tag:
            car_info["Price"] = price_tag.get_text(strip=True)
        in41 = soup.find_all("p", class_="flex-grow")
        for key_tag in in41:
            key = key_tag.get_text(strip=True)
            val_tag = key_tag.find_next("p")
            val = val_tag.get_text(strip=True) if val_tag else None
            if key and val:
                car_info[key] = val
        
        in42 = soup.find_all("span", class_="max-w-[60%]")
        for key_tag1 in in42:
            key1 = key_tag1.get_text(strip=True)
            val_tag1 = key_tag1.find_next("span")
            val1 = val_tag1.get_text(strip=True) if val_tag else None
            if key1 and val1:
                car_info[key1] = val1

    return car_info

if __name__ == "__main__":
    asyncio.run(crawl_details(path_file, parse_car_detail, table_id))