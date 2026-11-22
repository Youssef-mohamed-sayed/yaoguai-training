# Yaoguai Linux

Yaoguai Linux is a responsive, browser-local learning platform for the existing Linux Essentials course. It turns the Markdown course in `linux-essentials/` into a navigable learning path with lesson search, code examples, and persistent local progress. Its dark surfaces, deep red accents, Japanese-influenced typography, emblem, and compact navigation are adapted from the sibling Yaoguai Crypto project.

## Features

- Build-time discovery of numbered course modules, Markdown lessons, and lesson assets.
- Course dashboard, module overview, lesson reader, generated table of contents, and previous/next navigation.
- Search across module names, lesson titles, headings, and lesson text.
- Sanitized Markdown rendering, syntax highlighted code, copy buttons, tables, checklists, callouts, and safe local links.
- Browser-local completed lessons and last-accessed lesson, with course/module progress and Continue Learning.
- Responsive navigation drawer on mobile, scrollable code and tables, keyboard-accessible controls, and visible focus states.
- No account, authentication, API, or database requirement.

## Technology

- Vite and vanilla JavaScript (ES modules)
- Marked for Markdown parsing, DOMPurify for HTML sanitization, and Highlight.js for code highlighting
- Plain CSS design tokens adapted from Yaoguai Crypto

## Project structure

```text
Yaoguai-Linux/
├── index.html                 # Vite application entry
├── src/
│   ├── main.js                # Routing, course UI, search, and progress
│   └── style.css              # Design tokens, components, and responsive layouts
├── scripts/
│   └── build-course.js        # Discovers Markdown and packages course assets
├── public/
│   ├── assets/                # Yaoguai emblem, favicon, and bundled fonts
│   └── course-data.json       # Generated during build; intentionally ignored by Git
├── linux-essentials/          # Source of truth for course Markdown and assets
├── package.json
└── vercel.json
```

The Crypto reference remains a separate sibling project and is not needed to build or run Yaoguai Linux. Its fonts and emblem used by this app are copied into `public/assets/`.

## Run locally (Windows PowerShell)

Install Node.js 20 or newer, then run from the repository root:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`).

## Build and preview

```powershell
npm run build
npm run preview
npm test
```

`npm run build` first scans `linux-essentials/` and writes a generated `public/course-data.json` plus copied lesson assets under `public/course-assets/`. Vite then packages these files in `dist/`. Generated data, `dist/`, dependencies, environment files, and Vercel's local linkage are ignored by Git.

`npm test` rebuilds the generated course index and runs the built-in Node test suite. It checks module and lesson discovery, Markdown source preservation, asset packaging, and course overview/reference content without adding a separate test framework.

## Course content discovery

The build script reads the root `linux-essentials/README.md`, discovers child directories as modules, and sorts their existing numeric prefixes naturally. Within a module it discovers Markdown files other than `README.md` as lessons and sorts those filenames the same way. Module titles and descriptions come from each module's `README.md`; lesson titles come from the first Markdown heading, falling back to the filename. Non-Markdown files are copied while retaining their relative paths so local lesson links and assets can be resolved without exposing filesystem paths to the browser.

### Add a module

1. Create a naturally numbered directory, for example `16-new-topic/`.
2. Add `README.md` with a title, description, objectives, and lesson links.
3. Add one or more numbered Markdown lesson files.
4. Run `npm run build` and check the module in the generated curriculum.

### Add a lesson

1. Add a numbered `.md` file to the correct module, for example `03-next-topic.md`.
2. Start it with a descriptive `#` heading. Existing content and relative links remain the source of truth.
3. Put images or other downloadable assets alongside the lesson or under a module subdirectory, and use relative Markdown links.
4. Run `npm run build`; the lesson, search index, navigation, and counts are regenerated automatically.

No frontend lesson arrays need editing. Use numeric prefixes to establish the intended module and lesson order.

## Progress and privacy

Completed lesson IDs and the last accessed lesson are stored in `localStorage` under `yaoguai-linux:progress:v1`. Module and course totals are derived from the discovered lesson list. Continue Learning opens the last accessed lesson if it remains incomplete, otherwise the next incomplete lesson. Reset is available from the course navigation and asks for confirmation. Progress belongs only to the current browser profile and device; it does not sync between users or devices. Clearing browser storage also clears this progress.

## Vercel deployment

Import `https://github.com/Youssef-mohamed-sayed/yaoguai-linux` as a Vercel project. The checked-in `vercel.json` selects the Vite framework, runs `npm run build`, publishes `dist/`, and rewrites application routes to `index.html`. Vercel serves existing generated course JSON, lesson assets, fonts, and images as static files. No environment variables, database, or server function are required. Deploy after committing the project; direct lesson and module URLs are handled by the SPA rewrite.

## GitHub

The target directory is configured with the `origin` remote `https://github.com/Youssef-mohamed-sayed/yaoguai-linux.git`. No commit or push is made automatically. After reviewing your changes, push the initial branch with:

```powershell
git add .
git commit -m "Build Yaoguai Linux learning platform"
git branch -M main
git push -u origin main
```
