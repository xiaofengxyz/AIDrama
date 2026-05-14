const { spawn } = require('child_process');
const path = require('path');
const os = require('os');
const { getRuntimeConfig } = require('./runtime-config');

const root = path.join(__dirname, '..');
const frontendDir = path.join(root, 'frontend');
const config = getRuntimeConfig(root);
const npmCommand = os.platform() === 'win32' ? 'npm.cmd' : 'npm';

const env = {
  ...config.env,
  PORT: config.frontendPort,
  NEXT_PUBLIC_API_URL: config.apiUrl,
};

console.log(`[frontend] Starting Next.js on ${config.frontendUrl}`);
console.log(`[frontend] API URL: ${config.apiUrl}`);

const frontend = spawn(npmCommand, ['run', 'dev', '--', '-p', config.frontendPort], {
  cwd: frontendDir,
  stdio: 'inherit',
  env,
});

frontend.on('exit', (code) => process.exit(code || 0));
