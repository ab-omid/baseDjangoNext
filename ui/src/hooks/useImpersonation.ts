"use client";

/**
 * Loads impersonation status and exposes stop/start actions.
 *
 * Where: admin dashboard banners and future user-context controls.
 * Uses: `impersonationApi` and React Query.
 * Behavior: status query is disabled by default and can be refreshed on demand.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { impersonationApi } from "@/api/impersonation";

export function useImpersonation() {
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ["impersonation", "status"],
    queryFn: impersonationApi.status,
    staleTime: 30_000,
  });

  const stopMutation = useMutation({
    mutationFn: impersonationApi.stop,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["impersonation", "status"] });
      await queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  return {
    isImpersonating: statusQuery.data === true,
    isStatusLoading: statusQuery.isLoading,
    stopImpersonation: () => stopMutation.mutate(),
    isStopPending: stopMutation.isPending,
  };
}
