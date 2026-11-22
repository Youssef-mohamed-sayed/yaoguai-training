import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    proxy: Object.fromEntries(['/api', '/network', '/linux', '/programming', '/crypto', '/admin', '/reset-password'].map((route) => [route, 'http://127.0.0.1:5000'])),
  },
});
