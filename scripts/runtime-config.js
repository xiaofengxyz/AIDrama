const fs = require('fs');
const path = require('path');

const DEFAULT_BACKEND_PORT = '48217';
const DEFAULT_FRONTEND_PORT = '39211';
const DEFAULT_API_HOST = '0.0.0.0';
const DEFAULT_LLM_PROVIDER = 'dashscope';
const DEFAULT_OPENAI_MODEL = 'qwen-plus';

/**
 * Parse a single dotenv line without depending on an extra runtime package.
 * @param {string} line Raw line from a dotenv-style file.
 * @returns {{ key: string, value: string } | null} Parsed key/value pair or null for comments and invalid lines.
 */
function parseEnvLine(line) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('#')) {
    return null;
  }

  const normalized = trimmed.startsWith('export ') ? trimmed.slice(7).trim() : trimmed;
  const separatorIndex = normalized.indexOf('=');
  if (separatorIndex <= 0) {
    return null;
  }

  const key = normalized.slice(0, separatorIndex).trim();
  let value = normalized.slice(separatorIndex + 1).trim();
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    value = value.slice(1, -1);
  }

  return { key, value };
}

/**
 * Read a dotenv-style file into a plain object.
 * @param {string} envPath Absolute path to the environment file.
 * @returns {Record<string, string>} Parsed environment values.
 */
function readEnvFile(envPath) {
  if (!fs.existsSync(envPath)) {
    return {};
  }

  const values = {};
  const content = fs.readFileSync(envPath, 'utf8');
  for (const line of content.split(/\r?\n/)) {
    const parsed = parseEnvLine(line);
    if (parsed) {
      values[parsed.key] = parsed.value;
    }
  }
  return values;
}

/**
 * Load project environment values in the same order as the FastAPI app.
 * @param {string} root Repository root directory.
 * @returns {Record<string, string>} Environment values with local files applied.
 */
function loadProjectEnv(root = path.join(__dirname, '..')) {
  const preferred = process.env.AIDRAMA_ENV_FILE || '.env.local';
  const candidates = ['.env', preferred];
  const env = { ...process.env };

  for (const candidate of candidates) {
    Object.assign(env, readEnvFile(path.join(root, candidate)));
  }

  return env;
}

/**
 * Normalize a port string and fall back when the value is missing or invalid.
 * @param {string | undefined} value Candidate port value.
 * @param {string} fallback Safe default port.
 * @returns {string} Valid TCP port string.
 */
function normalizePort(value, fallback) {
  const port = String(value || '').trim();
  const numericPort = Number(port);
  if (!/^\d+$/.test(port) || numericPort < 1 || numericPort > 65535) {
    return fallback;
  }
  return port;
}

/**
 * Resolve all runtime values used by local Node launchers.
 * @param {string} root Repository root directory.
 * @returns {{
 *   env: Record<string, string>,
 *   apiHost: string,
 *   backendPort: string,
 *   frontendPort: string,
 *   frontendUrl: string,
 *   apiUrl: string,
 *   llmProvider: string,
 *   openaiModel: string
 * }} Runtime configuration with safe defaults.
 */
function getRuntimeConfig(root = path.join(__dirname, '..')) {
  const env = loadProjectEnv(root);
  const backendPort = normalizePort(env.API_PORT, DEFAULT_BACKEND_PORT);
  const frontendPort = normalizePort(env.FRONTEND_PORT || env.PORT, DEFAULT_FRONTEND_PORT);
  const apiHost = env.API_HOST || DEFAULT_API_HOST;
  const apiUrl = env.NEXT_PUBLIC_API_URL || `http://localhost:${backendPort}`;

  return {
    env,
    apiHost,
    backendPort,
    frontendPort,
    frontendUrl: `http://localhost:${frontendPort}`,
    apiUrl,
    llmProvider: (env.LLM_PROVIDER || DEFAULT_LLM_PROVIDER).trim() || DEFAULT_LLM_PROVIDER,
    openaiModel: (env.OPENAI_MODEL || DEFAULT_OPENAI_MODEL).trim() || DEFAULT_OPENAI_MODEL,
  };
}

module.exports = {
  DEFAULT_BACKEND_PORT,
  DEFAULT_FRONTEND_PORT,
  getRuntimeConfig,
  loadProjectEnv,
  normalizePort,
};
