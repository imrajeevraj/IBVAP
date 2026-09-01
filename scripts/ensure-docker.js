import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

console.log('🚀 [IBVAP] Checking and starting Docker infrastructure (PostgreSQL, Redis, MediaMTX)...');

try {
  execSync('docker-compose up -d postgres redis mediamtx', {
    cwd: rootDir,
    stdio: 'inherit',
    shell: true
  });
  console.log('✅ [IBVAP] Docker services are online and ready.');
} catch (err) {
  console.warn('⚠️  [IBVAP] Docker command returned a warning or Docker is not running. Proceeding with application startup...');
}
