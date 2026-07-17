# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Colour Mixer, macOS arm64 .app
#
# arm64 (Apple Silicon) build.
#
# Build (from the mac/ directory, after prepare_build.py):
#   pyinstaller --noconfirm colourmixer.spec

import os

# SPECPATH is the spec file's directory in current PyInstaller; handle a
# file path too, defensively, so a semantic change fails safe.
_base = SPECPATH if os.path.isdir(SPECPATH) else os.path.dirname(os.path.abspath(SPECPATH))
build_src = os.path.join(_base, "build_src")
assert os.path.isdir(build_src), (
    "build_src missing — run prepare_build.py before pyinstaller"
)

datas = [
    (os.path.join(build_src, "index.html"), "."),
    (os.path.join(build_src, "three.min.js"), "."),
]

a = Analysis(
    ["viewer.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="colourmixer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,               # suite convention: UPX off (AV false positives)
    console=False,
    target_arch="arm64",   # native on macos-15 runners; explicit for clarity
    codesign_identity=None,  # ad-hoc signing; SignPath/Developer ID later
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="colourmixer",
)

app = BUNDLE(
    coll,
    name="Colour Mixer.app",
    icon=None,               # no icon asset exists for this tool yet
    bundle_identifier="com.boristsui.colourmixer",
    info_plist={
        "CFBundleName": "Colour Mixer",
        "CFBundleDisplayName": "Colour Mixer",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSPrincipalClass": "NSApplication",
    },
)
