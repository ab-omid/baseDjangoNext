/**
 * Admin-facing user CRUD and profile API key management wrappers.
 *
 * Where: admin dashboard user management surface (`/admin-dashboard`).
 * Uses: `apiRequest` from `./client`.
 * Contract:
 * - GET `/user/?search=&page_token=&max_results=` -> envelope output with paginated users
 * - POST `/user/create/` -> envelope output user
 * - PATCH `/user/:user_uuid/update/` -> envelope output user
 * - DELETE `/user/:user_uuid/delete/` -> envelope output `{ message }`
 * - API key (admin own): GET `/user/api-key/`, POST `/user/api-key/generate/`, DELETE `/user/api-key/revoke/`
 * Behavior: all methods return `response.output` and throw `ApiError` on envelope/http errors.
 */

import { apiRequest, type ApiEnvelope } from "@/api/client";
import type {
  ApiKeyInfo,
  CreateUserInput,
  PaginatedOutput,
  UpdateUserInput,
  UserListQuery,
} from "@/types/admin";
import type { User } from "@/types/auth";

export const adminUsersApi = {
  async listUsers(query: UserListQuery = {}): Promise<PaginatedOutput<User>> {
    const params = new URLSearchParams();
    if (query.search) {
      params.set("search", query.search);
    }
    if (query.page_token) {
      params.set("page_token", query.page_token);
    }
    params.set("max_results", String(query.max_results ?? 20));

    const response = await apiRequest<ApiEnvelope<PaginatedOutput<User>>>(
      `/user/?${params.toString()}`,
    );
    return response.output;
  },

  async createUser(payload: CreateUserInput): Promise<User> {
    const response = await apiRequest<ApiEnvelope<User>>("/user/create/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return response.output;
  },

  async updateUser(userKey: string, payload: UpdateUserInput): Promise<User> {
    const response = await apiRequest<ApiEnvelope<User>>(`/user/${userKey}/update/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    return response.output;
  },

  async deleteUser(userKey: string): Promise<{ message: string }> {
    const response = await apiRequest<ApiEnvelope<{ message: string }>>(
      `/user/${userKey}/delete/`,
      { method: "DELETE" },
    );
    return response.output;
  },

  async getOwnApiKey(): Promise<ApiKeyInfo | null> {
    const response = await apiRequest<ApiEnvelope<ApiKeyInfo | null>>("/user/api-key/");
    return response.output;
  },

  async generateOwnApiKey(payload: { name?: string; scopes?: string[] } = {}): Promise<ApiKeyInfo> {
    const response = await apiRequest<ApiEnvelope<ApiKeyInfo>>("/user/api-key/generate/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return response.output;
  },

  async revokeOwnApiKey(): Promise<{ message: string }> {
    const response = await apiRequest<ApiEnvelope<{ message: string }>>("/user/api-key/revoke/", {
      method: "DELETE",
    });
    return response.output;
  },
};
