/** Common, framework-agnostic types shared across the CrimeKit frontend. */

export type ID = string;

/** ISO 8601 datetime string returned by the backend. */
export type ISOString = string;

/** Generic JSON object. */
export type Dict<T = unknown> = Record<string, T>;

/** Nullable helper. */
export type Nullable<T> = T | null;

/** Pagination parameters accepted by list endpoints. */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/** Generic paginated envelope. */
export interface PaginatedResponse<T> {
  items: T[];
  total?: number;
  page?: number;
  page_size?: number;
}

export interface SortParams {
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

/** Detail payload returned by the backend for errors. */
export type ErrorDetail = string | { message?: string; errors?: string[] };

/** Standard error body shape used across CrimeKit API routes. */
export interface ApiErrorBody {
  detail?: ErrorDetail;
}

export type ThemeMode = "light" | "dark" | "system";
