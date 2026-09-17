import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const currentDir = path.dirname(fileURLToPath(import.meta.url));

const themeCss = readFileSync(
  path.resolve(currentDir, "../theme.css"),
  "utf8",
);

const layoutCss = readFileSync(
  path.resolve(currentDir, "../layout.css"),
  "utf8",
);

describe("shell layout styles", () => {
  it("avoids a fixed desktop-only body width", () => {
    expect(themeCss).not.toContain("min-width: 1200px");
    expect(layoutCss).toContain("@media (max-width: 1199px)");
  });
});
