/**
 * Authentication endpoints for admin login/session bootstrap.
 *
 * Where: `LoginPage` and auth guard checks in admin routes.
 * Uses: `apiRequest` + token helpers from `./client`.
 * Contract: POST `/token/` returns raw `{ access, refresh, user }`; GET `/user/profile/` returns envelope with `output`.
 * Behavior: successful login persists JWT tokens; logout only clears local tokens.
 * Invariants: backend username field is email, so login sends `email`.
 */

import { apiRequest, clearTokens, setTokens, type ApiEnvelope } from "@/api/client";
import type { LoginRequest, LoginResponse, User } from "@/types/auth";

export const authApi = {
  async login(payload: LoginRequest): Promise<User> {
    const response = await apiRequest<LoginResponse>("/token/", {
      method: "POST",
      body: JSON.stringify({
        email: payload.email,
        password: payload.password,
      }),
    });
    setTokens(response.access, response.refresh);
    return response.user;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiRequest<ApiEnvelope<User>>("/user/profile/");
    return response.output;
  },

  logout(): void {
    clearTokens();
  },
};
