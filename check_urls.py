import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
urls = [
    ("gjdxy", "https://gjdxy.sxist.edu.cn/jyjx/zysz.htm"),
    ("nyxy", "https://nyxy.sxist.edu.cn/jyjx/zysz.htm"),
    ("hgxy", "https://hgxy.sxist.edu.cn/jyjx/zysz.htm"),
    ("jjglxy", "https://jjglxy.sxist.edu.cn/jyjx/zysz.htm"),
]
for name, url in urls:
    try:
        r = requests.get(url, timeout=15, headers=headers)
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        el = soup.select_one(".ywc_listR")
        if el:
            print(f"{name}: OK - {el.get_text(strip=True)[:150]}")
        else:
            body = soup.body.get_text(strip=True)[:200] if soup.body else "no body"
            print(f"{name}: no ywc_listR, body={body}")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
    print()
print("DONE")
