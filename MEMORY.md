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
    * Added `Dr eggbot / GrokBot 智能协同中枢` as the featured full-width card (`featured-full`) on desktop (swapped position with Taiwan Stock Quant model). Features a high-fidelity animated GIF (`grokbot-demo.gif`) simulating a conversational multi-agent Chief of Staff workspace (scheduling market research, coordinating podcast bots, and syncing Antigravity quant loops). Fictionalized dialogue protects personal privacy. Bottom badges updated to `GrokBot` (official red droplet icon), `Codex`, and `Antigravity`.
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
