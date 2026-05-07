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

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
