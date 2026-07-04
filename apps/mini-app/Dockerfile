FROM node:22-alpine AS runtime

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY --chown=app:app package.json package-lock.json ./
RUN npm ci

COPY --chown=app:app index.html tsconfig.json tsconfig.node.json vite.config.ts ./
COPY --chown=app:app src ./src
RUN chown -R app:app /app

USER app

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
