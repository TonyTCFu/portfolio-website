# Project Rules & Guidelines - 傅天君 Tony Fu 个人网站 (Portfolio Website)

This document outlines the project-wide coding standards, design philosophy, and guidelines for Tony Fu's personal website.

---

## 1. Project Overview & Architecture

* **Project Name**: 傅天君 Tony Fu 个人网站 (Personal Portfolio & Practice Portal)
* **Date Created / Initialized**: 2026-09-22
* **Tech Stack**:
  * Semantic HTML5 with bilingual presentation (Chinese primary, English subtitles via `.en-text`).
  * Vanilla Modern CSS3 (CSS custom properties, Glassmorphism, Dark/Light mode theme switching, Grid/Flexbox layouts).
  * Vanilla JavaScript (ES6+, DOM manipulation, IntersectionObserver for scroll reveals, theme management via `localStorage`).
  * Cloudflare Pages static hosting / GitHub repository sync (`TonyTCFu/portfolio-website`).

---

## 2. Directory Structure

```text
portfolio-website/
├── index.html               # Main homepage containing Hero, About, Projects, Podcast, Contact
├── style.css                # Global styles, variables, typography, component layouts
├── script.js                # Interaction scripts, theme toggle, mobile navigation
├── _headers                 # Cloudflare Pages HTTP security and caching headers
├── dashboard/               # Antigravity Taiwan Stock Quant Model Dashboard
├── ark/                     # ARK Tracker and daily research notes
├── assets & icons (*.png, *.gif, *.svg)
├── AGENTS.md                # Project standards & guidelines
└── MEMORY.md               # Architecture decisions, history, and operational memory
```

---

## 3. Coding & Design Standards

1. **Design Integrity**:
   * Adhere strictly to the established Glassmorphism dark-cyber aesthetic (cyan `#00d2ff`, magenta/purple `#d946ef`, glass cards with backdrop blur).
   * Ensure light mode compatibility via `[data-theme="light"]` variables.
2. **Bilingual Presentation**:
   * Core section headings and key project titles must feature Chinese with clean English translation subtitles (`.en-text`).
3. **Typography & Icons**:
   * Fonts: Quicksand, M PLUS Rounded 1c.
   * Icons: Inline SVGs or optimized PNGs with explicit dimensions and alt tags.
4. **Performance & Cleanliness**:
   * Zero heavy external UI frameworks (no React/Tailwind runtime overhead); keep pages lightweight, lightning fast, and fully responsive across mobile, tablet, and desktop screens.
   * No broken links or placeholder mockups that degrade user credibility.

---

## 4. Verification & Testing

* Always inspect rendered HTML syntax and responsive behavior.
* Verify dark and light themes render with appropriate contrast and readability.
* Ensure all navigation links, external podcast platforms, and project anchors function accurately.
