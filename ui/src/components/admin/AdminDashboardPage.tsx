"use client";

/**
 * First admin dashboard page with user management and profile API key tools.
 *
 * Where: mounted by `/admin-dashboard`.
 * Uses: `useAuth`, `useImpersonation`, `adminUsersApi`, MUI tables/forms, React Query mutations.
 * Behavior: admin-only view; supports user search/list/create/update/delete and own API key generate/revoke.
 * Invariants: API key actions target the authenticated admin profile (not other users).
 */

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { adminUsersApi } from "@/api/admin-users";
import { ApiError } from "@/api/client";
import { useAuth } from "@/hooks/useAuth";
import { useImpersonation } from "@/hooks/useImpersonation";
import type { CreateUserInput, UpdateUserInput } from "@/types/admin";
import type { User } from "@/types/auth";

const USER_STATUSES = ["ACTIVE", "SUSPENDED", "DELETED"] as const;

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.errorMessages[0] ?? error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
}

export function AdminDashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, authReady, isAuthenticated, isUserLoading, userError, logout } = useAuth();
  const { isImpersonating, isStatusLoading, stopImpersonation, isStopPending } = useImpersonation();

  const [search, setSearch] = useState("");
  const [createForm, setCreateForm] = useState<CreateUserInput>({
    name: "",
    email: "",
    password: "",
    status: "ACTIVE",
    is_staff: false,
    is_superuser: false,
  });
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editForm, setEditForm] = useState<UpdateUserInput>({});
  const [apiKeyLabel, setApiKeyLabel] = useState("Admin Default");
  const [apiKeyRaw, setApiKeyRaw] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!authReady || isUserLoading) {
      return;
    }
    if (!isAuthenticated || userError) {
      router.replace("/login");
    }
  }, [authReady, isAuthenticated, isUserLoading, router, userError]);

  const isAdminUser = Boolean(user?.is_staff || user?.is_superuser);

  const usersQuery = useQuery({
    queryKey: ["admin", "users", search],
    queryFn: () => adminUsersApi.listUsers({ search, max_results: 25 }),
    enabled: isAuthenticated && isAdminUser,
  });

  const apiKeyQuery = useQuery({
    queryKey: ["admin", "profile-api-key"],
    queryFn: () => adminUsersApi.getOwnApiKey(),
    enabled: isAuthenticated && isAdminUser,
  });

  const createUserMutation = useMutation({
    mutationFn: (payload: CreateUserInput) => adminUsersApi.createUser(payload),
    onSuccess: async () => {
      setSuccessMessage("User created successfully.");
      setCreateForm({
        name: "",
        email: "",
        password: "",
        status: "ACTIVE",
        is_staff: false,
        is_superuser: false,
      });
      await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ userKey, payload }: { userKey: string; payload: UpdateUserInput }) =>
      adminUsersApi.updateUser(userKey, payload),
    onSuccess: async () => {
      setSuccessMessage("User updated successfully.");
      setEditingUser(null);
      await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: (userKey: string) => adminUsersApi.deleteUser(userKey),
    onSuccess: async () => {
      setSuccessMessage("User deleted successfully.");
      await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });

  const generateApiKeyMutation = useMutation({
    mutationFn: () => adminUsersApi.generateOwnApiKey({ name: apiKeyLabel, scopes: ["READ", "WRITE"] }),
    onSuccess: async (result) => {
      setApiKeyRaw(result.raw_key ?? null);
      setSuccessMessage("API key generated successfully. Save the raw key now.");
      await queryClient.invalidateQueries({ queryKey: ["admin", "profile-api-key"] });
    },
  });

  const revokeApiKeyMutation = useMutation({
    mutationFn: () => adminUsersApi.revokeOwnApiKey(),
    onSuccess: async () => {
      setApiKeyRaw(null);
      setSuccessMessage("API key revoked successfully.");
      await queryClient.invalidateQueries({ queryKey: ["admin", "profile-api-key"] });
    },
  });

  const combinedError = useMemo(() => {
    return (
      usersQuery.error ||
      apiKeyQuery.error ||
      createUserMutation.error ||
      updateUserMutation.error ||
      deleteUserMutation.error ||
      generateApiKeyMutation.error ||
      revokeApiKeyMutation.error
    );
  }, [
    usersQuery.error,
    apiKeyQuery.error,
    createUserMutation.error,
    updateUserMutation.error,
    deleteUserMutation.error,
    generateApiKeyMutation.error,
    revokeApiKeyMutation.error,
  ]);

  const users = usersQuery.data?.items ?? [];

  if (!authReady || isUserLoading) {
    return (
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return (
      <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAdminUser) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Access denied: this page is only for admin/staff users.
        </Alert>
        <Button variant="outlined" onClick={logout}>
          Logout
        </Button>
      </Box>
    );
  }

  const handleCreateSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccessMessage(null);
    createUserMutation.mutate({
      ...createForm,
      email: createForm.email.trim().toLowerCase(),
      name: createForm.name.trim(),
    });
  };

  return (
    <Box component="main" sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: "auto" }}>
        <Stack
          direction="row"
          sx={{ mb: 2, justifyContent: "space-between", alignItems: "center" }}
        >
          <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
              Admin Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Initial admin control page (users + profile API key)
            </Typography>
          </Box>
          <Button variant="outlined" onClick={logout}>
            Logout
          </Button>
        </Stack>

        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {successMessage}
          </Alert>
        )}
        {combinedError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {getErrorMessage(combinedError)}
          </Alert>
        )}
        {!isStatusLoading && isImpersonating && (
          <Alert
            severity="warning"
            sx={{ mb: 2 }}
            action={
              <Button color="inherit" size="small" onClick={stopImpersonation} disabled={isStopPending}>
                Stop impersonation
              </Button>
            }
          >
            Impersonation is active in this browser session.
          </Alert>
        )}

        <Stack spacing={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                My API Key
              </Typography>
              <Stack
                direction={{ xs: "column", md: "row" }}
                spacing={2}
                sx={{ alignItems: { md: "center" } }}
              >
                <TextField
                  label="Key Label"
                  value={apiKeyLabel}
                  onChange={(event) => setApiKeyLabel(event.target.value)}
                  size="small"
                />
                <Button
                  variant="contained"
                  onClick={() => generateApiKeyMutation.mutate()}
                  disabled={generateApiKeyMutation.isPending}
                >
                  Generate New Key
                </Button>
                <Button
                  color="error"
                  variant="outlined"
                  onClick={() => revokeApiKeyMutation.mutate()}
                  disabled={revokeApiKeyMutation.isPending || !apiKeyQuery.data}
                >
                  Revoke Key
                </Button>
              </Stack>
              <Stack spacing={1} sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Current key prefix: {apiKeyQuery.data?.prefix ?? "No active key"}
                </Typography>
                {apiKeyRaw && (
                  <Alert severity="warning">
                    Raw key (shown once):{" "}
                    <Typography component="span" sx={{ fontWeight: 700 }}>
                      {apiKeyRaw}
                    </Typography>
                  </Alert>
                )}
              </Stack>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Create User
              </Typography>
              <Stack component="form" onSubmit={handleCreateSubmit} spacing={2}>
                <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                  <TextField
                    fullWidth
                    label="Name"
                    value={createForm.name}
                    onChange={(event) => setCreateForm((prev) => ({ ...prev, name: event.target.value }))}
                    required
                  />
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={createForm.email}
                    onChange={(event) => setCreateForm((prev) => ({ ...prev, email: event.target.value }))}
                    required
                  />
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={createForm.password}
                    onChange={(event) => setCreateForm((prev) => ({ ...prev, password: event.target.value }))}
                    required
                  />
                </Stack>
                <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                  <FormControl sx={{ minWidth: 180 }}>
                    <InputLabel id="create-user-status-label">Status</InputLabel>
                    <Select
                      labelId="create-user-status-label"
                      label="Status"
                      value={createForm.status ?? "ACTIVE"}
                      onChange={(event) =>
                        setCreateForm((prev) => ({ ...prev, status: event.target.value }))
                      }
                    >
                      {USER_STATUSES.map((status) => (
                        <MenuItem key={status} value={status}>
                          {status}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(createForm.is_staff)}
                        onChange={(event) =>
                          setCreateForm((prev) => ({ ...prev, is_staff: event.target.checked }))
                        }
                      />
                    }
                    label="is_staff"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={Boolean(createForm.is_superuser)}
                        onChange={(event) =>
                          setCreateForm((prev) => ({ ...prev, is_superuser: event.target.checked }))
                        }
                      />
                    }
                    label="is_superuser"
                  />
                  <Button type="submit" variant="contained" disabled={createUserMutation.isPending}>
                    Create
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Stack direction={{ xs: "column", md: "row" }} spacing={2} sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ flex: 1 }}>
                  Users
                </Typography>
                <TextField
                  label="Search users"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  size="small"
                />
              </Stack>
              <Divider sx={{ mb: 2 }} />

              {usersQuery.isLoading ? (
                <Box sx={{ py: 4, display: "flex", justifyContent: "center" }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Roles</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {users.map((row) => (
                      <TableRow key={row.key}>
                        <TableCell>{row.name}</TableCell>
                        <TableCell>{row.email}</TableCell>
                        <TableCell>{row.status}</TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1}>
                            {row.is_staff && <Chip size="small" label="staff" />}
                            {row.is_superuser && <Chip size="small" label="superuser" color="secondary" />}
                          </Stack>
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} sx={{ justifyContent: "flex-end" }}>
                            <Button
                              size="small"
                              onClick={() => {
                                setEditingUser(row);
                                setEditForm({
                                  name: row.name,
                                  email: row.email,
                                  status: row.status,
                                  is_staff: row.is_staff,
                                  is_superuser: row.is_superuser,
                                });
                              }}
                            >
                              Edit
                            </Button>
                            <Button
                              size="small"
                              color="error"
                              onClick={() => deleteUserMutation.mutate(row.key)}
                              disabled={deleteUserMutation.isPending || row.key === user?.key}
                            >
                              Delete
                            </Button>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Stack>

      <Dialog open={Boolean(editingUser)} onClose={() => setEditingUser(null)} fullWidth maxWidth="sm">
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={editForm.name ?? ""}
              onChange={(event) => setEditForm((prev) => ({ ...prev, name: event.target.value }))}
              fullWidth
            />
            <TextField
              label="Email"
              type="email"
              value={editForm.email ?? ""}
              onChange={(event) => setEditForm((prev) => ({ ...prev, email: event.target.value }))}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel id="edit-user-status-label">Status</InputLabel>
              <Select
                labelId="edit-user-status-label"
                label="Status"
                value={editForm.status ?? "ACTIVE"}
                onChange={(event) => setEditForm((prev) => ({ ...prev, status: event.target.value }))}
              >
                {USER_STATUSES.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Switch
                  checked={Boolean(editForm.is_staff)}
                  onChange={(event) =>
                    setEditForm((prev) => ({ ...prev, is_staff: event.target.checked }))
                  }
                />
              }
              label="is_staff"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={Boolean(editForm.is_superuser)}
                  onChange={(event) =>
                    setEditForm((prev) => ({ ...prev, is_superuser: event.target.checked }))
                  }
                />
              }
              label="is_superuser"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingUser(null)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (!editingUser) {
                return;
              }
              updateUserMutation.mutate({ userKey: editingUser.key, payload: editForm });
            }}
            disabled={updateUserMutation.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
