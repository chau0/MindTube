# SECURITY & SECRETS

- Do not log secrets or full URLs with tokens.
- Env-only secrets: Azure OpenAI keys, any API credentials.
- Client-side keys stored only in browser; provide 'forget key' control.
- Minimal PII; no server-side user history by default.
- Dependencies: pin versions; run vulnerability scans regularly.
