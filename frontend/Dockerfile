# ==========================================
# Stage 1: Build Stage (Vite static compilation)
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code and build production bundle
COPY . .
RUN npm run build

# ==========================================
# Stage 2: Production Nginx Server (~25MB image)
# ==========================================
FROM nginx:alpine AS runner

# Copy compiled static HTML/JS/CSS assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx SPA proxy configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
