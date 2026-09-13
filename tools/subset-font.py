"""只保留页面里实际用到的字形，把 Zpix 裁成小体积 webfont。

用法:
    python tools/subset-font.py

依赖: pip install fonttools brotli
源字体从 https://github.com/SolidZORO/zpix-pixel-font/releases 下载 zpix.woff2
放到 _font/zpix.woff2（该目录不入库）。改动页面文案后需要重新跑一次。
"""

import os
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
def find_source() -> str:
    """源字体可能是 woff2 或 ttf，两个都找一下。"""
    for name in ("zpix.woff2", "zpix.ttf", "Zpix.ttf"):
        p = os.path.join(ROOT, "_font", name)
        if os.path.exists(p):
            return p
    return os.path.join(ROOT, "_font", "zpix.woff2")


SRC = find_source()
OUT = os.path.join(ROOT, "assets", "fonts", "zpix-subset.woff2")

EXTRA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" \
        "：，。！？、；·「」（）-—/→+∞♪♫·&*"


def visible_text(html: str) -> str:
    body = re.sub(r"<style[\s\S]*?</style>", "", html)
    body = re.sub(r"<script[\s\S]*?</script>", "", body)
    body = re.sub(r"<!--[\s\S]*?-->", "", body)
    body = re.sub(r"<[^>]+>", "", body)
    return body


def main() -> int:
    if not os.path.exists(SRC):
        print(f"缺少源字体: {SRC}\n先从 zpix 的 release 下载 zpix.woff2 放到这里。")
        return 1

    chars = set(c for c in visible_text(open(HTML, encoding="utf-8").read()) if not c.isspace())
    chars |= set(EXTRA)
    text = "".join(sorted(chars))

    font = TTFont(SRC)
    cmap = font.getBestCmap()
    missing = [c for c in sorted(chars) if ord(c) not in cmap]
    if missing:
        print(f"警告：字库里没有这些字，会回退到系统字体: {''.join(missing)}")

    options = Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    sub = Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    font.save(OUT)
    print(f"字数 {len(text)} -> {OUT}  {os.path.getsize(OUT) // 1024}KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
