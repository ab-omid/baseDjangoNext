/**
 * Impersonation session API wrappers.
 *
 * Where: admin-only flows that may need acting as another user later.
 * Uses: `apiRequest` from `./client`.
 * Contract: POST `/impersonation/start/`, POST `/impersonation/stop/`, GET `/impersonation/status/` return envelope.
 * Behavior: relies on `credentials: "include"` in `apiRequest` so session cookie updates apply immediately.
 */

import { apiRequest, type ApiEnvelope } from "@/api/client";

export const impersonationApi = {
  async start(userUuid: string): Promise<boolean> {
    const response = await apiRequest<ApiEnvelope<boolean>>("/impersonation/start/", {
      method: "POST",
      body: JSON.stringify({ user_uuid: userUuid }),
    });
    return response.output;
  },

  async stop(): Promise<boolean> {
    const response = await apiRequest<ApiEnvelope<boolean>>("/impersonation/stop/", {
      method: "POST",
    });
    return response.output;
  },

  async status(): Promise<boolean> {
    const response = await apiRequest<ApiEnvelope<boolean>>("/impersonation/status/");
    return response.output;
  },
};
