<div align="center">

# Nullstacks

**Open-source AI tools and utilities. Small, sharp, composable.**

[![Follow](https://img.shields.io/github/followers/nullstacks?label=Follow&style=social)](https://github.com/nullstacks)

</div>

---

Tools for the browser, written in plain JavaScript. Every project here is a single-purpose utility with zero dependencies and no build step: clone it, load it, use it. Nothing to install, nothing to compile.

<img src="https://raw.githubusercontent.com/nullstacks/temp-mail-extension/main/.github/assets/screenshot-inbox.png" alt="TempMail extension popup: a disposable address with Autofill, Copy and New actions, a fake identity row and a live inbox with an OTP code chip" width="330" align="right" hspace="16">

## Projects

| | |
|---|---|
| [**temp-mail-extension**](https://github.com/nullstacks/temp-mail-extension) | Disposable email inbox for Chrome and Brave. The address stays put until you rotate it, fills any signup form in one keystroke, and surfaces verification codes as one-click chips. Manifest V3, zero dependencies. |
| [**mailapi**](https://github.com/nullstacks/mailapi) | Your own Gmail, as a REST API. Google OAuth plus per-user keys on Cloudflare Workers. Multi-account, disposable `+tag` aliases, one key. |
| [**cookie-manager**](https://github.com/nullstacks/cookie-manager) | Cookie editor for Chrome and Brave. View, add, edit, delete, import and export cookies for the current site. Manifest V3, zero dependencies. |

## How they connect

The projects compose. TempMail's optional **MyGmail** provider runs on mailapi: create an account on the Workers API once, paste the key into the extension, and your own Gmail becomes the disposable address with `+alias` and dot variants, filtered per address. The rest of the tools stand alone.

## Principles

- **Zero dependencies.** Everything the tool needs ships in the repo.
- **No build step.** Extensions load straight from source: `chrome://extensions` → Load unpacked.
- **Local-first.** Browser tools store everything in your browser. The one server component (mailapi) is a Workers deploy with your own OAuth setup, not someone else's database.
- **One tool, one job.** Each repo does a single thing well enough to be composed into something else.

## Contributing

Issues and PRs are welcome across all repos. For bug reports, include your browser and version and the affected surface.

<!--
Contact, links
-->
