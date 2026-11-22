import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'python-essentials');
const output = path.join(root, 'public');
const assetOutput = path.join(output, 'course-assets');

async function filesUnder(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const all = [];
  for (const entry of entries) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) all.push(...await filesUnder(absolute));
    else all.push(absolute);
  }
  return all;
}

function titleFrom(markdown, fallback) {
  const frontmatter = markdown.match(/^---\s*\r?\n[\s\S]*?^title:\s*["']?(.+?)["']?\s*$/m);
  if (frontmatter) return frontmatter[1].trim();
  const heading = markdown.match(/^#\s+(.+?)\s*#*\s*$/m);
  return heading?.[1]?.trim() || fallback;
}

function slugify(value) {
  return value.toLowerCase().trim().replace(/[`*_]/g, '').replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'section';
}

const allFiles = (await filesUnder(source)).sort((a, b) => path.relative(source, a).localeCompare(path.relative(source, b), undefined, { numeric: true, sensitivity: 'base' }));
const markdownFiles = allFiles.filter(file => file.toLowerCase().endsWith('.md'));
const moduleDirs = (await readdir(source, { withFileTypes: true }))
  .filter(entry => entry.isDirectory())
  .map(entry => entry.name)
  .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }));

const overviewPath = path.join(source, 'README.md');
const overview = await readFile(overviewPath, 'utf8');
const modules = [];
const lessonBySourcePath = new Map();
const moduleByReadmePath = new Map();

for (const [moduleIndex, directory] of moduleDirs.entries()) {
  const modulePath = path.join(source, directory);
  const readmePath = path.join(modulePath, 'README.md');
  moduleByReadmePath.set(path.relative(source, readmePath).split(path.sep).join('/').toLowerCase(), directory);
  let readme = '';
  try { readme = await readFile(readmePath, 'utf8'); }
  catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const markdownInModule = markdownFiles.filter(file => path.relative(modulePath, file) !== '..' && !path.relative(modulePath, file).startsWith(`..${path.sep}`));
  const listed = [...readme.matchAll(/^\s*[-*+]\s+\[[^\]]+\]\(([^)]+\.md)(?:#[^)]*)?\)/gm)].map(match => match[1]);
  const discovered = markdownInModule.filter(file => path.resolve(path.dirname(readmePath), file) !== path.resolve(readmePath));
  const ordered = [];
  for (const relative of listed) {
    const target = path.resolve(path.dirname(readmePath), relative);
    if (discovered.includes(target) && !ordered.includes(target)) ordered.push(target);
  }
  for (const file of discovered) if (!ordered.includes(file)) ordered.push(file);
  const lessons = [];
  for (const [lessonIndex, file] of ordered.entries()) {
    const sourcePath = path.relative(source, file).split(path.sep).join('/');
    const content = await readFile(file, 'utf8');
    const lesson = {
      id: sourcePath.replace(/\.md$/i, ''),
      sourcePath,
      title: titleFrom(content, path.basename(file, '.md').replace(/^\d+[-_]?/, '').replace(/[-_]+/g, ' ')),
      content,
      order: lessonIndex + 1,
    };
    lessons.push(lesson);
    lessonBySourcePath.set(sourcePath.toLowerCase(), lesson.id);
  }
  const firstParagraph = readme.split(/^##\s+/m)[0].split(/\r?\n/).slice(1).filter(line => line.trim() && !line.startsWith('#')).join('\n').trim();
  modules.push({
    id: directory,
    title: titleFrom(readme, directory.replace(/^\d+[-_]?/, '').replace(/[-_]+/g, ' ')),
    order: moduleIndex + 1,
    sourcePath: path.relative(source, readmePath).split(path.sep).join('/'),
    description: firstParagraph,
    readme,
    lessons,
  });
}

const files = {};
for (const file of allFiles.filter(file => !file.toLowerCase().endsWith('.md'))) {
  const relative = path.relative(source, file).split(path.sep).join('/');
  const destination = path.join(assetOutput, relative);
  await mkdir(path.dirname(destination), { recursive: true });
  await cp(file, destination);
  files[relative.toLowerCase()] = `/course-assets/${relative.split('/').map(encodeURIComponent).join('/')}`;
}

const totalLessons = modules.reduce((sum, module) => sum + module.lessons.length, 0);
if (!modules.length || !totalLessons) throw new Error(`No course modules or lessons discovered in ${source}`);
const headings = {};
for (const module of modules) {
  for (const lesson of module.lessons) {
    headings[lesson.id] = [...lesson.content.matchAll(/^(#{1,6})\s+(.+?)\s*#*\s*$/gm)]
      .map(match => ({ level: match[1].length, title: match[2], id: slugify(match[2]) }));
  }
}
const consumedMarkdown = new Set([
  'readme.md',
  ...modules.flatMap(module => [module.sourcePath, ...module.lessons.map(lesson => lesson.sourcePath)]),
].map(sourcePath => sourcePath.toLowerCase()));
const documents = {};
for (const file of markdownFiles) {
  const sourcePath = path.relative(source, file).split(path.sep).join('/');
  if (!consumedMarkdown.has(sourcePath.toLowerCase())) {
    const content = await readFile(file, 'utf8');
    documents[sourcePath.toLowerCase()] = { sourcePath, title: titleFrom(content, path.basename(file, '.md')), content };
  }
}

const manifest = {
  title: titleFrom(overview, 'Python Programming Essentials'),
  overview,
  modules,
  totalLessons,
  source: 'python-essentials/',
  assets: files,
  documents,
  lessonBySourcePath: Object.fromEntries(lessonBySourcePath),
  moduleByReadmePath: Object.fromEntries(moduleByReadmePath),
  headings,
};
await writeFile(path.join(output, 'course-manifest.json'), JSON.stringify(manifest));
console.log(`Discovered ${modules.length} modules and ${totalLessons} lessons from python-essentials/.`);
