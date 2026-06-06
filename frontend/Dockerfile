# Stage 1: Build the Next.js app
# CHANGE: node:18-alpine ko node:20-alpine kar diya
FROM node:20-alpine AS builder
WORKDIR /app

# Building for production (Inject environment variable)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
# ARG NEXT_PUBLIC_API_URL=https://samirk10-medical-ai-backend.hf.space

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Run the app
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]