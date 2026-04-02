# CLAUDE.md

## Project Overview

This is a mobile web application built with **Framework7** (v1.x), a full-featured HTML framework for building iOS and Android apps. The app uses Ajax-based page navigation and is structured as a PhoneGap/Cordova hybrid mobile app.

## Repository Structure

```
├── index.html          # Main entry point / home page (full HTML document)
├── about.html          # About page (Ajax partial - no <html>/<body> wrapper)
├── services.html       # Services page (Ajax partial)
├── form.html           # Form demo page (Ajax partial)
├── css/
│   ├── framework7.css      # Framework7 full CSS
│   ├── framework7.min.css  # Framework7 minified CSS (used in production)
│   └── my-app.css          # Custom app styles (currently empty)
├── js/
│   ├── framework7.js       # Framework7 full JS
│   ├── framework7.min.js   # Framework7 minified JS (used in production)
│   └── my-app.js           # Custom app initialization and logic
└── img/                    # Icons for form elements and app UI
```

## Key Architecture Decisions

- **Only `index.html` is a full HTML document.** All other pages (`about.html`, `services.html`, `form.html`) are partial HTML fragments loaded via Ajax by Framework7's router. They must NOT contain `<html>`, `<head>`, or `<body>` tags.
- **Page identification**: Each page fragment uses `data-page="pageName"` on its `.page` div. This name is used in `my-app.js` for page-specific event handling via the `pageInit` event.
- **Navigation**: Links between pages use standard `<a href="page.html">` tags. Framework7 intercepts these and loads content via Ajax. Back navigation uses the `.back` class.
- **Cordova/PhoneGap**: The app includes `cordova.js` for hybrid mobile deployment. This file is injected at build time and does not exist in the repo.

## Development Conventions

- **Framework7 v1.x API**: This project uses the legacy Framework7 v1 API. The app is initialized with `new Framework7()` and views are added with `myApp.addView()`. Do not use v2+ syntax.
- **Selector engine**: Use `Framework7.$` (aliased as `$$`) instead of jQuery for DOM manipulation.
- **Dynamic pages**: Created via `mainView.loadContent()` with HTML strings (see `createContentPage()` in `my-app.js`).
- **CSS**: Custom styles go in `css/my-app.css`. Do not modify `framework7.css` or `framework7.min.css`.
- **JS**: Custom logic goes in `js/my-app.js`. Do not modify `framework7.js` or `framework7.min.js`.

## Adding New Pages

1. Create a new `.html` file as an Ajax partial (no full document wrapper).
2. Include a navbar with a `.back` link and the page title.
3. Wrap content in `.pages > .page[data-page="pageName"] > .page-content`.
4. Add a navigation link in `index.html` or other pages.
5. If page-specific JS is needed, add a `pageInit` handler in `my-app.js` checking `page.name`.

## No Build System

This project has no build tools, package manager, or transpilation step. Files are served as-is. There are no tests, linters, or CI pipelines configured.

## Git Conventions

- The default branch is `master`.
- Commit messages have been informal/minimal. Use concise, descriptive messages for new commits.
