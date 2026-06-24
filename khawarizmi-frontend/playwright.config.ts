import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  timeout: 30_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], locale: "fr-DZ" },
    },
  ],
  ...(process.env.PW_SKIP_WEBSERVER !== "1"
    ? {
        webServer: [
          {
            command:
              "uvicorn main:app --host 0.0.0.0 --port 8000",
            cwd: "../khawarizmi-backend",
            port: 8000,
            reuseExistingServer: true,
            timeout: 60_000,
          },
          {
            command: "npm run dev",
            port: 3000,
            reuseExistingServer: true,
            timeout: 60_000,
          },
        ],
      }
    : {}),
});
