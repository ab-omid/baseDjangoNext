"use client";

/**
 * Auth/session hook for login/logout and current-user hydration.
 *
 * Where: login page, admin dashboard route guard.
 * Uses: `authApi`, token helpers from `api/client`, React Query cache.
 * Behavior: fetches current user only when an access token exists; login seeds user cache.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { authApi } from "@/api/auth";
import { getAccessToken } from "@/api/client";
import type { LoginRequest } from "@/types/auth";

export function useAuth() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const [hasToken, setHasToken] = useState(false);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    setHasToken(Boolean(getAccessToken()));
    setAuthReady(true);
  }, []);

  const userQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: authApi.getCurrentUser,
    enabled: authReady && hasToken,
    staleTime: 60_000,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: (payload: LoginRequest) => authApi.login(payload),
    onSuccess: (user) => {
      setHasToken(true);
      queryClient.setQueryData(["auth", "me"], user);
      router.replace("/admin-dashboard");
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      authApi.logout();
      setHasToken(false);
      queryClient.clear();
    },
    onSuccess: () => {
      router.replace("/login");
    },
  });

  return {
    user: userQuery.data ?? null,
    authReady,
    isAuthenticated: hasToken,
    isUserLoading: !authReady || (hasToken && userQuery.isLoading),
    userError: userQuery.error,
    loginError: loginMutation.error,
    isLoginPending: loginMutation.isPending,
    login: (payload: LoginRequest) => loginMutation.mutate(payload),
    logout: () => logoutMutation.mutate(),
  };
}
