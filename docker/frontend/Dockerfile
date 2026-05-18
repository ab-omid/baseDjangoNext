FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY ui/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY ui/ ./

# Expose port 5000 (matches vite.config.ts)
EXPOSE 5000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]