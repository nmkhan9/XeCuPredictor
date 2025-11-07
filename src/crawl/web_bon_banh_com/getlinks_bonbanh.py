import asyncio
import aiohttp
import os
from utils.crawl_links_utils import crawl_links
from pathlib import Path

PAGE = 150

BASE_DIR = Path(__file__).resolve().parents[3]
path_store = BASE_DIR / "data" / "links_bonbanh.txt"
os.makedirs(os.path.dirname(path_store), exist_ok=True)

def getlink(soup):
    items = soup.find_all("li", class_=["car-item row1", "car-item row2"])
    links = []
    for item in items:
        a_tag = item.find("a", itemprop="url")
        if a_tag and a_tag.get("href"):
            link = "https://bonbanh.com/" + a_tag.get("href")
            links.append(link)
    return links

async def main():
    link_set = set()
    url_template = "https://bonbanh.com/oto/page,{}"

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, PAGE + 1):
            task = crawl_links(
                session=session,
                func_get_links=getlink,
                i=i,
                link_set=link_set,
                url_template=url_template,
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

    with open(path_store, "a", encoding="utf-8") as f: 
        for r in results:
            if isinstance(r, tuple):
                links, _, _ = r
                for link in sorted(set(links)):  
                    if link not in link_set:    
                        f.write(link + "\n")
                        f.flush()
                        link_set.add(link)

    print(f"\n📦 Tổng số link thu được: {len(link_set)}")
    print(f"📁 Đã lưu tại: {path_store}")

if __name__ == "__main__":
    asyncio.run(main())
