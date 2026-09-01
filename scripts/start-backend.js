import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// Locate Python executable (check .venv first, then fallback to system python)
function getPythonExecutable() {
  const venvWindows = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
  const venvUnix = path.join(rootDir, '.venv', 'bin', 'python');

  if (fs.existsSync(venvWindows)) {
    return venvWindows;
  }
  if (fs.existsSync(venvUnix)) {
    return venvUnix;
  }

  // Fallback to system python
  return process.platform === 'win32' ? 'python' : 'python3';
}

const pythonExe = getPythonExecutable();

// If additional args are passed (e.g. node scripts/start-backend.js --run <script>)
const args = process.argv.slice(2);
let spawnArgs;

if (args.length > 0) {
  if (args[0] === '--run' && args[1]) {
    spawnArgs = [args[1], ...args.slice(2)];
  } else {
    spawnArgs = args;
  }
} else {
  // Default: start uvicorn backend
  spawnArgs = ['-m', 'uvicorn', 'backend.app.main:app', '--reload', '--port', '8000'];
}

console.log(`[IBVAP Backend] Starting with: "${pythonExe}" ${spawnArgs.join(' ')}`);

// Use shell: false to prevent space-in-path issues on Windows with cmd.exe
const backendProcess = spawn(pythonExe, spawnArgs, {
  cwd: rootDir,
  stdio: 'inherit',
  shell: false
});

backendProcess.on('error', (err) => {
  console.error('[IBVAP Backend] Failed to start backend process:', err.message);
  process.exit(1);
});

backendProcess.on('exit', (code, signal) => {
  if (signal) {
    console.log(`[IBVAP Backend] Process stopped with signal ${signal}`);
  } else if (code !== null && code !== 0) {
    console.log(`[IBVAP Backend] Process exited with code ${code}`);
  }
  process.exit(code || 0);
});

// Forward termination signals
['SIGINT', 'SIGTERM', 'SIGHUP'].forEach((signal) => {
  process.on(signal, () => {
    if (!backendProcess.killed) {
      try {
        backendProcess.kill(signal);
      } catch (e) {
        // ignore
      }
    }
  });
});
