import os
import tempfile
import zipfile
import io
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from markitdown import StreamInfo

from .converter import MarkItDownConverter, ConversionResult

app = FastAPI(title="MarkItDown GUI", version="0.1.0")

# Initialize converter
_converter = MarkItDownConverter(enable_plugins=False)

# Mount static files (frontend)
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
):
    """Convert a single uploaded file to Markdown."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(file.filename).suffix or ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        stream_info = StreamInfo(
            filename=file.filename,
            extension=suffix,
        )
        result = _converter.convert_file(tmp_path, file.filename, stream_info=stream_info)
    finally:
        os.unlink(tmp_path)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)

    return {
        "filename": result.filename,
        "markdown": result.markdown,
        "title": result.title,
    }


@app.post("/api/convert-batch")
async def convert_batch(
    files: List[UploadFile] = File(...),
):
    """Convert multiple uploaded files to Markdown."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results: List[ConversionResult] = []
    temp_paths: List[str] = []

    try:
        # Save all uploads to temp files
        file_infos = []
        for upload in files:
            if not upload.filename:
                continue
            suffix = Path(upload.filename).suffix or ""
            content = await upload.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
                temp_paths.append(tmp_path)
                file_infos.append({
                    "path": tmp_path,
                    "filename": upload.filename,
                    "stream_info": StreamInfo(
                        filename=upload.filename,
                        extension=suffix,
                    ),
                })

        # Convert sequentially
        for info in file_infos:
            result = _converter.convert_file(
                info["path"],
                info["filename"],
                stream_info=info["stream_info"],
            )
            results.append(result)

    finally:
        for p in temp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass

    return {
        "results": [
            {
                "filename": r.filename,
                "success": r.success,
                "markdown": r.markdown,
                "title": r.title,
                "error": r.error,
            }
            for r in results
        ]
    }


@app.get("/api/download")
async def download_result(
    filename: str,
    markdown: str,
):
    """Download a single converted markdown file."""
    if not filename or not markdown:
        raise HTTPException(status_code=400, detail="Filename and markdown content required")

    base_name = Path(filename).stem
    md_filename = f"{base_name}.md"

    return StreamingResponse(
        io.BytesIO(markdown.encode("utf-8")),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{md_filename}"'},
    )


@app.post("/api/download-zip")
async def download_zip(
    data: dict,
):
    """Download all results as a ZIP file."""
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=400, detail="No results provided")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        seen_names = set()
        for item in results:
            if not item.get("success"):
                continue
            base_name = Path(item["filename"]).stem
            md_name = f"{base_name}.md"
            # Handle duplicate names
            counter = 1
            original_name = md_name
            while md_name in seen_names:
                md_name = f"{base_name}_{counter}.md"
                counter += 1
            seen_names.add(md_name)
            zf.writestr(md_name, item.get("markdown", "").encode("utf-8"))

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="markitdown_results.zip"'},
    )


@app.get("/")
async def root():
    """Serve the main HTML page."""
    index_file = _static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend not built")
