import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'dist');
await mkdir(output, { recursive: true });
const copies = [
  ['platforms/linux/dist', 'dist/linux'],
  ['platforms/programming/public', 'dist/programming'],
  ['platforms/network/public/assets', 'dist/network/assets'],
  ['platforms/crypto/public', 'dist/crypto'],
];
for (const [from, to] of copies) {
  const destination = path.join(root, to);
  await rm(destination, { recursive: true, force: true });
  await mkdir(path.dirname(destination), { recursive: true });
  await cp(path.join(root, from), destination, { recursive: true });
}
for (const outputPath of ['dist/linux/training-bridge.js', 'dist/programming/training-bridge.js', 'dist/network/assets/js/training-bridge.js', 'dist/crypto/js/training-bridge.js', 'platforms/network/public/assets/js/training-bridge.js', 'platforms/crypto/public/js/training-bridge.js']) {
  const destination = path.join(root, outputPath);
  await mkdir(path.dirname(destination), { recursive: true });
  await cp(path.join(root, 'public/training-bridge.js'), destination);
}
console.log('Packaged the four preserved course applications under dist/.');
