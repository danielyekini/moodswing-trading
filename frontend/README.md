# MoodSwing Trading — Frontend

A Vite + React (TypeScript) single-page application for the MoodSwing Trading demo. It renders a landing page and a dashboard with a stock chart, live WebSocket ticks, and a news feed backed by the FastAPI service.

## Prerequisites

- Node.js 18+ (Vite 5 requires Node 18 or newer)
- npm 8+ (or another compatible package manager)

## Quick start

```bash
# From repository root
cd frontend

# Install dependencies
npm install

# Start the dev server (http://localhost:5173)
npm run dev
```

If you also want live API data, start the backend (from repo root):

```bash
# Start API + dependencies on http://localhost:8000
docker compose up -d api
```

## Available scripts

- `npm run dev`: Start the Vite dev server on http://localhost:5173
- `npm run build`: Type-check then build production assets into `dist/`
- `npm run preview`: Preview the production build locally
- `npm run lint`: Run ESLint on JS/JSX sources
- `npm run lint:fix`: Auto-fix lint issues for JS/JSX/TS/TSX

## Project structure (high level)

```
frontend/
├─ public/                 # Static assets copied to build as-is
├─ src/
│  ├─ pages/
│  │  ├─ LandingPage.tsx   # Marketing/landing shell
│  │  └─ DashboardPage.tsx # App dashboard shell
│  ├─ components/
│  │  ├─ StockChart.tsx    # Highcharts-based price chart + WS live ticks
│  │  └─ NewsFeed.tsx      # News list fetched from API
│  ├─ App.tsx              # Routes ("/" and "/dashboard")
│  ├─ main.tsx             # App bootstrap (React + Router)
│  └─ index.css            # Global styles
├─ vite.config.ts          # Vite + React plugin, alias '@' -> '/src'
├─ package.json            # Scripts and dependencies
└─ dist/                   # Production build output (after `npm run build`)
```

For more layout notes, see `frontend/SETUP.md`.

## Configuration

The frontend expects the API at `http://127.0.0.1:8000` by default.
- REST used in `src/components/NewsFeed.tsx`:
  - `GET http://127.0.0.1:8000/api/v1/news/{ticker}?limit=10`
- REST used in `src/components/StockChart.tsx`:
  - `GET http://127.0.0.1:8000/api/v1/stocks/{ticker}/history?...`
- WebSocket used in `src/components/StockChart.tsx`:
  - `ws://127.0.0.1:8000/api/v1/stocks/{ticker}/stream?interval=5`

If your API is not running on `127.0.0.1:8000`, update the URLs in those files or introduce an environment variable (recommended). With Vite, you can define `VITE_*` variables in `.env` files and read them via `import.meta.env`:

```ts
// example pattern (not yet wired in code)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
```

To deploy under a subpath (e.g., `/app/`), set `base` in `vite.config.ts` and rebuild.

## Routes

- `/` — Landing page
- `/dashboard` — Dashboard with chart, news feed, and placeholders

The app uses `<BrowserRouter>`. Ensure your production server serves `index.html` for unknown routes (SPA fallback).

## Build and deploy

```bash
npm run build
# Output written to frontend/dist/
```

You can serve `dist/` with any static host (Nginx, Netlify, Vercel, GitHub Pages). For an on-device check:

```bash
npm run preview
# Serves the built app on a local port (shown in the console)
```

## Linting

```bash
# Report issues
npm run lint

# Attempt fixes
npm run lint:fix
```

## Troubleshooting

- CORS errors: ensure the backend allows your frontend origin. In development, the API enables permissive CORS (`ALLOWED_ORIGINS: "*"`).
- API 4xx/5xx: verify the FastAPI service is running at `http://localhost:8000` and routes exist (`/docs` for Swagger).
- WebSocket shows "market-closed": live ticks purposely connect only during US market hours; outside hours, the chart falls back to historical data and placeholders.
- Blank chart: the chart initializes after historical data loads; check network requests in DevTools for errors.

## License

See the repository `LICENSE` file.


