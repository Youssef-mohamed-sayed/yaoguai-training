import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const contentRoot = path.join(root, 'linux-essentials');
const publicRoot = path.join(root, 'public');
const outputAssets = path.join(publicRoot, 'course-assets');
const markdown = (file) => fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
const sortName = (a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
const titleFrom = (text, fallback) => text.match(/^#\s+(.+)$/m)?.[1]?.trim() || fallback;
const sectionFrom = (source, title) => {
  const lines = source.split(/\r?\n/);
  const start = lines.findIndex((line) => /^##\s+/u.test(line) && line.replace(/^##\s+/u, '').trim().toLowerCase() === title.toLowerCase());
  if (start < 0) return '';
  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    if (/^#{1,2}\s+/u.test(lines[index])) { end = index; break; }
  }
  return lines.slice(start + 1, end).join('\n').trim();
};
const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
  const file = path.join(dir, entry.name);
  if (entry.isSymbolicLink()) throw new Error(`Symbolic links are not supported in course content: ${path.relative(contentRoot, file)}`);
  return entry.isDirectory() ? walk(file) : [file];
});

if (!fs.existsSync(contentRoot)) throw new Error(`Course content not found: ${contentRoot}`);
fs.mkdirSync(publicRoot, { recursive: true });
fs.rmSync(outputAssets, { recursive: true, force: true });
fs.mkdirSync(outputAssets, { recursive: true });

const moduleDirs = fs.readdirSync(contentRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort(sortName);
const modules = [];
for (const [moduleIndex, dirname] of moduleDirs.entries()) {
  const dir = path.join(contentRoot, dirname);
  const readme = path.join(dir, 'README.md');
  const moduleText = fs.existsSync(readme) ? markdown(readme) : '';
  const lessons = walk(dir)
    .filter((file) => file.toLowerCase().endsWith('.md') && path.basename(file).toLowerCase() !== 'readme.md')
    .sort((a, b) => sortName(path.relative(dir, a), path.relative(dir, b))).map((absolute) => {
      const filename = path.basename(absolute);
      const source = markdown(absolute);
      const id = path.relative(contentRoot, absolute).split(path.sep).join('/');
      return { id, slug: id.replace(/\.md$/i, ''), filename, title: titleFrom(source, filename.replace(/\.md$/i, '').replace(/^\d+-/, '').replaceAll('-', ' ')), markdown: source, moduleId: dirname, order: filename.match(/^\d+/)?.[0] || '999' };
    });
  if (!lessons.length) continue;
  modules.push({ id: dirname, title: titleFrom(moduleText, dirname.replace(/^\d+-/, '').replaceAll('-', ' ')), description: moduleText, order: dirname.match(/^\d+/)?.[0] || String(moduleIndex + 1), lessons });
}

const all = walk(contentRoot);
const assets = [];
for (const file of all.filter((name) => !name.toLowerCase().endsWith('.md'))) {
  const relative = path.relative(contentRoot, file);
  const destination = path.join(outputAssets, relative);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(file, destination);
  assets.push(relative.replaceAll(path.sep, '/'));
}
const rootReadme = markdown(path.join(contentRoot, 'README.md'));
const referencePath = path.join(contentRoot, 'REFERENCES.md');
fs.writeFileSync(path.join(publicRoot, 'course-data.json'), JSON.stringify({
  title: 'Linux Essentials',
  description: 'A practical, beginner-first Linux course for learners preparing for Linux administration, CTFs, and cybersecurity work.',
  introduction: rootReadme,
  overviewSections: {
    audience: sectionFrom(rootReadme, 'Audience'),
    outcomes: sectionFrom(rootReadme, 'Learning outcomes'),
    setup: sectionFrom(rootReadme, 'Practice environments and tools')
  },
  references: fs.existsSync(referencePath) ? markdown(referencePath) : '',
  modules,
  assets
}));
console.log(`Discovered ${modules.length} modules and ${modules.reduce((sum, module) => sum + module.lessons.length, 0)} lessons.`);
