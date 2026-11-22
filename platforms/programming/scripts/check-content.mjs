import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifest = JSON.parse(await readFile(path.join(root, 'public/course-manifest.json'), 'utf8'));
const sourceRoot = path.join(root, 'python-essentials');
let checked = 0;
for (const module of manifest.modules) {
  for (const lesson of module.lessons) {
    const original = await readFile(path.join(sourceRoot, lesson.sourcePath), 'utf8');
    if (original !== lesson.content) throw new Error(`Content mismatch: ${lesson.sourcePath}`);
    checked++;
  }
}
console.log(`Verified ${manifest.modules.length} modules and ${checked} lesson files byte-for-byte against python-essentials/.`);
