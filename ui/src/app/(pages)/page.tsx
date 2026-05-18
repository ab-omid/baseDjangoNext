import { Box, Typography } from "@mui/material";

/**
 * Renders the home page content at the root route.
 *
 * Where: `/` in the App Router pages group
 * Uses: Material UI `Box` and `Typography`
 * Behavior: Shows a centered hello-world heading
 */
export default function HomeRoutePage() {
  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
      }}
    >
      <Typography component="h1" variant="h4">
        Hello World
      </Typography>
    </Box>
  );
}
