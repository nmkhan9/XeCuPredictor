import asyncio
import os
from src.utils.crawl_links_utils import crawl_more_links
from pathlib import Path

url_template = "https://www.carmudi.vn/xe-o-to/?page={}"

BASE_DIR = Path(__file__).resolve().parents[3]
path_store = BASE_DIR / "data" / "links_carmudi.txt"
os.makedirs(os.path.dirname(path_store), exist_ok=True)

def getlink(soup):
    items = soup.find_all('div', class_='carmudi-listing-item')
    links = []
    for item in items:
        a_tag = item.find_next("a")
        if a_tag and a_tag.get("href"):
            link = "https://www.carmudi.vn" + a_tag.get("href")
            links.append(link)
    return links


if __name__ == "__main__":
    asyncio.run(crawl_more_links(url_template, getlink, path_store, PAGE=100))