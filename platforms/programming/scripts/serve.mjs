import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2' };
createServer(async (request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  const candidate = pathname === '/' ? path.join(root, 'index.html') : path.resolve(root, `.${pathname}`);
  if (!candidate.startsWith(root + path.sep) && candidate !== path.join(root, 'index.html')) {
    response.writeHead(403).end('Forbidden'); return;
  }
  try {
    let target = candidate;
    if ((await stat(target)).isDirectory()) target = path.join(target, 'index.html');
    const body = await readFile(target);
    response.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream' });
    response.end(body);
  } catch {
    response.writeHead(200, { 'Content-Type': types['.html'] });
    response.end(await readFile(path.join(root, 'index.html')));
  }
}).listen(4173, () => console.log('Yaoguai Programming: http://localhost:4173'));
