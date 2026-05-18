"use client";

/**
 * Admin login screen for obtaining JWT credentials.
 *
 * Where: mounted by `/login` route.
 * Uses: `useAuth`, MUI form controls.
 * Behavior: submits email/password, persists session via auth hook, shows API errors inline.
 */

import { KeyboardEvent, useState } from "react";
import {
  Alert,
  Box,
  Button,
  FormControl,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { Email, Lock } from "@mui/icons-material";

import { ApiError } from "@/api/client";
import { useAuth } from "@/hooks/useAuth";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.errorMessages[0] ?? error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Login failed";
}

export function LoginPage() {
  const { login, isLoginPending, loginError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submitLogin = () => {
    if (!email.trim() || !password) {
      return;
    }
    login({ email: email.trim().toLowerCase(), password });
  };

  const handleEnterSubmit = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submitLogin();
    }
  };

  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        px: 2,
      }}
    >
      <Paper elevation={2} sx={{ width: "100%", maxWidth: 420, p: 4 }}>
          <Stack spacing={2}>
          <Typography component="h1" variant="h5" sx={{ fontWeight: 700 }}>
            Admin Login
          </Typography>
          <FormControl variant="outlined" required>
            <InputLabel htmlFor="login-email">Email</InputLabel>
            <OutlinedInput
              id="login-email"
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              disabled={isLoginPending}
              onKeyDown={handleEnterSubmit}
              startAdornment={
                <InputAdornment position="start">
                  <Email fontSize="small" />
                </InputAdornment>
              }
            />
          </FormControl>
          <FormControl variant="outlined" required>
            <InputLabel htmlFor="login-password">Password</InputLabel>
            <OutlinedInput
              id="login-password"
              label="Password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              disabled={isLoginPending}
              onKeyDown={handleEnterSubmit}
              startAdornment={
                <InputAdornment position="start">
                  <Lock fontSize="small" />
                </InputAdornment>
              }
            />
          </FormControl>
          {loginError && <Alert severity="error">{getErrorMessage(loginError)}</Alert>}
          <Button variant="contained" disabled={isLoginPending} onClick={submitLogin}>
            {isLoginPending ? "Signing in..." : "Sign in"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
