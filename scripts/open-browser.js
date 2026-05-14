const { exec } = require('child_process');
const path = require('path');
const { getRuntimeConfig } = require('./runtime-config');

const config = getRuntimeConfig(path.join(__dirname, '..'));

setTimeout(() => {
  console.log('\n  ╔══════════════════════════════════════════╗');
  console.log('  ║                                          ║');
  console.log('  ║   AIDrama Film Engine Ready!             ║');
  console.log('  ║                                          ║');
  console.log(`  ║   Frontend:  ${config.frontendUrl.padEnd(29)}║`);
  console.log(`  ║   Backend:   ${config.apiUrl.padEnd(29)}║`);
  console.log('  ║                                          ║');
  console.log('  ║   Press Ctrl+C to stop all services.     ║');
  console.log('  ║                                          ║');
  console.log('  ╚══════════════════════════════════════════╝\n');

  const cmd = process.platform === 'win32' ? `start "" "${config.frontendUrl}"`
    : process.platform === 'darwin' ? `open "${config.frontendUrl}"`
    : `xdg-open "${config.frontendUrl}"`;
  exec(cmd);
}, 5000);
