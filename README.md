# Colour Mixer — macOS build

One arm64 `.app` (Apple Silicon only) built on GitHub
Actions. Trigger: Actions → build-macos → Run workflow, or push a `mac-v*` tag.

## Layout
- `viewer.py` — pywebview wrapper (loopback server, fixed port 8517,
  Host-check, `private_mode=False` + storage_path for localStorage persistence)
- `prepare_build.py` — copies canonical HTML → `build_src/index.html`,
  patches the Three.js CDN tag to local, vendors sha256-pinned three.min.js (r128)
- `colourmixer.spec` — PyInstaller arm64 onedir → `Colour Mixer.app`
- `requirements.txt` — pinned deps (pyobjc arrives via pywebview)

## Updating
- New canonical HTML: update `HTML_SOURCE` in the workflow. If the Three.js
  CDN tag ever changes, `prepare_build.py` fails its count==1 assertion —
  update `CDN_TAG` there.
- New Python: bump `PYTHON_VERSION` in the workflow.

## Known limits
- Ad-hoc signed only: first launch needs right-click → Open (Gatekeeper).
  SignPath / Developer ID signing is the durable fix.
- No icon asset yet (`icon=None` in the spec).
- If the preferred port 8517 is occupied, a fallback port is used for that
  session; localStorage is origin-scoped, so settings from the preferred
  port won't be visible until it frees up (tool falls back to defaults).
- Untested on real macOS as of 2026-07-17 — container verification covers
  parsing, logic, and server behaviour, not WKWebView or PyInstaller output.
