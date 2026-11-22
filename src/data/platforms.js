const icons = {
  network: `<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><path d="M16 19 32 11l16 8v20l-16 9-16-9V19Z"/><path d="m16 19 16 9 16-9M32 28v20M8 47l9-9m39 9-9-9M8 17l9 2m39-2-9 2"/><circle cx="8" cy="17" r="3"/><circle cx="56" cy="17" r="3"/><circle cx="8" cy="47" r="3"/><circle cx="56" cy="47" r="3"/><circle cx="32" cy="11" r="3"/><circle cx="32" cy="48" r="3"/><circle cx="32" cy="28" r="3"/></svg>`,
  linux: `<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><rect x="9" y="13" width="46" height="36" rx="2"/><path d="M9 21h46M16 17h.01M21 17h.01M26 17h.01M17 31l6 5-6 5m12 0h12"/><path d="M25 56h14M32 49v7"/></svg>`,
  python: `<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><path d="M30 9h10a8 8 0 0 1 8 8v11H28a8 8 0 0 0-8 8v-7a8 8 0 0 1 8-8h6V9Z"/><path d="M34 55H24a8 8 0 0 1-8-8V36h20a8 8 0 0 0 8-8v7a8 8 0 0 1-8 8h-6v12Z"/><circle cx="38" cy="16" r="1.5"/><circle cx="26" cy="48" r="1.5"/></svg>`,
  crypto: `<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><rect x="13" y="27" width="38" height="28" rx="2"/><path d="M21 27v-8a11 11 0 0 1 22 0v8M32 38v7m0-25v1m-6 28h12"/><circle cx="32" cy="39" r="2"/></svg>`,
};

export const platforms = [
  {
    name: 'Yaoguai Network',
    topic: 'Networking',
    description: 'Explore networking fundamentals and build the knowledge needed to understand networks, protocols, and network security.',
    url: '/network',
    icon: 'network',
    tone: 'network',
  },
  {
    name: 'Yaoguai Linux',
    topic: 'Systems',
    description: 'Learn Linux from the command line, understand system administration fundamentals, and develop practical Linux skills.',
    url: '/linux',
    icon: 'linux',
    tone: 'linux',
  },
  {
    name: 'Yaoguai Programming',
    topic: 'Programming',
    description: 'Learn Python programming, problem-solving, automation, and practical scripting for cybersecurity.',
    url: '/programming',
    icon: 'python',
    tone: 'python',
  },
  {
    name: 'Yaoguai Crypto',
    topic: 'Cryptography',
    description: 'Explore cryptography concepts, encryption, hashing, encoding, and practical cryptographic challenges.',
    url: '/crypto',
    icon: 'crypto',
    tone: 'crypto',
  },
];

export function renderPlatform(platform, index, stats = null) {
  return `
    <a class="platform-card ${platform.tone}" href="${platform.url}" aria-label="Open ${platform.name}">
      <div class="card-topline"><span class="card-number">0${index + 1}</span><span class="card-topic">${platform.topic}</span></div>
      <div class="card-icon">${icons[platform.icon]}</div>
      <div class="card-copy">
        <h3>${platform.name}</h3>
        <p>${platform.description}</p>
      </div>
      <div class="card-action"><span>${stats ? stats.modules_count + ' modules · ' + stats.activities_count + ' activities' : 'Open course'}</span><span class="action-arrow" aria-hidden="true">→</span></div>
    </a>`;
}
