import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const contentRoot = path.join(root, 'linux-essentials');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public', 'course-data.json'), 'utf8'));
const sortName = (a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
const walk = (directory) => fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
  const absolute = path.join(directory, entry.name);
  return entry.isDirectory() ? walk(absolute) : [absolute];
});

test('discovers every module in the source course in numeric order', () => {
  const expected = fs.readdirSync(contentRoot, { withFileTypes: true }).filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort(sortName);
  assert.deepEqual(data.modules.map((module) => module.id), expected);
  assert.equal(data.introduction, fs.readFileSync(path.join(contentRoot, 'README.md'), 'utf8'));
});

test('includes each lesson once and preserves its Markdown source', () => {
  const expected = data.modules.flatMap((module) => walk(path.join(contentRoot, module.id))
    .filter((file) => file.toLowerCase().endsWith('.md') && path.basename(file).toLowerCase() !== 'readme.md')
    .map((file) => path.relative(contentRoot, file).split(path.sep).join('/'))).sort(sortName);
  const actual = data.modules.flatMap((module) => module.lessons.map((lesson) => lesson.id)).sort(sortName);
  assert.ok(actual.length > 0);
  assert.deepEqual(actual, expected);
  for (const module of data.modules) {
    assert.ok(module.title);
    assert.ok(module.description);
    assert.ok(module.lessons.length > 0);
    for (const lesson of module.lessons) {
      const source = path.resolve(contentRoot, ...lesson.id.split('/'));
      const relative = path.relative(contentRoot, source);
      assert.ok(relative && !relative.startsWith('..') && !path.isAbsolute(relative), `Lesson escapes course content: ${lesson.id}`);
      assert.equal(lesson.markdown, fs.readFileSync(source, 'utf8'));
      assert.ok(lesson.title);
      assert.equal(lesson.moduleId, module.id);
    }
  }
});

test('copies every non-Markdown course asset without changing its contents', () => {
  const expected = walk(contentRoot).filter((file) => !file.toLowerCase().endsWith('.md'))
    .map((file) => path.relative(contentRoot, file).split(path.sep).join('/')).sort(sortName);
  assert.deepEqual([...data.assets].sort(sortName), expected);
  for (const asset of data.assets) {
    const source = path.resolve(contentRoot, ...asset.split('/'));
    const output = path.resolve(root, 'public', 'course-assets', ...asset.split('/'));
    assert.deepEqual(fs.readFileSync(output), fs.readFileSync(source), `Asset changed during build: ${asset}`);
  }
});

test('includes course overview, learning outcomes, and reference library', () => {
  assert.ok(data.overviewSections.audience);
  assert.ok(data.overviewSections.outcomes);
  assert.ok(data.overviewSections.setup);
  assert.ok(data.references.includes('https://'));
});
