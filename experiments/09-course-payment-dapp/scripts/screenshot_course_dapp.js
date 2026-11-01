const { chromium } = require("playwright");

const BASE_URL =
  "http://127.0.0.1:8080/experiments/09-course-payment-dapp/ui/index.html";
const OUTPUT = "experiments/09-course-payment-dapp/output";

async function waitForStatus(page, text, timeout = 30000) {
  await page.waitForFunction(
    (needle) => document.getElementById("status").textContent.toLowerCase().includes(needle),
    text.toLowerCase(),
    { timeout }
  );
}

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
    deviceScaleFactor: 1.5,
  });

  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await page.waitForSelector(".course-card", { timeout: 20000 });
  await page.waitForFunction(
    () => document.querySelectorAll(".course-card").length === 3,
    null,
    { timeout: 20000 }
  );
  await page.waitForTimeout(1200);

  await page.screenshot({ path: `${OUTPUT}/01_dapp_dashboard.png`, fullPage: true });
  console.log("wrote 01_dapp_dashboard.png");

  await page.locator(".course-card button.buy").first().click();
  await waitForStatus(page, "purchase confirmed");
  await page.waitForTimeout(800);

  await page.screenshot({ path: `${OUTPUT}/02_purchase_confirmed.png`, fullPage: true });
  console.log("wrote 02_purchase_confirmed.png");

  await page.locator("#withdraw").click();
  await waitForStatus(page, "withdrawal confirmed");
  await page.waitForTimeout(800);

  await page.screenshot({ path: `${OUTPUT}/03_owner_withdraw.png`, fullPage: true });
  console.log("wrote 03_owner_withdraw.png");

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
