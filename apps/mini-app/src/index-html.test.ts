import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

describe("Mini App HTML shell", () => {
  it("loads the Telegram WebApp SDK before the application module", () => {
    const html = readFileSync("index.html", "utf8");
    const telegramSdkIndex = html.indexOf(
      '<script src="https://telegram.org/js/telegram-web-app.js?62"></script>',
    );
    const applicationModuleIndex = html.indexOf('<script type="module" src="/src/main.tsx"></script>');

    expect(telegramSdkIndex).toBeGreaterThan(-1);
    expect(telegramSdkIndex).toBeLessThan(applicationModuleIndex);
  });
});
