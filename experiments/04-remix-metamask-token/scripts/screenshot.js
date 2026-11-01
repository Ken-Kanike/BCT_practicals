const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1100 },
    deviceScaleFactor: 1
  });

  await page.goto("http://127.0.0.1:8080/experiments/04-remix-metamask-token/ui/", {
    waitUntil: "networkidle"
  });
  await page.waitForSelector("#balances tr");
  await page.waitForTimeout(1200);

  const out = path.join(__dirname, "..", "output", "05_token_dashboard.png");
  await page.screenshot({ path: out, fullPage: true });
  console.log(`wrote ${out}`);
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
