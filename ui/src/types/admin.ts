/**
 * Types for admin-facing user and API key operations.
 *
 * Where: `admin-users` API module and admin dashboard UI.
 * Uses: `User` type from `types/auth`.
 * Behavior: type-only module; no runtime logic.
 */

import type { User } from "@/types/auth";

export interface PaginatedOutput<TItem> {
  items: TItem[];
  next_page_token: string | null;
  previous_page_token: string | null;
  total_results: number | null;
}

export interface UserListQuery {
  search?: string;
  page_token?: string;
  max_results?: number;
}

export interface CreateUserInput {
  name: string;
  email: string;
  password: string;
  status?: string;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface UpdateUserInput {
  name?: string;
  email?: string;
  status?: string;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface ApiKeyInfo {
  key: string;
  name: string;
  prefix: string;
  scopes: string[];
  last_used_at: string | null;
  created_at: string;
  type: string;
  raw_key?: string;
}

export interface UserRowState extends User {
  isEditing?: boolean;
}
