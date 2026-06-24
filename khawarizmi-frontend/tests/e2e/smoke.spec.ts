import { test, expect } from "@playwright/test";

const TEST_EMAIL = `e2e-test-${Date.now()}@gmail.com`;
const TEST_PASSWORD = "TestPass123!";

let authToken: string | null = null;

test.describe.serial("Smoke runtime", () => {
  test("01 — landing page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1").first()).toBeVisible();
    const title = await page.title();
    expect(title).toContain("الخوارزمي");
  });

  test("02 — register creates user and redirects to dashboard", async ({ page }) => {
    await page.goto("/auth/register");
    await expect(page.locator("form")).toBeVisible();

    await page.locator("input[type='text']").first().fill("E2E Test User");
    await page.locator("input[type='email']").first().fill(TEST_EMAIL);
    await page.locator("input[type='password']").first().fill(TEST_PASSWORD);
    await page.locator("select").first().selectOption("Sciences Naturelles");
    await page.locator("button[type='submit']").first().click();

    await page.waitForURL("**/dashboard", { timeout: 15_000 });
    await expect(page.locator("body")).toBeVisible();
  });

  test("03 — login and verify token stored", async ({ page }) => {
    await page.goto("/auth/login");
    await page.locator("input[type='email']").first().fill(TEST_EMAIL);
    await page.locator("input[type='password']").first().fill(TEST_PASSWORD);
    await page.locator("button[type='submit']").first().click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    authToken = await page.evaluate(() =>
      localStorage.getItem("khawarizmi_token")
    );
    expect(authToken).toBeTruthy();
  });

  test("04 — /cours loads", async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem("khawarizmi_token", token!);
    }, authToken);
    await page.goto("/cours");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).toBeVisible();
  });

  test("05 — /action-verbs loads", async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem("khawarizmi_token", token!);
    }, authToken);
    await page.goto("/action-verbs");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).toBeVisible();
  });

  test("06 — /document-analysis loads", async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem("khawarizmi_token", token!);
    }, authToken);
    await page.goto("/document-analysis");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).toBeVisible();
  });

  test("07 — /annales loads", async ({ page }) => {
    await page.addInitScript((token) => {
      localStorage.setItem("khawarizmi_token", token!);
    }, authToken);
    await page.goto("/annales");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).toBeVisible();
  });
});
