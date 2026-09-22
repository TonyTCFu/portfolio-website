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
  * **Projects / AI Practice Notes**: Real automation and research implementations.
  * **Podcast Section**: Added "Tony的跨界笔记" (Tony's Cross-Border Notes), highlighting multi-platform availability (Apple Podcasts, Spotify, 小宇宙, 喜马拉雅).
  * **Contact & Social**: Email, locations (Shanghai & Taipei), direct feedback form.

---

## 2. Maintenance & Deployment Notes

* Static files are deployed via Git push to `origin/main` (`TonyTCFu/portfolio-website`).
* Cloudflare Pages handles automated continuous deployment.
* Asset caching: Use cache-busting query strings (e.g. `?v=YYYYMMDDHHMMSS`) on CSS and JS references when publishing updates.
