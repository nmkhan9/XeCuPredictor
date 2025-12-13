import asyncio
import os
from src.utils.crawl_links_utils import crawl_more_links
from pathlib import Path

PAGE = 500
url_template = "https://oto.com.vn/mua-ban-xe/p{}"

BASE_DIR = Path(__file__).resolve().parents[3]
path_store = BASE_DIR / "data" / "links_oto.txt"
os.makedirs(os.path.dirname(path_store), exist_ok=True)

def getlink(soup):
    items = soup.find_all("h3", class_="title")
    links = []
    for item in items:
        a_tag = item.find("a")
        if a_tag and a_tag.get("href"):
            link = "https://oto.com.vn" + a_tag["href"]
            links.append(link)
    return links


if __name__ == "__main__":
    asyncio.run(crawl_more_links(url_template, PAGE, getlink, path_store))