import requests
from bs4 import BeautifulSoup
import json
import re
import subprocess
import os

BASE_URL = "https://www.bizinfo.go.kr"
LIST_URL = f"{BASE_URL}/web/lay1/bbs/S1T122C128/AS/74/list.do"
PARAMS = {
    "rows": 15,
    "cpage": 1,
    "schWntyAt": "Y",
    "schAreaDetailCodes": "6450000",
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
            onclick = title_tag.get("onclick", "")
            match = re.search(r"pblancId='(.*?)'", onclick)
            if not match:
                continue
            pblanc_id = match.group(1)
            detail_url = f"{BASE_URL}/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId={pblanc_id}"

            all_items.append({
                "title": title_tag.text.strip(),
                "summary": f"{cols[2].text.strip()} 분야 공고",
                "status": cols[0].text.strip(),
                "category": cols[2].text.strip(),
                "period": cols[4].text.strip(),
                "url": detail_url
            })

        page += 1

    with open("notices.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

def git_commit_and_push():
    # GitHub 토큰을 환경 변수에서 읽기
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        return

    # GitHub 주소에 토큰 포함
    repo = "Joyeyoung/seoul-notice-site"
    remote_url = f"https://{token}@github.com/{repo}.git"

    subprocess.run(["git", "config", "--global", "user.email", "render@bot.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])

    subprocess.run(["git", "remote", "set-url", "origin", remote_url])
    subprocess.run(["git", "add", "notices.json"])
    subprocess.run(["git", "commit", "-m", "자동 업데이트", "--allow-empty"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    crawl_all_pages()
    git_commit_and_push()
