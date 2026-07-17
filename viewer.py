#!/usr/bin/env python3
"""Colour Mixer — macOS desktop wrapper.

Serves the bundled HTML (with vendored three.min.js) over a loopback-only
HTTP server and displays it in a pywebview (WKWebView) window.

Design notes (suite conventions):
- Fixed preferred port (8517): localStorage is origin-scoped
  (scheme+host+port), so a stable port keeps colourMixerSettings_v1
  persistent across launches. If the port is taken, the next ports in
  PORT_CANDIDATES are tried; a fallback port means a fresh settings
  origin for that session (the tool falls back to defaults silently).
- Host header check: only 127.0.0.1:<port> / localhost:<port> accepted
  (403 otherwise) — DNS-rebinding defence. No CORS headers by design.
- GET/HEAD only. Path traversal handled by SimpleHTTPRequestHandler's
  translate_path plus the directory= pin.
- private_mode=False is REQUIRED: pywebview defaults to private_mode=True,
  which discards localStorage every run (verified against pywebview 6.2.1
  source). storage_path pins WebKit data to Application Support.
- No subprocess, no eval, no external network access at runtime.
"""

import http.server
import os
import socket
import sys
import threading

import webview

APP_NAME = "Colour Mixer"
PORT_CANDIDATES = list(range(8517, 8527))  # 8517 preferred; see note above
INDEX = "index.html"


def resource_dir():
    """Directory holding index.html + three.min.js (frozen or source run)."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.join(base, "build_src")
    return base


def storage_dir():
    path = os.path.join(
        os.path.expanduser("~/Library/Application Support"), "ColourMixer"
    )
    os.makedirs(path, exist_ok=True)
    return path


class Handler(http.server.SimpleHTTPRequestHandler):
    server_port = None  # set after bind

    def _host_ok(self):
        host = self.headers.get("Host", "")
        allowed = {
            f"127.0.0.1:{self.server_port}",
            f"localhost:{self.server_port}",
        }
        return host in allowed

    def do_GET(self):
        if not self._host_ok():
            self.send_error(403, "Forbidden")
            return
        super().do_GET()

    def do_HEAD(self):
        if not self._host_ok():
            self.send_error(403, "Forbidden")
            return
        super().do_HEAD()

    # Everything else (POST etc.) falls through to 501 via the base class.

    def log_message(self, fmt, *args):
        pass  # quiet by default


def start_server(directory):
    last_err = None
    for port in PORT_CANDIDATES:
        try:
            handler = lambda *a, **kw: Handler(*a, directory=directory, **kw)
            httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        except OSError as e:
            last_err = e
            continue
        Handler.server_port = port
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        return httpd, port
    raise RuntimeError(
        f"No free port in {PORT_CANDIDATES[0]}-{PORT_CANDIDATES[-1]}: {last_err}"
    )


def main():
    rdir = resource_dir()
    index_path = os.path.join(rdir, INDEX)
    if not os.path.isfile(index_path):
        raise SystemExit(f"Bundled HTML not found: {index_path}")

    httpd, port = start_server(rdir)
    try:
        webview.create_window(
            APP_NAME,
            url=f"http://127.0.0.1:{port}/{INDEX}",
            width=1280,
            height=840,
            min_size=(900, 640),
        )
        webview.start(
            private_mode=False,          # REQUIRED for localStorage persistence
            storage_path=storage_dir(),
        )
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
