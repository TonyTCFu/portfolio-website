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
  * **Hero**: Executive profile (30-year corporate leader ✕ AI enthusiast).
  * **About / Strengths**: Executive leadership & familiar AI tool stacks (Codex, Antigravity, Claude Code, Open Claw, Hermes, Grok).
  * **Projects / AI Practice Notes**:
    * Added `Dr eggbot / GrokBot 智能协同中枢` with high-fidelity multi-agent IM chat vector illustration (`grokbot-demo.svg`) reflecting real Chief of Staff workflows coordinating Podcast bots and Antigravity quant loops.
    * Added Antigravity Taiwan Stock Quant Model, Open Claw Scraper, AI Task Orchestrator, and Obsidian Personal Wiki.
  * **Podcast Section ("Tony的跨界笔记")**:
    * Strictly corrected topic positioning: Does NOT cover corporate management history; focused 100% on global tech news, frontier AI shifts, visionary reports (ARK Big Ideas, Dario Amodei, Cybercab, GPT-6), biopharma breakthroughs, longevity medicine, and cross-border insights.
    * Embedded 10 featured episodes (EP01-EP10) with duration and key takeaways.
    * Multi-platform access: Apple Podcasts, Spotify, 小宇宙 (Xiaoyuzhou), 喜马拉雅 (Ximalaya).
  * **Contact & Social**: Email, locations (Shanghai & Taipei), direct feedback form.

---

## 2. Maintenance & Deployment Notes

* Static files are deployed via Git push to `origin/main` (`TonyTCFu/portfolio-website`).
* Cloudflare Pages handles automated continuous deployment.
* Asset caching: Use cache-busting query strings (e.g. `?v=YYYYMMDDHHMMSS`) on CSS and JS references when publishing updates.
