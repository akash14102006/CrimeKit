/**
 * User Identity and Display Name Utility for CrimeKit Enterprise.
 *
 * Adheres strictly to the profile display name requirements:
 * - Uses the user's actual Google / Descope profile display name (e.g. "Akash M").
 * - NEVER uses the email username prefix (e.g. "akraguvaran66").
 * - Safe fallback order:
 *     1. Profile full display name (if not an email or email prefix)
 *     2. firstName + lastName / givenName + familyName
 *     3. givenName / firstName
 *     4. familyName / lastName
 *     5. customAttributes.name
 *     6. email only as final fallback
 */

export interface DescopeOrUserClaims {
  name?: string | null;
  displayName?: string | null;
  givenName?: string | null;
  given_name?: string | null;
  firstName?: string | null;
  first_name?: string | null;
  familyName?: string | null;
  family_name?: string | null;
  lastName?: string | null;
  last_name?: string | null;
  email?: string | null;
  phone?: string | null;
  userId?: string | null;
  sub?: string | null;
  loginIds?: string[] | null;
  customAttributes?: Record<string, unknown> | null;
  [key: string]: unknown;
}

/**
 * Extracts the user's actual Google/Descope profile display name from claims or user object.
 */
export function extractDisplayName(
  source: DescopeOrUserClaims | null | undefined,
  fallback = "Investigator"
): string {
  if (!source) return fallback;

  const email = (typeof source.email === "string" ? source.email : "").trim();
  const emailPrefix = email.includes("@") ? email.split("@")[0].toLowerCase() : "";

  // 1. Raw name check (Google / Descope full name claim)
  const rawName = (
    (typeof source.name === "string" ? source.name : "") ||
    (typeof source.displayName === "string" ? source.displayName : "")
  ).trim();

  // If rawName is present, not empty, and not an email or email username prefix
  if (
    rawName &&
    !rawName.includes("@") &&
    (!emailPrefix || rawName.toLowerCase() !== emailPrefix)
  ) {
    return rawName;
  }

  // 2. firstName + lastName / givenName + familyName
  const given = (
    (typeof source.givenName === "string" ? source.givenName : "") ||
    (typeof source.given_name === "string" ? source.given_name : "") ||
    (typeof source.firstName === "string" ? source.firstName : "") ||
    (typeof source.first_name === "string" ? source.first_name : "")
  ).trim();

  const family = (
    (typeof source.familyName === "string" ? source.familyName : "") ||
    (typeof source.family_name === "string" ? source.family_name : "") ||
    (typeof source.lastName === "string" ? source.lastName : "") ||
    (typeof source.last_name === "string" ? source.last_name : "")
  ).trim();

  if (given && family) {
    return `${given} ${family}`;
  }

  // 3. givenName / firstName alone
  if (given) {
    return given;
  }

  // 4. familyName / lastName alone
  if (family) {
    return family;
  }

  // 5. customAttributes.name
  const custom = source.customAttributes;
  if (custom && typeof custom.name === "string" && custom.name.trim()) {
    const customName = custom.name.trim();
    if (
      !customName.includes("@") &&
      (!emailPrefix || customName.toLowerCase() !== emailPrefix)
    ) {
      return customName;
    }
  }

  // 6. If rawName was provided, use it if it's not strictly an email prefix
  if (rawName && !rawName.includes("@") && rawName.toLowerCase() !== emailPrefix) {
    return rawName;
  }

  // 7. Final fallback: full email address if available, or fallback
  return email || fallback;
}

/**
 * Returns a human-friendly display name specifically for greetings and user labels.
 * Guaranteed never to return an email prefix like "akraguvaran66".
 */
export function getSafeDisplayName(
  user: { name?: string | null; email?: string | null } | null | undefined,
  fallback = "Investigator"
): string {
  if (!user) return fallback;

  const email = (user.email ?? "").trim();
  const emailPrefix = email.includes("@") ? email.split("@")[0].toLowerCase() : "";
  const name = (user.name ?? "").trim();

  // If user.name is valid and not an email prefix or full email
  if (name && !name.includes("@") && (!emailPrefix || name.toLowerCase() !== emailPrefix)) {
    return name;
  }

  // If we have an email but name was email prefix or empty
  if (email && (!emailPrefix || name.toLowerCase() !== emailPrefix) && !name.includes("@")) {
    return name;
  }

  return fallback;
}

/**
 * Computes 1-2 letter uppercase initials for user avatars.
 * Examples:
 *   "Akash M" -> "AM"
 *   "Akash" -> "A"
 *   "lead.investigator@crimekit.gov" -> "L"
 */
export function getUserInitials(nameOrEmail: string | null | undefined): string {
  if (!nameOrEmail || !nameOrEmail.trim()) return "U";

  const clean = nameOrEmail.trim();

  // If it's an email address, take the first letter
  if (clean.includes("@")) {
    return clean.charAt(0).toUpperCase();
  }

  // Split name by spaces
  const parts = clean.split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }

  // First letter of first token + first letter of last token
  const first = parts[0].charAt(0).toUpperCase();
  const last = parts[parts.length - 1].charAt(0).toUpperCase();
  return `${first}${last}`;
}
