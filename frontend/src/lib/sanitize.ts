/** Defensive text sanitizers for display and logging. */

const TAG_PATTERN = /<[^>]*>/g;

/** Strip HTML tags. Suitable for rendering plain text extracted from documents. */
export function stripTags(input: string): string {
  return input.replace(TAG_PATTERN, "").trim();
}

/** Collapse whitespace and trim. */
export function normalizeWhitespace(input: string): string {
  return input.replace(/\s+/g, " ").trim();
}

/** Clamp free text to a maximum length for UI previews. */
export function clampText(input: string, max = 200, ellipsis = "…"): string {
  if (input.length <= max) return input;
  return `${input.slice(0, max).trimEnd()}${ellipsis}`;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(input: string): boolean {
  return EMAIL_PATTERN.test(input.trim());
}

/** Redact email addresses from a string (for log hygiene). */
export function redactEmails(input: string): string {
  return input.replace(/[^\s@]+@[^\s@]+\.[^\s@]+/g, "[redacted]");
}

/** Redact everything after the first 2 chars of a token for display. */
export function maskToken(token: string): string {
  if (token.length <= 4) return "****";
  return `${token.slice(0, 2)}…${token.slice(-2)}`;
}
