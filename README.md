# MarkItDown GUI

A web-based GUI wrapper for [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

Convert PDF, Word, Excel, PowerPoint, images, audio, and more to Markdown — all in your browser, with no data leaving your machine.

## Features

- Drag & drop file conversion
- Batch convert multiple files
- Live Markdown preview with syntax highlighting
- Download individual `.md` files or a ZIP of all results
- Single executable — no installation needed
- Cross-platform: Windows, macOS, Linux

## Usage

### Run from source

```bash
pip install -e .
python -m markitdown_gui
```

Or use the CLI entry point:

```bash
markitdown-gui
```

### Build standalone executable

```bash
pip install pyinstaller
python scripts/build.py
```

The executable will be in `dist/`.

### Build via GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow that automatically builds standalone executables for **Windows**, **Linux**, and **macOS**.

**To trigger a build:**

1. Go to the repository's **Actions** tab on GitHub.
2. Select the **Build** workflow from the left sidebar.
3. Click the **Run workflow** button (dropdown on the right).
4. Choose the branch (`main`) and click **Run workflow**.

**To download the compiled executables:**

1. Wait for the workflow run to complete (typically 5–10 minutes).
2. Click on the completed workflow run.
3. Scroll down to the **Artifacts** section.
4. Download the artifact for your platform:
   - `markitdown-gui-windows` — contains `markitdown-gui.exe`
   - `markitdown-gui-linux` — contains `markitdown-gui`
   - `markitdown-gui-macos` — contains `markitdown-gui`

> **Note:** The workflow also runs automatically on every push to `main` and on every version tag (`v*`).

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
