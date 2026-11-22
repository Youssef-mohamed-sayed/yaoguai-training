import { cp, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const bridge = path.join(root, 'public', 'training-bridge.js');
for (const directory of [
  'platforms/linux/public',
  'platforms/programming/public',
  'platforms/network/public/assets/js',
  'platforms/crypto/public/js',
]) {
  await mkdir(path.join(root, directory), { recursive: true });
  await cp(bridge, path.join(root, directory, 'training-bridge.js'));
}
