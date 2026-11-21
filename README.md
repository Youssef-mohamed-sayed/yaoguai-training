# Yaoguai Essentials Training

Yaoguai Essentials Training is the central hub for four independent Yaoguai learning platforms. It introduces the ecosystem and gives learners a direct path into networking, Linux, Python programming, and cryptography.

## Learning platforms

1. [Yaoguai Network](https://yaoguai-network.vercel.app/) — networking fundamentals, protocols, and network security.
2. [Yaoguai Linux](https://yaoguai-linux.vercel.app/) — command-line use, system administration, and practical Linux skills.
3. [Yaoguai Python](https://yaoguai-programming.vercel.app/) — Python programming, problem-solving, automation, and cybersecurity scripting.
4. [Yaoguai Crypto](https://yaoguai-crypto.vercel.app/) — cryptography, encryption, hashing, encoding, and practical challenges.

## Technology

The hub is a lightweight static site built with semantic HTML, CSS, vanilla JavaScript, and Vite. It has no backend, authentication, or runtime framework dependency. Yaoguai Crypto's visual identity informed the colors and typography; the required logo, favicon, and font files are copied into this project's `public/assets` directory so the site works independently of its sibling projects.

## Run locally

Requires Node.js 20.19+ or 22.12+.

```sh
npm install
npm run dev
```

Vite prints the local URL (usually `http://localhost:5173`).

## Production build

```sh
npm run build
npm run preview
```

The static production files are written to `dist/`.

## Deploy on Vercel

Import this repository as a Vercel project. `vercel.json` configures the Vite production build (`npm run build`) and publishes `dist/`. No environment variables or backend services are required.

## Project structure

```text
index.html
public/assets/        copied brand assets and local fonts
src/data/platforms.js platform names, descriptions, icons, and URLs
src/main.js           renders the platform cards
src/styles/main.css   responsive visual system
```
