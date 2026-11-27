import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 50_000,
  use: { baseURL:'http://127.0.0.1:8765', trace:'retain-on-failure' },
  webServer: { command: (process.env.PALMPAY_PYTHON ?? (process.platform==='win32'?'.\\.venv\\Scripts\\python.exe':'.venv/bin/python'))+' scripts/start-test-server.py', url:'http://127.0.0.1:8765', timeout:30000 },
})

