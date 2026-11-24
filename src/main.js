import { platforms, renderPlatform } from './data/platforms.js';
import { initAuth } from './auth.js';
import './styles/main.css';

async function renderCourses() {
  try {
    const response = await fetch('/api/platforms');
    if (!response.ok) throw new Error('Catalog unavailable');
    const { data } = await response.json();
    const stats = Object.fromEntries(data.map((course) => [course.id, course]));
    document.querySelector('#platform-grid').innerHTML = platforms.map((platform, index) => renderPlatform(platform, index, stats[platform.url.slice(1)])).join('');
  } catch {
    document.querySelector('#platform-grid').innerHTML = platforms.map(renderPlatform).join('');
  }
}
// The course grid exists only on the home page; skip the catalog request on account and admin pages.
if ((location.pathname.replace(/\/$/, '') || '/') === '/') renderCourses();
document.querySelector('.footer-index').textContent = `Yaoguai Training · ${new Date().getFullYear()}`;
initAuth().finally(() => document.querySelector('#yg-boot')?.remove());
