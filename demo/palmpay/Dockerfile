FROM node:24-alpine AS frontend
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps ./apps
COPY packages ./packages
RUN npm install -g pnpm@12
RUN pnpm install --frozen-lockfile
COPY index.html vite.config.ts tsconfig.json playwright.config.ts ./
COPY public ./public
RUN pnpm build

FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY backend ./backend
COPY alembic.ini .
COPY --from=frontend /app/dist ./dist
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn backend.main:app --host 0.0.0.0 --port 8000"]

