# True Detective browser frontend

From the repository root, start the backend with its documented command:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

For first-time backend setup, see the root README.

In another terminal:

```powershell
cd web-frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

`VITE_API_URL` defaults to `http://127.0.0.1:8000`. Set it in `.env.local` to
change servers, then restart Vite. Use frontend port 5173 to match backend CORS.
On Windows with restricted PowerShell scripts, use `npm.cmd` instead of `npm`.

Text and links both send JSON `{ "content": "...", "language": "en" }` to
`POST /verify`. Only backend responses determine the displayed risk. Failures,
invalid responses, and 30-second timeouts show a retry message; mock data is
never used automatically. Images and multi-turn sessions are not yet supported.
Returned sources and clarification questions are displayed, but there is no
conversation reply mechanism until the backend implements one.

Checks: `npm run lint` and `npm run build`.

Integration checks (with the backend running):

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
node tests/api-integration.mjs
```

If Windows rejects port 8000, start Uvicorn with `--port 8001`, and use
`VITE_API_URL=http://127.0.0.1:8001` in `.env.local` and the test command.
The integration checks cover real text/link responses, both CORS origins,
request completion timing, and simulated network/HTTP/malformed-response failures.

