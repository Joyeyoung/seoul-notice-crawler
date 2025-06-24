import requests
from bs4 import BeautifulSoup
import json
import os
import subprocess

BASE_URL = "https://www.bizinfo.go.kr"
LIST_URL = f"{BASE_URL}/web/lay1/bbs/S1T122C128/AS/74/list.do"
PARAMS = {
    "rows": 15,
    "cpage": 1,
    "schWntyAt": "Y",
    "schAreaDetailCodes": "6450000",  # 서울 지역 코드
    "schEndAt": "Y"
}

def crawl_bizinfo():
    res = requests.get(LIST_URL, params=PARAMS)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    for row in soup.select(".table_list tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        title_tag = cols[1].find("a")
        items.append({
            "title": title_tag.text.strip(),
            "summary": f"{cols[2].text.strip()} 분야 공고",
            "status": cols[0].text.strip(),
            "category": cols[2].text.strip(),
            "period": cols[4].text.strip(),
            "url": BASE_URL + title_tag["href"]
        })

    with open("notices.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def git_commit_and_push():
    os.system('git config --global user.email "you@example.com"')
    os.system('git config --global user.name "Render Bot"')
    subprocess.run(["git", "add", "notices.json"])
    subprocess.run(["git", "commit", "-m", "자동 업데이트", "--allow-empty"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    crawl_bizinfo()
    git_commit_and_push()
