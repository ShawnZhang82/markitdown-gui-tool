#!/usr/bin/env python3
"""Build script for MarkItDown GUI using PyInstaller."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_DIR = PROJECT_ROOT / "src" / "markitdown_gui"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# PyInstaller uses different separators on different platforms
SEP = ";" if sys.platform == "win32" else ":"


def find_magika_data() -> list[tuple[str, str]]:
    """Find magika package data directories (models, config, etc.)."""
    try:
        import magika
    except ImportError:
        print("ERROR: magika is not installed. Run: pip install markitdown")
        sys.exit(1)

    magika_dir = Path(magika.__file__).parent
    data_dirs = []

    for subdir in ["models", "config"]:
        src = magika_dir / subdir
        if src.exists():
            data_dirs.append((str(src), f"magika/{subdir}"))

    return data_dirs


def clean():
    """Remove previous build artifacts."""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"Removed {d}")


def build():
    """Run PyInstaller to build the standalone executable."""
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name", "markitdown-gui",
        "--onefile",
        "--noconfirm",
        "--clean",
        # Add static files as data
        "--add-data",
        f"{SRC_DIR / 'static'}{SEP}markitdown_gui/static",
    ]

    # Add magika data files
    for src, dest in find_magika_data():
        cmd.extend(["--add-data", f"{src}{SEP}{dest}"])

    # Hidden imports for markitdown converters
    hidden_imports = [
        "markitdown.converters",
        "markitdown.converters._pdf_converter",
        "markitdown.converters._docx_converter",
        "markitdown.converters._xlsx_converter",
        "markitdown.converters._pptx_converter",
        "markitdown.converters._html_converter",
        "markitdown.converters._plain_text_converter",
        "markitdown.converters._image_converter",
        "markitdown.converters._audio_converter",
        "markitdown.converters._csv_converter",
        "markitdown.converters._epub_converter",
        "markitdown.converters._zip_converter",
        "markitdown.converters._ipynb_converter",
        "markitdown.converters._rss_converter",
        "markitdown.converters._wikipedia_converter",
        "markitdown.converters._youtube_converter",
        "markitdown.converters._bing_serp_converter",
        "markitdown.converters._outlook_msg_converter",
        "markitdown.converters._doc_intel_converter",
        # uvicorn internals
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Entry point
    cmd.append(str(SRC_DIR / "__main__.py"))

    print("Running PyInstaller...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    print(f"\nBuild complete!")
    exe_name = "markitdown-gui.exe" if sys.platform == "win32" else "markitdown-gui"
    print(f"Executable: {DIST_DIR / exe_name}")


if __name__ == "__main__":
    clean()
    build()
