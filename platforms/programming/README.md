# Yaoguai Programming

A responsive, no-account Python learning platform in the Yaoguai visual family. The course progresses from Python fundamentals to practical problem solving, debugging, networking, and safe cybersecurity-oriented scripts.

The course source is **[`python-essentials/`](python-essentials/)**. It is the exclusive source of lesson and course content. The application generates a browser-ready index from these files; it does not keep a second manually authored copy of the curriculum.

## Features

- Dynamically discovered modules and lessons, with the module README lesson list and natural numeric filename ordering respected.
- Markdown lesson reading with a generated table of contents, safe HTML sanitization, syntax-highlighted code, copy buttons, tables, lists, links, and relative assets.
- Search through lesson and module titles, headings, and full lesson text.
- Previous/next lesson and module navigation, a responsive course drawer, and course overview.
- Lesson and module completion, course progress, last lesson, and Continue Learning stored in this browser only.
- No account, authentication, database, server-side user data, or learner-code execution.
- Static production output suitable for Vercel.

## Technology

Vanilla JavaScript modules bundled with esbuild, Markdown-it, Highlight.js, DOMPurify, and a small Node.js build script. The application is a static site; no backend or runtime environment variables are required. Yaoguai Crypto's Shippori Mincho, Zen Kaku Gothic New, and IBM Plex Mono font assets are bundled locally. The interface adapts the reference project's near-black surfaces, deep red accent, fine borders, restrained glow, and Japanese-inspired visual language.

## Project structure

```text
Yaoguai-Programming/
├── python-essentials/          # Exclusive, unchanged course source
│   ├── README.md                # Course overview and recommended order
│   ├── COURSE-CHECKLIST.md
│   └── NN-module-name/          # Module README and lesson Markdown
├── public/
│   ├── index.html
│   ├── styles.css
│   └── fonts/                   # Local Yaoguai-family fonts
├── scripts/
│   ├── build-course.mjs         # Discovers content and emits manifest/assets
│   ├── check-content.mjs        # Checks indexed lessons against source files
│   └── serve.mjs                # Local static preview server
├── src/app.js                   # Routing, UI, Markdown, search, progress
├── package.json
└── vercel.json
```

## Local setup (Windows PowerShell)

Install Node.js 20 or newer, then run:

```powershell
Set-Location D:\yaoguai\Yaoguai-Programming
npm install
npm run dev
```

Open <http://localhost:4173>. `npm run dev` creates the course manifest and JavaScript bundle before starting the local server. To serve the most recently generated output without rebuilding, use `npm run preview`.

## Build and content verification

```powershell
npm run build
npm run check:content
```

The build command discovers the course, emits `public/course-manifest.json`, copies any non-Markdown course assets to `public/course-assets/`, and bundles `src/app.js` to `public/app.bundle.js`. Generated files are ignored by Git. `npm run check:content` compares every indexed lesson's text with its original Markdown source.

The content discovery script reads **only `python-essentials/`**. It reads the root `README.md` as the overview, discovers module directories in numeric/natural order, reads each module README, follows its Markdown lesson list first, then includes any additional Markdown files in natural filename order. Lesson IDs derive from their source-relative paths, so lesson ordering changes do not reassign completion records. The build copies any future images and other non-Markdown assets with their relative paths; Markdown asset references resolve against the original Markdown file location.

### Adding a module

Create a numbered module directory in `python-essentials/`, add a `README.md` with its title, description, and lesson list, and add the lesson Markdown files. Rebuild to include it in the navigation, dashboard, search, and progress calculations.

### Adding a lesson

Add the Markdown lesson under its module and link it from that module's README under `## Lessons`. Use a numbered filename to make ordering explicit. Rebuild; no frontend changes are needed. If a file is not linked in the module README, it is still discovered and follows the natural filename order after listed lessons.

### Markdown, code, and exercises

Lessons are rendered from their source Markdown. Fenced blocks use the language tag from the Markdown fence, with Python, Bash/shell, PowerShell, JSON, JavaScript, HTML/XML, and plaintext supported. Each block gets a language label and copy control. Existing exercise, hint, and solution sections stay in their source lesson and are rendered as written; no grading behavior or expected result is invented. HTML from Markdown is sanitized before insertion. Links and images are resolved relative to their source file, and external links open in a separate tab with safe `rel` attributes.

The platform presents code for study and copying; it does not execute arbitrary learner code. Exercises are completed in the learner's own Python environment.

## Progress and privacy

Completion, last accessed lesson, and last module are stored in `localStorage` on the current browser/device. Course and module percentages are calculated from currently discovered lesson IDs. Continue Learning opens the last accessed incomplete lesson, falling back to the first incomplete lesson. Use **Reset local progress** in the course navigation to erase local progress; the app asks for confirmation first.

Progress is local to this browser and does not sync across devices. There is no authentication or backend progress service. Progress code is isolated from the UI so a future sync adapter can be added separately.

## Vercel deployment

Import the GitHub repository `Youssef-mohamed-sayed/yaoguai-programming` into Vercel with the project root at this directory. The included `vercel.json` uses `npm run build` and publishes `public/`; no environment variables are needed. Vercel serves `index.html` for lesson, module, and search routes, so direct links and refreshes work. Markdown source is compiled into the generated manifest at build time; relative assets are packaged under `public/course-assets/`.

For a local production-output preview, run `npm run build`, then `npm run preview` and open <http://localhost:4173>.
