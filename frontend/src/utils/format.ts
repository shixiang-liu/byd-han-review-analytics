type NumberFormatInput = number | null | undefined;

export function formatNumber(
  value: NumberFormatInput,
  options: Intl.NumberFormatOptions & { locale?: string; fallback?: string } = {},
) {
  const { locale = "en-US", fallback = "--", ...numberOptions } = options;

  if (typeof value !== "number" || Number.isNaN(value)) {
    return fallback;
  }

  return new Intl.NumberFormat(locale, numberOptions).format(value);
}

export function formatPercent(
  value: NumberFormatInput,
  options: {
    fractionDigits?: number;
    locale?: string;
    fallback?: string;
    input?: "ratio" | "percent";
  } = {},
) {
  const {
    fractionDigits = 1,
    locale = "en-US",
    fallback = "--",
    input = "ratio",
  } = options;

  if (typeof value !== "number" || Number.isNaN(value)) {
    return fallback;
  }

  const basis = input === "ratio" ? value * 100 : value;
  const formatter = new Intl.NumberFormat(locale, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });

  return `${formatter.format(basis)}%`;
}
