# Long-term Memory - 傅天君 Tony Fu 个人网站 (Portfolio Website)

This document records architectural decisions, major design iterations, and maintenance notes for the portfolio website.

---

## 1. Architectural Decisions & Key Iterations

* **Glassmorphism & Dual Theme Support**:
  * Adopted a custom glassmorphism design system using CSS variables (`--bg-color`, `--card-bg`, `--glass-border`, `--primary-color`).
  * Default theme is `dark` with glowing cyan/purple orbs, with a clean `light` mode toggle persisted in `localStorage`.
* **Sub-application Integration**:
  * `/dashboard/`: Antigravity Taiwan Stock Quant Model real-time dashboard.
  * `/ark/`: ARK Investment Tracking and research daily notes.
* **Content Organization**:
  * **Hero**: Executive profile (30-year multinational corporate executive ✕ 喜欢折腾新科技的动手派). Tone is relaxed, grounded, conversational, and personal ("管了 30 多年跨国公司，退休后我没闲着，彻底玩起了 AI... 建这个小站，就是想交个朋友，轻松聊聊新科技").
  * **About / Strengths**: Approachable narrative ("退而不休，换个方式玩科技"); conversational tone describing hands-on coding, Taiwan stock quant model, multi-agent bot workflows, cross-border eCommerce, and "Tony's Lab" podcast. Categorized into 3 natural pillars: 常用的 AI 工具箱, 平时在折腾的事, 过去 30 年积累.
  * **Projects / AI Practice Notes**:
    * Added `Dr eggbot / GrokBot 智能协同中枢` as the featured full-width card (`featured-full`) on desktop (swapped position with Taiwan Stock Quant model). Features a high-fidelity animated GIF (`grokbot-demo.gif`) simulating a conversational multi-agent Chief of Staff workspace (scheduling market research, coordinating podcast bots, and syncing Antigravity quant loops). Fictionalized dialogue protects personal privacy. Bottom badges updated to authentic `GrokBot` App icon (black squircle with 3D white dome character and diagonal capsule eyes), `Codex`, and `Antigravity`.
    * Added Antigravity Taiwan Stock Quant Model, Open Claw Scraper, AI Task Orchestrator, and Obsidian Personal Wiki.
  * **Podcast Section ("Tony的跨界笔记 / Tony's Lab")**:
    * Strictly corrected topic positioning: Does NOT cover corporate management history; focused 100% on global tech news, frontier AI shifts, visionary reports (ARK Big Ideas, Dario Amodei, Cybercab, GPT-6), biopharma breakthroughs, longevity medicine, and cross-border insights.
    * English branding established as `Tony's Lab`.
    * Kept section evergreen by intentionally removing hard-coded episode lists, directing listeners seamlessly to Apple Podcasts, Spotify, 小宇宙, and 喜马拉雅.
  * **Contact & Social**: Email, locations (Shanghai & Taipei), direct feedback form.

---

## 2. Maintenance & Deployment Notes

* Static files are deployed via Git push to `origin/main` (`TonyTCFu/portfolio-website`).
* Cloudflare Pages handles automated continuous deployment.
* Asset caching: Use cache-busting query strings (e.g. `?v=YYYYMMDDHHMMSS`) on CSS and JS references when publishing updates.
