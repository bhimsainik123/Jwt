# JWT API (cleaned)

API-only version. Telegram, admin forwarding, GitHub token/upload, scheduling, local credential storage, and the hidden verification service were removed.

## POST /api/jwt

```json
{"uid":"123456789","password":"..."}
```

If `API_KEY` is configured, send `X-API-Key`.

Run:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Credentials are not intentionally persisted or logged by this API. Use HTTPS and a strong API key before public deployment.
