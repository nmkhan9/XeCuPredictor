import asyncio
import os
from src.utils.crawl_links_utils import crawl_more_links
from pathlib import Path

PAGE = 150
url_template = "https://www.carmudi.vn/xe-o-to/?page={}&last_page=187"

BASE_DIR = Path(__file__).resolve().parents[3]
path_store = BASE_DIR / "data" / "links_carmudi.txt"
os.makedirs(os.path.dirname(path_store), exist_ok=True)

def getlink(soup):
    items = soup.find_all("div", class_="carmudi-listing-item listingItem2")
    links = []
    for item in items :
        link_tag = item.find("div",class_="w-full h-full relative")
        if link_tag:
            link = "https://www.carmudi.vn" + link_tag.find_next("a")["href"]
            links.append(link)
    return links


if __name__ == "__main__":
    asyncio.run(crawl_more_links(url_template, PAGE, getlink, path_store))
