import { describe, expect, it } from "vitest";
import { formatNumber, formatPercent } from "../format";

describe("format helpers", () => {
  it("formats large numbers with grouping", () => {
    expect(formatNumber(1234567)).toBe("1,234,567");
  });

  it("formats ratio values as percentages", () => {
    expect(formatPercent(0.1234)).toBe("12.3%");
  });
});
