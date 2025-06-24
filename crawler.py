import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.bizinfo.go.kr"
LIST_URL = f"{BASE_URL}/web/lay1/bbs/S1T122C128/AS/74/list.do"

PARAMS = {
    "rows": 15,
    "cpage": 1,
    "schWntyAt": "Y",
    "schAreaDetailCodes": "6450000",  # 서울 지역
    "schEndAt": "Y"
}

def crawl_all_pages():
    all_items = []
    page = 1

    while True:
        PARAMS["cpage"] = page
        res = requests.get(LIST_URL, params=PARAMS)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select(".table_list tbody tr")
        if not rows or "등록된 데이터가 없습니다" in soup.text:
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            title_tag = cols[1].find("a")
            all_items.append({
                "title": title_tag.text.strip(),
                "summary": f"{cols[2].text.strip()} 분야 공고",
                "status": cols[0].text.strip(),
                "category": cols[2].text.strip(),
                "period": cols[4].text.strip(),
                "url": BASE_URL + title_tag["href"]
            })

        page += 1

    with open("notices.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    crawl_all_pages()
