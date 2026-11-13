# Stage 1: build the frontend if frontend/package.json exists; otherwise copy the static frontend/dist
# (the current dashboard is plain HTML/JS with no build step).
FROM node:20-slim AS web
WORKDIR /src
COPY . /src
RUN mkdir -p /out && \
    if [ -f frontend/package.json ]; then \
      cd frontend && npm ci && npm run build && cp -r dist/. /out/ ; \
    elif [ -d frontend/dist ]; then \
      cp -r frontend/dist/. /out/ ; \
    fi

# Stage 2: the API (serves frontend/dist when it has content).
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/
COPY data/curated/ data/curated/
COPY --from=web /out /app/frontend/dist
# An empty dist folder would hide the JSON root, so drop it when nothing was built.
RUN [ -n "$(ls -A frontend/dist 2>/dev/null)" ] || rm -rf frontend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
