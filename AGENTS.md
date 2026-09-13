# AGENTS.md

Static GitHub Pages site — single `index.html` with embedded CSS/JS. No build step, no framework, no dependencies.

## Structure

- `index.html` — the entire site (HTML + CSS + JS, ~1250 lines)
- `assets/` — images (WebP) and the BGM
  - Scene backgrounds: `hero-farm.webp`, `night-farm.webp`, `field-mail.webp`, `sky-clouds.webp`, `stall.webp`, `path-seasons.webp`
  - Transparent pixel item sprites: `cake.webp`, `stardrop.webp`, `sword.webp`, `roses.webp`, `heart.webp`
  - `fonts/zpix-subset.woff2` — Chinese pixel font subset (12KB, only the glyphs used on this page)
  - `bgm.mp3` — "The Valley Comes Alive"
- `tools/subset-font.py` — regenerates the pixel font subset after copy changes
- `.gitignore` — 排除 `_font/`（源字库缓存，只为重裁子集用）和本地预览/截图临时文件
- `CNAME` — custom domain `meoworz.cn`
- `.nojekyll` — disables Jekyll processing
- `.github/workflows/deploy.yml` — GitHub Actions static deployment

## Deploy

Push to `main` → GitHub Actions auto-deploys. No manual build needed.

```bash
git add . && git commit -m "描述" && git push
```

Actions workflow: `.github/workflows/deploy.yml` (uses `actions/deploy-pages@v4`).

## Key details

- **Owner:** YiyuMeowzZ
- **Domain:** meoworz.cn (DNS via Cloudflare, 4 A records → GitHub Pages IPs)
- **Content:** Stardew Valley themed birthday page for 萱萱 (born 2005, turning 21). Scenes: 农场清晨 → 信箱 → 升级 Lv.21 → 四件礼物 → 四季 → 烟花
- **Audio:** `assets/bgm.mp3` via an `<audio>` element, autoplay with first-interaction fallback. Firework SFX is Web Audio API generated.

## Editing notes

- All CSS/JS is inline in `index.html` — no separate files
- Chinese content throughout — keep encoding UTF-8
- Scroll-snap paging: each `<section class="scene">` is `min-height: 100dvh`, `scroll-snap-align: start`, `scroll-snap-stop: always` (one gesture = one page). A JS wheel handler makes a single mouse-wheel notch flip exactly one page; touch devices use the native snap-stop.
- **每个 scene 的内容必须放得进一屏**。放不进时（`scrollHeight > innerHeight`）滚轮翻页会主动让位给原生滚动，但 `scroll-snap-stop` 会让它卡在页首，体验很差。
- Pixel art: every image uses `image-rendering: pixelated`
- Chinese pixel font: `assets/fonts/zpix-subset.woff2` (Zpix subset, 12KB) — **全站字体**，正文和大标题都用它；英文 HUD 标签另用 Press Start 2P。改动页面中文文案后必须重跑 `python tools/subset-font.py`，否则新字会回退到系统字体。源字体从 https://github.com/SolidZORO/zpix-pixel-font/releases 下载 `zpix.woff2` 放到 `_font/`（该目录不入库）
- 字号尽量取 12 的整数倍（36/48/60px），点阵块才是等大正方形；非整数倍时浏览器会把块渲染成 5px/6px 混合，颗粒不均
- **已知取舍**：Zpix 是 12×11 点阵，笔画多的字（如「萱」15 画）会丢笔画，且方舟像素（Ark Pixel 12px）渲染结果几乎相同，换字库无法解决。用户已知悉并接受。
- Fonts: Zpix (中文大标题，本地自托管) + Noto Sans SC (正文) + Press Start 2P (英文像素 HUD)，后两者走 Google Fonts CDN
- Autoplay policy: browsers block audio with sound before user interaction. The page calls `bgm.play()` on load and falls back to the first pointer/key event, with a `.music-hint` wooden chip nudging the user.
