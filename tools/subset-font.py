"""把页面用到的字体裁成小体积 webfont。

用法:
    python tools/subset-font.py

依赖: pip install fonttools brotli

两个字体：
1. Zpix（中文像素字）—— 从页面可见文案里收集用到的字，输入 `_font/zpix.woff2`
   或 `_font/zpix.ttf`，输出 `assets/fonts/zpix-subset.woff2`
2. Press Start 2P（拉丁像素字，用于 .px-tag 那类英文标签）—— 输入
   `_font/PressStart2P.ttf`，输出 `assets/fonts/press-start-2p-subset.woff2`

源字体都不入库（`_font/` 被 .gitignore 排除）。下载地址：
- zpix:          https://github.com/SolidZORO/zpix-pixel-font/releases
- Press Start 2P: https://github.com/google/fonts/tree/main/ofl/pressstart2p

**改动页面文案后要重新跑一次**，否则新字不在子集里、会掉回系统字体。
"""

import os
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
FONT_DIR = os.path.join(ROOT, "_font")
OUT_DIR = os.path.join(ROOT, "assets", "fonts")

# 页面里出现在 HTML 属性/JS 字符串里、但不是"可见正文"的字符，手动补上
EXTRA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" \
        "：，。！？、；·「」（）-—/→+∞♪♫·&*"

# Press Start 2P 是纯拉丁字，按 ASCII 可打印区整段保留，省得漏字；顺带带上中点
LATIN_RANGE = "".join(chr(c) for c in range(0x20, 0x7F)) + "·×"


def visible_text(html: str) -> str:
    body = re.sub(r"<style[\s\S]*?</style>", "", html)
    body = re.sub(r"<script[\s\S]*?</script>", "", body)
    body = re.sub(r"<!--[\s\S]*?-->", "", body)
    body = re.sub(r"<[^>]+>", "", body)
    return body


def find_source(*names: str) -> str:
    for name in names:
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return p
    return os.path.join(FONT_DIR, names[0])


def subset(src: str, out: str, text: str, label: str) -> bool:
    if not os.path.exists(src):
        print(f"[跳过] {label}: 缺少源字体 {src}")
        return False

    font = TTFont(src)
    cmap = font.getBestCmap()
    missing = [c for c in sorted(set(text)) if ord(c) not in cmap]
    if missing:
        print(f"  {label} 字库里没有这些字，会回退到系统字体: {''.join(missing)}")

    options = Options()
    options.flavor = "woff2"
    options.desubroutinize = True
    sub = Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    font.save(out)
    print(f"  {label}: {len(set(text))} 字 -> {os.path.relpath(out, ROOT)}  "
          f"{os.path.getsize(out) // 1024}KB  (源 {os.path.getsize(src) // 1024}KB)")
    return True


def main() -> int:
    html = open(HTML, encoding="utf-8").read()

    cjk_chars = set(c for c in visible_text(html) if not c.isspace()) | set(EXTRA)
    print("裁剪字体子集：")
    ok1 = subset(find_source("zpix.woff2", "zpix.ttf", "Zpix.ttf"),
                 os.path.join(OUT_DIR, "zpix-subset.woff2"),
                 "".join(sorted(cjk_chars)), "Zpix 中文")
    ok2 = subset(find_source("PressStart2P.ttf", "PressStart2P-Regular.ttf"),
                 os.path.join(OUT_DIR, "press-start-2p-subset.woff2"),
                 LATIN_RANGE, "Press Start 2P 拉丁")

    if not (ok1 or ok2):
        print("\n两个源字体都没找到，先从各自的 release / 仓库下到 _font/ 里。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
