import tempfile
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import markitdown
from markitdown import MarkItDown, StreamInfo, DocumentConverterResult
from markitdown._exceptions import (
    UnsupportedFormatException,
    FileConversionException,
    MissingDependencyException,
)


@dataclass
class ConversionResult:
    filename: str
    success: bool
    markdown: str = ""
    title: Optional[str] = None
    error: str = ""


class MarkItDownConverter:
    """Wrapper around markitdown.MarkItDown with error handling and batch support."""

    def __init__(self, enable_plugins: bool = False):
        self._md = MarkItDown(enable_plugins=enable_plugins)

    def convert_file(
        self,
        file_path: str,
        filename: str,
        stream_info: Optional[StreamInfo] = None,
    ) -> ConversionResult:
        """Convert a single file to Markdown."""
        try:
            result = self._md.convert_local(file_path, stream_info=stream_info)
            return ConversionResult(
                filename=filename,
                success=True,
                markdown=result.markdown,
                title=result.title,
            )
        except UnsupportedFormatException as e:
            return ConversionResult(
                filename=filename,
                success=False,
                error=f"Unsupported file format: {e}",
            )
        except FileConversionException as e:
            # Try to provide a helpful error message
            error_msg = str(e)
            if e.attempts:
                for attempt in e.attempts:
                    if attempt.exc_info:
                        exc_type, exc_value, _ = attempt.exc_info
                        if exc_type is MissingDependencyException:
                            error_msg = (
                                f"Missing dependency for {filename}. "
                                f"Install with: pip install markitdown[all]"
                            )
                            break
            return ConversionResult(
                filename=filename,
                success=False,
                error=error_msg,
            )
        except Exception as e:
            return ConversionResult(
                filename=filename,
                success=False,
                error=f"Conversion failed: {e}",
            )

    def convert_stream(
        self,
        file_stream,
        filename: str,
        stream_info: Optional[StreamInfo] = None,
    ) -> ConversionResult:
        """Convert a file stream to Markdown."""
        try:
            result = self._md.convert_stream(file_stream, stream_info=stream_info)
            return ConversionResult(
                filename=filename,
                success=True,
                markdown=result.markdown,
                title=result.title,
            )
        except UnsupportedFormatException as e:
            return ConversionResult(
                filename=filename,
                success=False,
                error=f"Unsupported file format: {e}",
            )
        except FileConversionException as e:
            error_msg = str(e)
            if e.attempts:
                for attempt in e.attempts:
                    if attempt.exc_info:
                        exc_type, exc_value, _ = attempt.exc_info
                        if exc_type is MissingDependencyException:
                            error_msg = (
                                f"Missing dependency for {filename}. "
                                f"Install with: pip install markitdown[all]"
                            )
                            break
            return ConversionResult(
                filename=filename,
                success=False,
                error=error_msg,
            )
        except Exception as e:
            return ConversionResult(
                filename=filename,
                success=False,
                error=f"Conversion failed: {e}",
            )

    def convert_batch(
        self,
        files: List[Dict[str, Any]],
    ) -> List[ConversionResult]:
        """Convert multiple files sequentially.

        files: list of dicts with keys 'path', 'filename', optionally 'stream_info'
        """
        results: List[ConversionResult] = []
        for f in files:
            result = self.convert_file(
                file_path=f["path"],
                filename=f["filename"],
                stream_info=f.get("stream_info"),
            )
            results.append(result)
        return results
