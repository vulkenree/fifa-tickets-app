FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Debug: Show current directory and files
RUN echo "=== Current directory ===" && pwd
RUN echo "=== Root files ===" && ls -la
RUN echo "=== Components directory ===" && ls -la components/
RUN echo "=== Components/ui directory ===" && ls -la components/ui/
RUN echo "=== Lib directory ===" && ls -la lib/ || echo "lib directory does not exist!"
RUN echo "=== Lib contents ===" && ls -la lib/* || echo "lib directory is empty or does not exist!"
RUN echo "=== Check if utils.ts exists ===" && test -f lib/utils.ts && echo "utils.ts EXISTS" || echo "utils.ts DOES NOT EXIST"
RUN echo "=== Show utils.ts content ===" && cat lib/utils.ts || echo "Cannot read utils.ts"
RUN echo "=== App directory ===" && ls -la app/
RUN echo "=== Hooks directory ===" && ls -la hooks/

# Debug: Show tsconfig and jsconfig
RUN echo "tsconfig.json:" && cat tsconfig.json && echo "jsconfig.json:" && cat jsconfig.json

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["node", "server.js"]
