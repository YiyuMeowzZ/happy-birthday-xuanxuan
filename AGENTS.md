# AGENTS.md

Static GitHub Pages site — single `index.html` with embedded CSS/JS. No build step, no framework, no dependencies.

## Structure

- `index.html` — the entire site (HTML + CSS + JS, ~1250 lines)
- `assets/` — images (WebP) and the BGM
  - Scene backgrounds: `hero-farm.webp`, `night-farm.webp`, `field-mail.webp`, `sky-clouds.webp`, `stall.webp`, `path-seasons.webp`
  - Transparent pixel item sprites: `cake.webp`, `stardrop.webp`, `sword.webp`, `roses.webp`, `heart.webp`
  - `fonts/zpix-subset.woff2` — Chinese pixel font subset (12KB, only the glyphs used on this page)
  - `fonts/press-start-2p-subset.woff2` — Latin pixel font subset (20KB, ASCII only)
  - `bgm.mp3` — "The Valley Comes Alive" (4:22, 128kbps stereo, ~4MB)
- `tools/subset-font.py` — regenerates both font subsets after copy changes
- `.gitignore` — 排除 `_*`（`_font/` 源字库缓存 + 本地预览/截图/测试临时文件）
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
- Scroll-snap paging: each `<section class="scene">` is `min-height: 100dvh`, `scroll-snap-align: start`, `scroll-snap-stop: always`. 但**翻页不依赖 CSS**：`wheel` 处理一格一页，`touchstart/touchmove/touchend` 处理一次滑动一页。
- **触屏为什么不用 `scroll-snap-stop`**：iOS 的惯性滚动会直接冲过吸附点、一次滑好几页。所以 `touchmove`（**必须显式 `{passive:false}`**，Chrome 对 window 上的 touchmove 默认 passive，那样 `preventDefault` 无效）里判断手势后拦掉原生滚动并翻一页；一次手势只翻一次，后续移动全部吞掉，避免原生滚动和 smooth 翻页同时生效。
- **每个 scene 的内容必须放得进一屏**。放不进时（`scrollHeight > innerHeight`）滚轮和触摸都会主动让位给原生滚动（滚到边界才翻页），但 `scroll-snap-stop` 会让它卡在页首，体验很差。
- Pixel art: every image uses `image-rendering: pixelated`
- Chinese pixel font: `assets/fonts/zpix-subset.woff2` (Zpix subset, 12KB) — **全站字体**，正文和大标题都用它；英文 HUD 标签另用 Press Start 2P。改动页面中文文案后必须重跑 `python tools/subset-font.py`，否则新字会回退到系统字体。源字体放到 `_font/`（该目录不入库）：Zpix 从 https://github.com/SolidZORO/zpix-pixel-font/releases 下 `zpix.woff2`，Press Start 2P 从 https://github.com/google/fonts/tree/main/ofl/pressstart2p 下 `PressStart2P-Regular.ttf`。脚本会一次把两个子集都重裁。
- 字号尽量取 12 的整数倍（36/48/60px），点阵块才是等大正方形；非整数倍时浏览器会把块渲染成 5px/6px 混合，颗粒不均
- **已知取舍**：Zpix 是 12×11 点阵，笔画多的字（如「萱」15 画）会丢笔画，且方舟像素（Ark Pixel 12px）渲染结果几乎相同，换字库无法解决。用户已知悉并接受。
- Fonts: Zpix (中文，本地子集) + Press Start 2P (英文 HUD，本地子集)。**两者都自托管，页面零第三方请求**——原来用 Google Fonts 的 `@import`，那是阻塞渲染的第三方请求且国内经常很慢，已移除。
- Autoplay policy: browsers block audio with sound before user interaction. `scheduleAutoPlay()` 在 `load` 之后延迟 600ms 调用 `bgm.play()`，被拦时由 `.music-hint` 木牌提示、首次交互即播。
- **性能红线（改动时别破坏）**：
  - `<audio>` 必须是 `preload="none"`。`preload="auto"` 会让 4MB 的 mp3 在首屏就开始下载，是"打开很慢"的头号原因。实测：自动播放被拦时浏览器根本不会去下这个文件。
  - 5 个非首屏背景图的 URL 放在元素的 `data-bg` 上（CSS 里不出现 url），由 `deferBackgrounds()` 在 `load` 之后 300ms 统一挂载。首屏只加载 `hero-farm.webp`（另有 `<link rel=preload>`）。
  - 非首屏 `<img>` 都带 `loading="lazy" decoding="async"`。
  - 实测首屏关键路径约 250KB（原来约 4.8MB）。改动后请用带访问日志的本地服务复核请求顺序，不要凭感觉。
