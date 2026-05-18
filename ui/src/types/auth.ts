/**
 * Auth-related TypeScript shapes (current user, login payload, token pair).
 *
 * Where: `useAuth`, `Login`/`Logout`, and API modules handling session.
 * Uses: embeds optional `UserStatistics` from `types/team`.
 * Behavior: types only — mirrors auth API serializers.
 */


export interface User {
  key: string;
  email: string;
  name: string;
  status: string;
  profile_image: string | null;
  is_staff: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface TokenRefreshRequest {
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
}
