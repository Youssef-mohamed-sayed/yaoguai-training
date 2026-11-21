import { platforms, renderPlatform } from './data/platforms.js';
import './styles/main.css';

document.querySelector('#platform-grid').innerHTML = platforms.map(renderPlatform).join('');
document.querySelector('#year').textContent = new Date().getFullYear();
