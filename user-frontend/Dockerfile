FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Copy built assets
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./

# We only need production dependencies, but SvelteKit's build output for node adapter 
# usually has a standalone server in build/index.js.
# No need to npm install here as the build directory has everything bundled, 
# except we might need some runtime deps depending on the app.
# Since it's a basic app, running the index.js is sufficient.
# Actually, node adapter might require some production dependencies to be installed.
# We'll install production dependencies just in case.
RUN npm install --omit=dev

EXPOSE 3000

ENV PORT=3000
ENV NODE_ENV=production

CMD ["node", "build/index.js"]
