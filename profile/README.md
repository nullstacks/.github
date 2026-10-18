# Nullstacks

Open-source AI tools and utilities. Small, sharp, composable.

## Model gateways

OpenAI/Anthropic-compatible APIs on Cloudflare Workers — plug any harness (Claude Code, Codex CLI, Aider, curl, …) into free model tiers.

- **[kilo-gateway](https://github.com/nullstacks/kilo-gateway)** — Kilo Gateway's free models, keyless: transparent proxy + auto-refreshing free-model catalog (17 models)
- **[opencode-gateway](https://github.com/nullstacks/opencode-gateway)** — OpenCode models (incl. free tier) in any harness, no OpenCode account or API key needed
- **[cline2api](https://github.com/nullstacks/cline2api)** — Cline's free models as an API, with a catalog that auto-refreshes from Cline every 10 min
- **[qoder2api](https://github.com/nullstacks/qoder2api)** — Qoder (international) as a self-hosted OpenAI-compatible API — 16 models (Kimi-K3, GLM-5.3, DeepSeek V4.1, Qwen3.7-Max), device-flow login

## APIs & services

- **[mailapi](https://github.com/nullstacks/mailapi)** — your Gmail, as a REST API: Google OAuth + per-user keys on Cloudflare Workers, multi-account, disposable +tag aliases, one key
- **[heardlist](https://github.com/nullstacks/heardlist)** — free public proxy-list API ([live](https://heardlist.pushkarsingh4343.workers.dev)): hourly-refreshed pool of HTTP/SOCKS proxies, JSON/TXT/CSV output, no API key

## Browser extensions

- **[temp-mail-extension](https://github.com/nullstacks/temp-mail-extension)** — disposable email for Chrome & Brave: constant address until you rotate it, one-click form autofill, live inbox with OTP copy. Powered by the free temp.tf API (MV3, zero dependencies)
- **[cookie-manager](https://github.com/nullstacks/cookie-manager)** — cookie editor for Chrome & Brave: view, add, edit, delete, import & export cookies for the current site (MV3, zero dependencies, no build step)

## Contact

Open an issue, or email [help.pushkar@gmail.com](mailto:help.pushkar@gmail.com).
