# ==============================================================================
# IBVAP Frontend - Multi-Stage Production Dockerfile
# Stage 1: Build React 19 TypeScript application via Vite
# Stage 2: Serve static production bundle with Nginx reverse proxy
# ==============================================================================

# --- Stage 1: Build ---
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy source files
COPY frontend ./

# Build production bundle
RUN npm run build

# --- Stage 2: Production Server ---
FROM nginx:alpine

# Copy built static artifacts
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
