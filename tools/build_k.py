# /k/<키>/ = 문자용 짧은 주소 → /sam2/ 의 그 가전 모음으로 넘김 (10-17 대표님 "주말 문자")
# 문자는 66자 안에 끝나야 해서(scripts/ads/sms_auto.py) sam2 긴 주소 대신 rentalmallra.co.kr/k/rf 처럼 보낸다.
# 사용: python3 tools/build_k.py   (키는 sms_auto.py K_LINK 와 같아야 한다)
import os
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = {"tv": ("TV", "TV"), "rf": ("냉장고", "냉장고"), "wm": ("세탁기", "세탁기·건조기"),
     "nb": ("노트북", "노트북"), "rc": ("로봇청소기", "로봇청소기")}  # 키: (sam2 검색어, 제목에 쓸 이름)

PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} 모음</title>
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url!r});</script>
</head><body><a href="{url}">{name} 모음 보기</a></body></html>
"""

for key, (q, name) in K.items():
    url = "/sam2/?" + urlencode({"q": q, "t": f"추천드리는 {name}"})
    d = os.path.join(ROOT, "k", key)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(PAGE.format(name=name, url=url))
    print(key, url)
