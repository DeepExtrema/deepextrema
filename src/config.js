const fs = require('fs');
const path = require('path');

const REQUIRED = ['name', 'tagline', 'githubLogin', 'about', 'currently', 'projects', 'links', 'footerStamp'];

function loadConfig(file = path.join(__dirname, '..', 'profile.config.json')) {
  const cfg = JSON.parse(fs.readFileSync(file, 'utf8'));
  const missing = REQUIRED.filter((k) => cfg[k] === undefined);
  if (missing.length) throw new Error(`Config missing required field(s): ${missing.join(', ')}`);
  if (!Array.isArray(cfg.projects) || cfg.projects.length === 0) throw new Error('Config missing required field: projects');
  if (!Array.isArray(cfg.links) || cfg.links.length === 0) throw new Error('Config missing required field: links');
  return cfg;
}

module.exports = { loadConfig };
