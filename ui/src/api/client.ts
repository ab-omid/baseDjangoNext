/**
 * Shared fetch client for Django API with JWT + refresh + impersonation-session support.
 *
 * Where: imported by every `ui/src/api/*.ts` module.
 * Uses: browser `localStorage` for access/refresh tokens and `fetch`.
 * Contract: calls `${API_BASE}${path}`; expects JSON envelope `{ output, error, error_messages, http_response_code }`
 *   for application APIs, while auth endpoints (`/token/`, `/token/refresh/`) return raw JWT payloads.
 * Behavior: attaches `Authorization: Bearer <access>`; includes `credentials: "include"` on every request so
 *   impersonation session cookies stay in sync; on 401 attempts one refresh then retries original request.
 * Invariants: refresh token is sent in body `{ refresh }`; failed refresh clears tokens.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001/api";

export interface ApiEnvelope<TOutput> {
  output: TOutput;
  error: boolean;
  http_response_code: number;
  error_messages: string[];
}

export class ApiError extends Error {
  statusCode: number;

  errorMessages: string[];

  constructor(message: string, statusCode: number, errorMessages: string[] = []) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorMessages = errorMessages;
  }
}

const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";

function getStorageItem(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(key);
}

function setStorageItem(key: string, value: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(key, value);
}

function removeStorageItem(key: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(key);
}

export function getAccessToken(): string | null {
  return getStorageItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return getStorageItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  setStorageItem(ACCESS_TOKEN_KEY, accessToken);
  setStorageItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  removeStorageItem(ACCESS_TOKEN_KEY);
  removeStorageItem(REFRESH_TOKEN_KEY);
}

function buildUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE}${path}`;
}

async function parseJson<T>(response: Response): Promise<T | null> {
  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    return null;
  }
  return (await response.json()) as T;
}

function extractErrorMessages(payload: unknown): string[] {
  if (!payload) {
    return [];
  }

  if (typeof payload === "string") {
    return [payload];
  }

  if (typeof payload !== "object") {
    return [];
  }

  const record = payload as Record<string, unknown>;

  const envelopeErrors = record.error_messages;
  if (Array.isArray(envelopeErrors)) {
    return envelopeErrors.map((item) => String(item)).filter(Boolean);
  }

  const nonFieldErrors = record.non_field_errors;
  if (Array.isArray(nonFieldErrors)) {
    return nonFieldErrors.map((item) => String(item)).filter(Boolean);
  }

  if (typeof record.detail === "string") {
    return [record.detail];
  }

  const flattened: string[] = [];
  for (const [field, value] of Object.entries(record)) {
    if (Array.isArray(value)) {
      for (const item of value) {
        flattened.push(`${field}: ${String(item)}`);
      }
      continue;
    }
    if (typeof value === "string") {
      flattened.push(`${field}: ${value}`);
    }
  }
  return flattened;
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  const refreshResponse = await fetch(buildUrl("/token/refresh/"), {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!refreshResponse.ok) {
    clearTokens();
    return null;
  }

  const refreshJson = await parseJson<{ access?: string }>(refreshResponse);
  const nextAccessToken = refreshJson?.access;
  if (!nextAccessToken) {
    clearTokens();
    return null;
  }

  setTokens(nextAccessToken, refreshToken);
  return nextAccessToken;
}

export async function apiRequest<TResponse>(
  path: string,
  init: RequestInit = {},
  options: { retryOnUnauthorized?: boolean } = {},
): Promise<TResponse> {
  const retryOnUnauthorized = options.retryOnUnauthorized ?? true;
  const token = getAccessToken();

  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path), {
    ...init,
    headers,
    credentials: "include",
  });

  if (response.status === 401 && retryOnUnauthorized) {
    const nextAccessToken = await refreshAccessToken();
    if (nextAccessToken) {
      return apiRequest<TResponse>(
        path,
        {
          ...init,
          headers: {
            ...(init.headers || {}),
            Authorization: `Bearer ${nextAccessToken}`,
          },
        },
        { retryOnUnauthorized: false },
      );
    }
  }

  const responseJson = await parseJson<TResponse | ApiEnvelope<unknown>>(response);
  if (!response.ok) {
    const errorMessages = extractErrorMessages(responseJson);
    const message = errorMessages[0] ?? `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, errorMessages);
  }

  if (responseJson === null) {
    throw new ApiError("Expected JSON response body", response.status);
  }

  return responseJson as TResponse;
}
