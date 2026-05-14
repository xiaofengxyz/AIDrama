const { spawn } = require('child_process');
const path = require('path');
const os = require('os');
const { getRuntimeConfig } = require('./runtime-config');

const isWin = os.platform() === 'win32';
const pythonPath = isWin
  ? path.join(__dirname, '..', '.venv', 'Scripts', 'python')
  : path.join(__dirname, '..', '.venv', 'bin', 'python');
const config = getRuntimeConfig(path.join(__dirname, '..'));

const env = {
  ...config.env,
  API_HOST: config.apiHost,
  API_PORT: config.backendPort,
  LLM_PROVIDER: config.llmProvider,
  OPENAI_MODEL: config.openaiModel,
  NO_PROXY: '*.aliyuncs.com,localhost,127.0.0.1',
  no_proxy: '*.aliyuncs.com,localhost,127.0.0.1'
};

console.log(`[backend] Starting FastAPI on ${config.apiHost}:${config.backendPort}`);
console.log(`[backend] LLM provider: ${config.llmProvider}`);

const backend = spawn(pythonPath, [
  '-m', 'uvicorn', 'src.apps.comic_gen.api:app',
  '--reload', '--port', config.backendPort, '--host', config.apiHost
], {
  stdio: 'inherit',
  env
});

backend.on('exit', (code) => process.exit(code || 0));
